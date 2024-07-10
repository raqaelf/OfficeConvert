# your_application.py

import os
import win32com.client
import pythoncom
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def convert_docx_to_pdf(docx_path):
    try:
        pythoncom.CoInitialize()
        word = win32com.client.Dispatch('Word.Application')
        
        pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
        
        doc = word.Documents.Open(os.path.abspath(docx_path))
        doc.SaveAs(os.path.abspath(pdf_path), FileFormat=17)
        doc.Close()
        
        word.Quit()
        pythoncom.CoUninitialize()

        return pdf_path

    except Exception as e:
        raise Exception(f"Error converting document: {str(e)}")
