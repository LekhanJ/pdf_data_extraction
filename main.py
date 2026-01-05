import logging
import json
import argparse
import shutil
from pathlib import Path
from pdf2image import pdfinfo_from_path

from config import Config
from image_converter import ImageConverter
from gemini_client import GeminiClient
from validator import Validator

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("extraction.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Change the get_total_pages function:
def get_total_pages(pdf_path: str) -> int:
    try:
        # Pass poppler_path here too
        info = pdfinfo_from_path(pdf_path, poppler_path=Config.POPPLER_PATH) 
        return info["Pages"]
    except Exception as e:
        logger.error(f"Could not read PDF info: {e}")
        raise

def main(pdf_path: str):
    logger.info(f"Starting extraction for: {pdf_path}")
    
    # 1. Initialization
    converter = ImageConverter()
    client = GeminiClient()
    validator = Validator()
    all_voter_data = []

    # 2. Determine Page Range
    total_pages = get_total_pages(pdf_path)
    limit = Config.TOTAL_PAGES_TO_PROCESS if Config.TOTAL_PAGES_TO_PROCESS else total_pages
    logger.info(f"Total Pages: {total_pages}. Processing: {limit}")

    # 3. Batch Processing Loop
    # We iterate by Chunk Size (e.g., 2 pages at a time)
    for start_page in range(1, limit + 1, Config.CHUNK_SIZE):
        end_page = min(start_page + Config.CHUNK_SIZE - 1, limit)
        
        chunk_header = f"Processing Chunk: Pages {start_page}-{end_page}"
        logger.info("-" * len(chunk_header))
        logger.info(chunk_header)

        img_paths = []
        try:
            # A. Convert PDF Chunk to Images
            img_paths = converter.convert_pdf_chunk(pdf_path, start_page, end_page)

            # B. Send to Gemini Vision
            batch_raw_data = client.process_image_batch(img_paths)

            # C. Validate Data
            valid_data = validator.validate_batch(batch_raw_data)
            
            # D. Merge
            all_voter_data.extend(valid_data)
            logger.info(f"Chunk success. Added {len(valid_data)} records. Total: {len(all_voter_data)}")

        except Exception as e:
            logger.error(f"Critical failure in chunk {start_page}-{end_page}: {e}")
            # In production, we might log failed page numbers to a 'failed_jobs.json'
            # to retry later, but we continue to next chunk here.
            continue
        
        finally:
            # E. Cleanup Local Temp Images
            for p in img_paths:
                if p.exists():
                    p.unlink()

    # 4. Final Output Export
    output_file = Config.OUTPUT_DIR / "final_voter_data.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_voter_data, f, ensure_ascii=False, indent=2)

    logger.info(f"✅ Extraction Complete. Data saved to {output_file}")
    logger.info(f"Total Records Extracted: {len(all_voter_data)}")

    # Cleanup temp dir
    shutil.rmtree(Config.TEMP_DIR)
    Config.TEMP_DIR.mkdir()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gemini Vision PDF Extractor")
    parser.add_argument("pdf_path", type=str, help="Path to the scanned PDF file")
    args = parser.parse_args()
    
    if not Path(args.pdf_path).exists():
        print(f"Error: File {args.pdf_path} not found.")
        exit(1)
        
    main(args.pdf_path)