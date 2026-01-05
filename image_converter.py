import logging
from pdf2image import convert_from_path
from pathlib import Path
from typing import List
from config import Config

logger = logging.getLogger(__name__)

class ImageConverter:
    @staticmethod
    def convert_pdf_chunk(pdf_path: str, start_page: int, end_page: int) -> List[Path]:
        """
        Converts a specific range of PDF pages to High-Res PNGs.
        Uses poppler (pdftoppm) backend.
        """
        logger.info(f"Converting PDF pages {start_page} to {end_page}...")
        
        try:
            # pdf2image uses 1-based indexing for first_page/last_page
            # Change the convert_from_path call:
            images = convert_from_path(
                pdf_path,
                dpi=Config.DPI,
                first_page=start_page,
                last_page=end_page,
                fmt="png",
                poppler_path=Config.POPPLER_PATH  # <--- ADD THIS
            )
            
            saved_paths = []
            for i, image in enumerate(images):
                page_num = start_page + i
                filename = Config.TEMP_DIR / f"page_{page_num:04d}.png"
                image.save(filename, "PNG")
                saved_paths.append(filename)
                
            return saved_paths

        except Exception as e:
            logger.error(f"Failed to convert pages {start_page}-{end_page}: {str(e)}")
            raise