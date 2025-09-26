import requests
import json
import os

# Caminho do output.json gerado pelo hotkey_runner.py
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "output.json")

# Lê o conteúdo de output.json
if os.path.isfile(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            data_json = json.load(f)
            user_text = data_json.get("result", "")
            if not user_text.strip():
                user_text = "Digite algo sobre IA em RaspberryPI"  # fallback caso esteja vazio
    except Exception as e:
        print("Erro ao ler output.json:", e)
        user_text = "Digite algo sobre IA em RaspberryPI"
else:
    print("output.json não encontrado, usando texto padrão.")
    user_text = "Digite algo sobre IA em RaspberryPI"

# Dados da requisição
url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer (TOKEN AQUI)",
    "Content-Type": "application/json",
}

payload = {
    "model": "(MODELO AQUI)",
    "messages": [
        {
            "role": "user",
            "content": [
                { "type": "text", "text": user_text },
                # Se quiser enviar imagem, descomente abaixo e adicione URL
                # {
                #     "type": "image_url",
                #     "image_url": {"url": "URL_DA_IMAGEM_AQUI"}
                # }
            ]
        }
    ]
}

# Enviar requisição
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Processar resposta
if response.status_code == 200:
    try:
        data = response.json()
        # Tenta pegar a primeira escolha
        choice = data.get('choices', [{}])[0]
        message = choice.get('message', {})
        content = message.get('content')
        if isinstance(content, list) and len(content) > 0:
            text = content[0].get('text', '')
        elif isinstance(content, str):
            text = content
        else:
            text = str(content)

        print("Resposta do modelo:\n")
        print(text)
    except Exception as e:
        print("Erro ao processar resposta:", e)
        print("Resposta completa:", response.text)
else:
    print("Erro na requisição:", response.status_code)
    print(response.text)
