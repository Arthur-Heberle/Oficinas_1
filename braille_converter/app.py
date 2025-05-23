'''======================================================================='''
#  
#   Project: Edubra - Educador de Braille
# 
#   This file is responsible to create the back-end to the website.
#   It can recieve a (.pdf, .docx, .txt) file and send it's text  
#   to the Raspberry Pi 4 via Wi-fi.
#
#   Autor: Arthur Gabriel P. Heberle
#   Email: a.gp.heberle@gmail.com
#
'''-----------------------------------------------------------------------'''


from flask import Flask, render_template, request
import os
import requests
from gtts import gTTS
from docx import Document
import PyPDF2
app = Flask(__name__)
app.secret_key = "Heberle2023"

'''
Important Notes:

Replace PI_IP in app.py with your Pi's actual IP

Ensure both devices are on the same network

Create the uploads directory before first run

PDF text extraction quality depends on the PDF structure

'''

# Configure your Pi's IP and port
# PI_IP = "192.168.43.170" #Rafael
PI_IP = "192.168.150.221"

# PI_IP = "10.5.0.44"
PI_PORT = "5000"
PI_ENDPOINT = f"http://{PI_IP}:{PI_PORT}/"
PI_ROUTE_TEXT = "receive-text"
PI_ROUTE_RUN = "run-text"

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
            text = ''.join([page.extract_text() for page in reader.pages])
            tmp = ''
            for word in text.split('\n'):
                tmp += word
            text = tmp            
            return text
    return ""

def create_txt_file(file_path, text, folder):
    try:
        path = f"{folder}/{file_path}"
        file = open(path, "x")

        for letter in text:
            file.write(letter)
            
        file.close()
        print(f"File '{file_path}' created successfully.")
    except FileExistsError:
        print(f"File '{file_path}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_words(text):
    lines = text.split('\n')
    i =0 
    aux = []
    for line in lines:
        aux.append(line.split(' '))
        i+=1
    words = []
    for i in aux:
        for j in i:
            words.append(j)
    return words    

def create_text_audio(text):
    try:
        tts = gTTS(text=text, lang="pt")
        tts.save("static/outputTEXT.mp3")
    except  Exception as e:
        print(f'Error when trying to create text audio: \n {str(e)}')

def destoy_text_audio():
    try:
        os.remove("static/outputTEXT.mp3")
    except Exception as e:
        print(f'Error when trying to destroy text audio: \n {str(e)}')

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

        text = text.lower()
        words = get_words(text)
        create_text_audio(text)
        
        new_file = 'my_' + temp_path[8:].split('.')[0] + '.txt'
        
        os.remove(temp_path)

        create_txt_file(new_file, text, "files")
        

        # Send to Pi
    
        response = requests.post(PI_ENDPOINT+PI_ROUTE_TEXT, json={'text': text, 'words': words})

        if response.status_code == 200:
            return render_template('index.html', message="Text sent to Raspberry Pi successfully!")
        else:
            return render_template('index.html', message="Error sending to Raspberry Pi")
        
    except Exception as e:
        return render_template('index.html', message=f"Error: {str(e)}")

@app.route('/run', methods=['POST'])
def run_text():
    try:
        time_str = request.form.get('quantity', '0.5')
        try:
            time = float(time_str)
        except ValueError:
            return render_template('index.html', message2="Invalid time value.")
        
        response = requests.post(PI_ENDPOINT+PI_ROUTE_RUN, json= {'time': time})

        if response.status_code == 200:
            return render_template('index.html', message2="Text Runned!")
        else:
            return render_template('index.html', message2="Error sending to Raspberry Pi")
        
    except Exception as e:
        return render_template('index.html', message2=f"Error: {str(e)}")
    finally:
        destoy_text_audio()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
