# -*- coding: utf-8 -*-
import os
import json
import pyperclip
import sys
import io
import uuid
import time
from PIL import ImageGrab
import google.generativeai as genai
import mimetypes

# === Configuração de saída UTF-8 ===
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# === Caminhos ===
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(ROOT_DIR, "prompt", "imagem")
PROMPT_FILE = os.path.join(ROOT_DIR, "prompt/prompt.json")
OUTPUT_FILE = os.path.join(ROOT_DIR, "output.json")
HISTORY_FILE = os.path.join(ROOT_DIR, "history.json")
MAX_HISTORY = 15

os.makedirs(IMAGE_DIR, exist_ok=True)

# === Inicializa Gemini ===
API_KEY = 'AIzaSyDSZsRE7SacHoVc6FsyUwyy0uJlrc3A6KI'
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-pro")

# === Funções de histórico ===
def load_history():
    if os.path.isfile(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"🔴 Erro ao salvar history.json: {e}")

def add_to_history(question, response):
    history = load_history()
    new_entry = {
        "id": str(uuid.uuid4()),
        "question": question,
        "response": response,
        "timestamp": time.time()
    }
    if len(history) >= MAX_HISTORY:
        history.pop(0)
    history.append(new_entry)
    save_history(history)

def get_history_context():
    history = load_history()
    if not history:
        return ""
    ctx = ""
    for entry in history:
        q = entry.get("question", "")
        r = entry.get("response", "")
        ctx += f"Pergunta anterior: {q}\nResposta anterior: {r}\n"
    return ctx

# === Lê o prompt base (prompt.json) ===
prompt_text = ""
if os.path.isfile(PROMPT_FILE):
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "prompt" in data:
                prompt_text = data["prompt"].strip()
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "prompt" in item:
                        prompt_text = str(item["prompt"]).strip()
                        break
    except Exception as e:
        print(f"🔴 Erro ao ler prompt.json: {e}")

if not prompt_text:
    prompt_text = ""  # continuará, mas avisaremos se necessário

# === Função: salva imagem do clipboard (se houver) ===
def salvar_imagem_clipboard():
    img = ImageGrab.grabclipboard()
    if img is not None:
        filename = f"imagem_clipboard_{int(time.time())}.png"
        filepath = os.path.join(IMAGE_DIR, filename)
        try:
            img.save(filepath, "PNG")
            return filepath
        except Exception as e:
            print(f"🔴 Erro ao salvar imagem do clipboard: {e}")
    return None

# === Execução principal ===
def main():
    # primeiro tenta salvar uma imagem do clipboard (se houver)
    saved_path = salvar_imagem_clipboard()

    # lista de imagens já presente na pasta
    image_files = [
        os.path.join(IMAGE_DIR, f)
        for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp"))
    ]

    # obtém texto do clipboard (pode ser vazio)
    clipboard_text = pyperclip.paste()
    clipboard_text = clipboard_text.strip() if isinstance(clipboard_text, str) else ""

    # compõe a pergunta que será registrada no histórico
    if image_files:
        question_repr = "Imagem(s): " + ", ".join(os.path.basename(p) for p in image_files)
    elif clipboard_text:
        question_repr = clipboard_text
    else:
        question_repr = "(nenhuma pergunta detectada)"

    # monta contexto do histórico
    history_ctx = get_history_context()
    if history_ctx:
        full_input_text = f"{prompt_text}\n\nUse as informações abaixo apenas como referência. Não responda sobre elas.\n{history_ctx}\nPergunta: {question_repr if not clipboard_text else clipboard_text}"
    else:
        # se houver texto no clipboard, priorizamos ele como pergunta; se não, usamos prompt_text como fallback
        if clipboard_text:
            full_input_text = f"{prompt_text}\n\nPergunta: {clipboard_text}"
        else:
            full_input_text = f"{prompt_text}\n\nPergunta: {question_repr}"

    # gera resposta enviando imagens (se houver) ou apenas texto
    try:
        if image_files:
            print(f"🟡 Imagem(s) detectada(s): {', '.join(os.path.basename(p) for p in image_files)}")
            image_parts = []
            for path in image_files:
                try:
                    mime, _ = mimetypes.guess_type(path)
                    mime = mime or "image/png"
                    with open(path, "rb") as f:
                        data = f.read()
                    image_parts.append({"mime_type": mime, "data": data})
                except Exception as e:
                    print(f"🔴 Falha ao ler imagem {path}: {e}")

            # envia texto + imagens
            # nota: estrutura compatível com versões recentes do SDK
            request_parts = [{"text": full_input_text}] + image_parts
            response = model.generate_content(
                [{"role": "user", "parts": request_parts}],
                generation_config=genai.types.GenerationConfig(temperature=0.7)
            )
            result_text = response.text.strip() if hasattr(response, "text") else str(response)

            # salva output e history
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump({"result": result_text, "timestamp": time.time()}, f, ensure_ascii=False, indent=4)

            add_to_history(question_repr, result_text)

            # apaga as imagens após análise
            for p in image_files:
                try:
                    os.remove(p)
                except Exception as e:
                    print(f"⚠️ Não foi possível remover {p}: {e}")

            pyperclip.copy(result_text)
            print("\n🟢 Resposta (imagem) copiada para a área de transferência.")
            print(f"\n{result_text}")

        else:
            # sem imagens: envia o texto (clipboard_text) como pergunta
            if not clipboard_text:
                print("🔴 Nenhum texto ou imagem encontrado na área de transferência.")
                return

            response = model.generate_content(
                full_input_text,
                generation_config=genai.types.GenerationConfig(temperature=0.7)
            )
            result_text = response.text.strip() if hasattr(response, "text") else str(response)

            # salva output e history
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump({"result": result_text, "timestamp": time.time()}, f, ensure_ascii=False, indent=4)

            add_to_history(clipboard_text, result_text)

            pyperclip.copy(result_text)
            print("\n🟢 Resposta (texto) copiada para a área de transferência.")
            print(f"\n{result_text}")

    except Exception as e:
        err_msg = f"🔴 Erro ao gerar/obter resposta: {e}"
        print(err_msg)
        # registra erro no history para rastreio
        add_to_history(question_repr, err_msg)
        # também grava no output.json para consistência
        try:
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump({"result": err_msg, "timestamp": time.time()}, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

if __name__ == "__main__":
    main()
