import docx

def extract_text_from_docx(docx_file):
    """
    Extracts text from a DOCX file (supports both file path strings and file-like objects).
    """
    try:
        # docx.Document accepts both paths and file-like objects
        doc = docx.Document(docx_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        print(f"Error reading docx: {e}")
        return ""
