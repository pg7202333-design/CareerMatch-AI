import fitz

def extract_pdf_text(uploaded_file) -> str:
    """Extract selectable text from an uploaded PDF."""
    pdf_bytes = uploaded_file.read()
    document = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = [page.get_text("text") for page in document]
    document.close()
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No selectable text was found in the PDF.")
    return text
