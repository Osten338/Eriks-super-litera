import os
from typing import Optional

import pytesseract
from PIL import Image


def set_tesseract_cmd_from_env() -> None:
    cmd = os.getenv("TESSERACT_CMD")
    if cmd:
        pytesseract.pytesseract.tesseract_cmd = cmd


def ocr_image(image: Image.Image, lang: str = "eng") -> str:
    set_tesseract_cmd_from_env()
    return pytesseract.image_to_string(image, lang=lang)


