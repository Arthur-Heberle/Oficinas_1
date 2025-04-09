'''
========== IDEIAS CHATGPT =========

1. Leitura e Interpretação do arquivo:

    # Para .txt
    with open("arquivo.txt", "r") as file:
        texto = file.read()

    # Para .pdf com PyPDF2
    import PyPDF2 #tem também PyMuPDF, mas dai são outras funções acho
    with open("arquivo.pdf", "rb") as file:
        reader = PyPDF2.PdfReader(file)
        texto = ''
        for page in reader.pages:
            texto += page.extract_text()

    # Para .docx com python-docx
    from docx import Document
    doc = Document("arquivo.docx")
    texto = "\n".join([paragrafo.text for paragrafo in doc.paragraphs])

2. Envio para a Raspberry Pi via Wi-Fi:

    import requests

    # Supondo que você tenha o texto extraído
    texto_extraido = "Aqui está o texto extraído do arquivo"

    # URL do servidor da Raspberry Pi
    url = "http://<IP_da_Raspberry_Pi>:5000/receber_dados"

    # Enviando via POST
    response = requests.post(url, json={"texto": texto_extraido})

    if response.status_code == 200:
        print("Dados enviados com sucesso!")
    else:
        print("Falha ao enviar dados.")
    ------------------------------------------------
    from flask import Flask, request

    app = Flask(__name__)

    @app.route('/receber_dados', methods=['POST'])
    def receber_dados():
        dados = request.json
        texto_recebido = dados.get('texto')
        # Aqui você pode processar o texto recebido
        print(f"Texto recebido: {texto_recebido}")
        return {"status": "sucesso"}, 200

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)  # Isso faz o Flask rodar na Raspberry Pi

3.Configuração do Wi-Fi na Raspberry Pi:

    network={
        ssid="NOME_DA_REDE"
        psk="SENHA"
    }



'''