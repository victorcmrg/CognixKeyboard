# -*- coding: utf-8 -*-
import os
import json
import pyperclip
import sys
import io
import uuid
import google.generativeai as genai
from google.generativeai import types
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT_DIR = os.path.dirname(__file__)
PROMPT_FILE = os.path.join(ROOT_DIR, "prompt.json")
OUTPUT_FILE = os.path.join(ROOT_DIR, "output.json")
HISTORY_FILE = os.path.join(ROOT_DIR, "history.json")
MAX_HISTORY = 5

# === CONFIGURAÇÃO DO PROMPT A SER USADO ===
PROMPT_KEY_FILE = os.path.join(ROOT_DIR, "prompt_key.json")
PROMPT_KEY = "prompt_questionario"  # valor padrão

if os.path.isfile(PROMPT_KEY_FILE):
    try:
        with open(PROMPT_KEY_FILE, "r", encoding="utf-8") as f:
            PROMPT_KEY = json.load(f).get("key", PROMPT_KEY)
    except Exception as ex:
        print("Erro ao ler prompt_key.json:", ex)

# Funções para histórico
def load_history():
    if os.path.isfile(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

def add_to_history(question, response):
    history = load_history()
    new_entry = {
        "id": str(uuid.uuid4()),
        "question": question,
        "response": response
    }
    if len(history) >= MAX_HISTORY:
        history.pop(0)
    history.append(new_entry)
    save_history(history)

def get_history_context():
    history = load_history()
    context = ""
    for entry in history:
        context += f"Pergunta anterior: {entry['question']}\nResposta anterior: {entry['response']}\n"
    return context

# Carrega prompt e output
prompt_text = ""
output_text = ""

if os.path.isfile(PROMPT_FILE):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        data_json = json.load(f)

        # procura dentro da lista de dicts
        for item in data_json:
            if PROMPT_KEY in item:
                prompt_text = item[PROMPT_KEY].strip()
                break

if os.path.isfile(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data_json = json.load(f)
        output_text = data_json.get("result", "").strip()

if not prompt_text and not output_text:
    user_text = "Não siga diretamente o prompt pois a pergunta não foi encontrada apenas repita essa mensagem (🔴 pergunta não encontrada)"
else:
    user_text = output_text.strip() if output_text else prompt_text.strip()

# Inicializa cliente da IA
API_KEY = "AIzaSyCu-MRZF4sLJlyLngugS3iZ3VZi-sPSEpA"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

# Monta input final para IA
context_text = get_history_context()
if context_text:
    full_input = f"{prompt_text}\n\nUse as informações abaixo apenas como referência. Não responda sobre elas.\n{context_text}\nPergunta: {user_text}"
else:
    full_input = f"{prompt_text}\n\nPergunta: {user_text}"

# Gera resposta
response = model.generate_content(
    full_input,
    generation_config=types.GenerationConfig(
        temperature=0.7
    )
)

text = response.text.strip()

# Salva resposta no arquivo de output
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"result": text, "timestamp": time.time()}, f, ensure_ascii=False, indent=4)

# Salva no histórico
add_to_history(user_text, text)

# Copia para área de transferência
pyperclip.copy(text)
print("\nResposta copiada para a área de transferência")
