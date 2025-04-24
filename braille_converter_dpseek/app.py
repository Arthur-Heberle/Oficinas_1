from flask import Flask, render_template, request
import os
import requests
from docx import Document
import PyPDF2
import textract

app = Flask(__name__)
app.secret_key = "your_secret_key"

'''Important Notes:

Replace PI_IP in app.py with your Pi's actual IP

Ensure both devices are on the same network

Create the uploads directory before first run

PDF text extraction quality depends on the PDF structure

Add your Braille display logic in pi_receiver.py

This provides a complete end-to-end system for document-to-Braille conversion with network communication between the web interface and Raspberry Pi.'''


# Configure your Pi's IP and port
PI_IP = "192.168.1.100"
PI_PORT = "5000"
PI_ENDPOINT = f"http://{PI_IP}:{PI_PORT}/receive-text"

def extract_text_from_file(file_path, extension):
    if extension == 'txt':
        with open(file_path, 'r') as f:
            return f.read()
    elif extension == 'docx':
        doc = Document(file_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    elif extension == 'pdf':
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = '\n'.join([page.extract_text() for page in reader.pages])
            return text
    return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', message="No file selected")
    
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', message="No file selected")

    allowed_extensions = {'txt', 'docx', 'pdf'}
    extension = file.filename.split('.')[-1].lower()
    
    if extension not in allowed_extensions:
        return render_template('index.html', message="Invalid file type")

    try:
        # Save temporarily
        os.makedirs('uploads', exist_ok=True)
        temp_path = os.path.join('uploads', file.filename)
        file.save(temp_path)
        
        # Extract text
        text = extract_text_from_file(temp_path, extension)
        os.remove(temp_path)

        # Send to Pi
        response = requests.post(PI_ENDPOINT, data=text.encode('utf-8'))
        
        if response.status_code == 200:
            return render_template('index.html', message="Text sent to Raspberry Pi successfully!")
        else:
            return render_template('index.html', message="Error sending to Raspberry Pi")

    except Exception as e:
        return render_template('index.html', message=f"Error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)