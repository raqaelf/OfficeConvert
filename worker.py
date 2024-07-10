# worker.py

from celery import Celery
import os
import base64
from dotenv import load_dotenv
from convert import convert_docx_to_pdf

# Load environment variables from .env file
load_dotenv()

app = Celery('tasks', broker=os.getenv('REDIS_URL'))

@app.task
def convert_task(docx_path):
    try:
        pdf_path = convert_docx_to_pdf(docx_path)  # Call your conversion function
        with open(pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')

        # Clean up files after conversion
        os.remove(docx_path)
        os.remove(pdf_path)

        return {'pdf_base64': pdf_base64}

    except Exception as e:
        raise Exception(f"Conversion error: {str(e)}")
