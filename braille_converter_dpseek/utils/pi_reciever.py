from flask import Flask, request

app = Flask(__name__)

@app.route('/receive-text', methods=['POST'])
def receive_text():
    text = request.data.decode('utf-8')
    # Add your Braille hardware control here
    print(f"Received text: {text}")
    return "Text received", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)