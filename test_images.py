import argparse
import shutil
from pathlib import Path
from pdf2image import convert_from_path

# Import your existing config to ensure we test the EXACT settings you are using
try:
    from config import Config
    # If you added POPPLER_PATH to config.py, we use it. If not, it stays None.
    POPPLER_PATH = getattr(Config, "POPPLER_PATH", None) 
    DPI = getattr(Config, "DPI", 300)
except ImportError:
    # Fallback if config.py isn't found
    POPPLER_PATH = r"C:\lekhan\pdf_extractor\poppler\Library\bin" # Adjust if needed
    DPI = 300

def test_image_generation(pdf_path):
    # 1. Setup Output Directory
    output_dir = Path("debug_images")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    print(f"🔍 Testing PDF: {pdf_path}")
    print(f"⚙️  Settings: DPI={DPI}, Poppler={POPPLER_PATH}")
    print("⏳ Converting first 2 pages... (this might take a few seconds)")

    try:
        # 2. Run Conversion
        images = convert_from_path(
            pdf_path,
            dpi=DPI,              # Uses the DPI from your config
            first_page=1,         # Only page 1
            last_page=2,          # To page 2
            fmt="png",
            poppler_path=POPPLER_PATH
        )

        # 3. Save Images
        if not images:
            print("❌ No images were generated!")
            return

        for i, image in enumerate(images):
            file_path = output_dir / f"debug_page_{i+1}.png"
            image.save(file_path, "PNG")
            print(f"✅ Saved Image: {file_path}")
            print(f"   Resolution: {image.width}x{image.height} pixels")

        print("\n🎉 SUCCESS!")
        print(f"👉 Open this folder to check quality: {output_dir.absolute()}")
        print("💡 Check: Is the text blurry? Can you read the names clearly?")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        if "poppler" in str(e).lower():
            print("💡 TIP: This is definitely a Poppler path issue.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test PDF to Image Conversion")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file")
    args = parser.parse_args()
    
    if not Path(args.pdf_path).exists():
        print(f"Error: File {args.pdf_path} not found.")
    else:
        test_image_generation(args.pdf_path)