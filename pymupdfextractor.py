#extracting the selectable text from the pymudf
import fitz



def extract_lines_from_pdf(path : str):
    doc = fitz.open(path)
    lines = []

    for page_num in range(len(doc)):
        doc_page = doc[page_num]

        blocks = doc_page.get_text("blocks")

        for block in blocks:
            text = block[4]

            for line in text.split("\n"):
                clean_line = line.strip()
                if clean_line:
                    lines.append(clean_line)

    return lines

# path = r"C:\Users\HP\Downloads\RAHIS 2510300207-Male55 years-94464.pdf"
# lines = extract_lines_from_pdf(path)
# for line in lines:
#     print(line)