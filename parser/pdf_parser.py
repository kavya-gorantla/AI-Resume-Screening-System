import pdfplumber
import PyPDF2

def extract_text_from_pdf(pdf_file):
    """
    Extracts text from a PDF file (supports both file path strings and file-like objects).
    """
    text = ""
    try:
        # pdfplumber accepts both paths and file-like objects
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed: {e}. Trying PyPDF2...")
        try:
            if isinstance(pdf_file, str):
                with open(pdf_file, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            else:
                # Reset stream pointer just in case it was read
                if hasattr(pdf_file, 'seek'):
                    pdf_file.seek(0)
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e2:
            print(f"PyPDF2 also failed: {e2}")
    
    return text
