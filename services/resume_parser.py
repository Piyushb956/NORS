import fitz

def extract_resume_text(pdf_path):

    text = ""

    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()

    return text