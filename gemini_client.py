import google.generativeai as genai
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from config import Config
from prompts import get_system_prompt

logger = logging.getLogger(__name__)

# Configure Global API
genai.configure(api_key=Config.GOOGLE_API_KEY)

class GeminiClient:
    def __init__(self):
        self.model = genai.GenerativeModel(
            model_name=Config.MODEL_NAME,
            system_instruction=get_system_prompt(),
            generation_config={
                "temperature": Config.TEMPERATURE,
                "response_mime_type": "application/json"
            }
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def process_image_batch(self, image_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Uploads images to Gemini and requests extraction.
        Retries on transient failures.
        """
        uploaded_files = []
        try:
            # 1. Upload files to Gemini File API (required for large images/multiple images)
            prompt_parts = ["Analyze these voter list pages and extract data according to the rules."]
            
            for img_path in image_paths:
                logger.debug(f"Uploading {img_path.name} to Gemini...")
                # Uploading using the File API is more robust for high-res images
                sample_file = genai.upload_file(path=img_path, display_name=img_path.name)
                uploaded_files.append(sample_file)
                prompt_parts.append(sample_file)

            # 2. Wait for files to be active (usually instant for images, but safe practice)
            # In a production loop, we might check state, but for images strict processing usually works.

            # 3. Generate Content
            logger.info(f"Sending batch of {len(image_paths)} pages to Gemini Vision...")
            response = self.model.generate_content(prompt_parts)
            
            # 4. Parse Response
            raw_text = response.text
            
            # Clean potential markdown fences if model ignores MIME type enforcement
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
                
            data = json.loads(raw_text)
            
            if not isinstance(data, list):
                # Handle edge case where model returns a dict instead of list
                if isinstance(data, dict) and "voters" in data:
                    data = data["voters"]
                else:
                    data = [data]

            logger.info(f"Extracted {len(data)} records from batch.")
            return data

        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e}")
            logger.debug(f"Raw Response: {response.text}")
            raise
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            raise
        finally:
            # 5. Cleanup: Delete files from Gemini Cloud to respect limits
            for f in uploaded_files:
                try:
                    genai.delete_file(f.name)
                except Exception:
                    pass