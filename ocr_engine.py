import io
import fitz  # PyMuPDF
import numpy as np
from PIL import Image
from paddleocr import PaddleOCR

# Initialize OCR once (global, heavy object)
ocr = PaddleOCR(use_angle_cls=True, lang="en")


def extract_text_from_pdf(pdf_path: str) -> str:
    lines = []

    # Use context manager to avoid file lock on Windows
    with fitz.open(pdf_path) as doc:
        for page in doc:
            # Render page to image
            pix = page.get_pixmap(dpi=300)
            img_bytes = pix.tobytes("png")

            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")

            # Convert to numpy array for PaddleOCR
            img_np = np.array(image)

            # Run OCR
            result = ocr.ocr(img_np)

            # Safety check
            if not result:
                continue

            for block in result:
                for line in block:
                    text = line[1][0].strip()
                    if text:
                        lines.append(text)

    return "\n".join(lines)
