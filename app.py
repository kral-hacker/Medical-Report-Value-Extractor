from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

from pymupdfextractor import extract_lines_from_pdf
from ocr_engine import extract_text_from_pdf
from openai_extractor import extract_lab_report_with_openai

app = FastAPI(title="Medical Report OCR API")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # remember to add the domain in the future
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "Medical OCR API"}


@app.post("/extract-report")
async def extract_report(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        # Save uploaded PDF temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # OCR
        lines = extract_lines_from_pdf(tmp_path)
        raw_text = "\n".join(lines)

        # OpenAI extraction
        structured_data = extract_lab_report_with_openai(raw_text)

        return {
            "success": True,
            "filename": file.filename,
            "data": structured_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
