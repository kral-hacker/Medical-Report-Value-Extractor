import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a medical lab report extraction system.

CRITICAL RULES:

1. Some headings are PANEL NAMES (for example: "Differential Leukocyte Count (DLC)", "Liver Function Test", "Lipid Profile").
   These are NOT individual lab tests.

2. NEVER include panel names as tests.

3. Only include rows that have:
   - a biological analyte name (e.g., Neutrophils, Glucose, HbA1c)
   - a numeric value
   - optionally a unit and reference range.

4. Ignore:
   - section titles
   - panel names
   - page numbers
   - method lines (e.g., "Method: Microscopy")
   - interpretations
   - footnotes
   - references

5. Return ONLY valid JSON.
6. If a field is missing, use empty string.
7. If the patient name line contains a long number (8–12 digits), extract it as kmed_id.
    Example:
    "MS. PRIYANKA 2504280203"
    → name = "MS. PRIYANKA"
    → kmed_id = "2504280203"
"""

def extract_lab_report_with_openai(text: str) -> dict:

    user_prompt = f"""
Return JSON in this format:

{{
  "patient": {{
    "name": "",
    "kmed_id": "",
    "age": "",
    "gender": "",
    "patient_id": "",
    "report_id": "",
    "collection_date": "",
    "report_date": ""
  }},
  "tests": [
    {{
      "name": "",
      "value": "",
      "unit": "",
      "reference_range": ""
    }}
  ]
}}

OCR TEXT:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        raise ValueError("OpenAI returned invalid JSON")
