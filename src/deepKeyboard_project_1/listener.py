# listener.py
import os
import threading
import subprocess
import logging
import sys
import time
import json

try:
    import keyboard
except Exception as e:
    print("Módulo 'keyboard' não encontrado. Rode: pip install keyboard")
    raise

if os.name == 'nt':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='strict')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='strict')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "output.json")
PROMPT_KEY_FILE = os.path.join(os.path.dirname(__file__), "prompt_key.json")
_running_lock = threading.Lock()
_is_running = False

# === Funções auxiliares ===
def find_seeker_path():
    cwd = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.join(cwd, "root", "seeker.py"),
        os.path.join(cwd, "seeker.py"),
    ]
    for p in candidates:
        if os.path.isfile(p):
            return p
    return None

def find_cognix_path():
    cwd = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(cwd, "cognix.py")
    return path if os.path.isfile(path) else None

def save_output(data):
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({"result": data, "timestamp": time.time()}, f, ensure_ascii=False, indent=4)
    except Exception as ex:
        logging.exception("Erro ao salvar output.json: %s", ex)

def set_prompt_key(keyname):
    """Salva a PROMPT_KEY selecionada no arquivo prompt_key.json"""
    try:
        with open(PROMPT_KEY_FILE, "w", encoding="utf-8") as f:
            json.dump({"key": keyname}, f, ensure_ascii=False, indent=4)
        logging.info("Prompt key definido: %s", keyname)
    except Exception as ex:
        logging.exception("Erro ao salvar prompt_key.json: %s", ex)

def run_seeker():
    global _is_running
    seeker_path = find_seeker_path()
    if not seeker_path:
        logging.error("seeker.py não encontrado")
        return

    if not _running_lock.acquire(blocking=False):
        logging.info("Execução em andamento - ignorando trigger")
        return

    _is_running = True
    logging.info("Iniciando seeker - Colando pergunta no console: %s", seeker_path)

    try:
        cmd = [sys.executable, seeker_path]
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="strict"
        )

        logging.info("Seeker finalizado. returncode=%s", completed.returncode)
        if completed.stdout:
            logging.info("pergunta:\n%s", completed.stdout.strip())
        if completed.stderr:
            logging.warning("error:\n%s", completed.stderr.strip())

        result_text = completed.stdout.strip() if completed.stdout else completed.stderr.strip()
        save_output(result_text or "[vazio]")

        cognix_path = find_cognix_path()
        if cognix_path:
            logging.info("Cognix está pensando...")
            subprocess.run([sys.executable, cognix_path], encoding="utf-8", errors="strict")
        else:
            logging.warning("cognix.py não encontrado.")

    except Exception as ex:
        logging.exception("Erro ao executar seeker.py ou cognix.py: %s", ex)
    finally:
        _is_running = False
        _running_lock.release()
        logging.info("Aguardando próxima combinação de hotkey...")

def run_with_prompt(keyname):
    """Define PROMPT_KEY e executa seeker + cognix"""
    set_prompt_key(keyname)
    t = threading.Thread(target=run_seeker, daemon=True)
    t.start()

# === Main Listener ===
def main():
    logging.info("Hotkey listener iniciado.")
    logging.info("Alt+C+X → usa prompt_questionario")
    logging.info("Alt+R+S → usa prompt_traducao")
    logging.info("Alt+P → sequencia especial de cópia para clipboard")

    # Hotkeys para prompts
    keyboard.add_hotkey('alt+c+x', lambda: run_with_prompt("prompt_questionario"))
    keyboard.add_hotkey('alt+r+s', lambda: run_with_prompt("prompt_traducao"))

    # Hotkey para sequência de cópia (Alt+P)
    def run_hello():
        logging.info("Alt+P pressionado - iniciando sequência de cópia")
        import pyperclip
        sequence = [
            '.', '·', '˙', '․', '‧',
            '‚', '‥', '…', '˙', '·',
            '⸱', '⸰', '﹒', '﹐', '․',
            '・', ';', '⸳', '᛫', '⸴',
            '⸱', '⋅', '․', '‧', '․'
        ]
        for char in sequence:
            pyperclip.copy(char)
            logging.info("Copiado para clipboard: %s", char)
            time.sleep(0.1)
        logging.info("Sequência finalizada. Aguardando próxima combinação Alt+P ou hotkeys de prompt...")

    def hotkey_handler_hello():
        t = threading.Thread(target=run_hello, daemon=True)
        t.start()

    keyboard.add_hotkey('alt+p', hotkey_handler_hello)

    # Loop principal
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Finalizando por KeyboardInterrupt...")
    finally:
        logging.info("Saindo.")

if __name__ == "__main__":
    main()
