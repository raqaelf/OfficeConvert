from flask import Flask, request, jsonify
import os
import base64
import uuid
import logging
from dotenv import load_dotenv
from celery import Celery
from worker import convert_task

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'sqla+sqlite:///celerydb.sqlite'
app.config['CELERY_RESULT_BACKEND'] = 'db+sqlite:///results.sqlite'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route('/convert', methods=['POST'])
def handle_conversion_request():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        ext = file.filename.split('.')[-1]
        random_name = str(uuid.uuid4())
        docx_path = os.path.join('uploads', random_name + "." + ext)
        file.save(docx_path)
        
        logging.info("Received file: %s", docx_path)

        # Enqueue the conversion task
        task = convert_task.delay(docx_path)

        return jsonify({'task_id': task.id}), 202

    except Exception as e:
        logging.error("An error occurred during conversion: %s", str(e))
        return jsonify({'error': 'An error occurred during conversion'}), 500

@app.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = convert_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }
        if task.state == 'SUCCESS':
            response['result'] = task.result
    else:
        response = {
            'state': task.state,
            'status': str(task.info)  # this is the exception raised
        }
    return jsonify(response)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    app.run(host='0.0.0.0', port=8080)
