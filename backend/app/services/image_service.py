from PIL import Image
import pytesseract
from backend.app.core.config import TESSERACT_CMD

# Only override the tesseract path if one was set in .env (Windows users
# who don't have it on PATH). On Linux/Mac this stays empty and
# pytesseract just calls the "tesseract" command directly.
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)
