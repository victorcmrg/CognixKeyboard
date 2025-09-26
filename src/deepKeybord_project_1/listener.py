# hotkey_runner.py
import os
import threading
import subprocess
import logging
import sys
import time
import json

try:
    import keyboard  # pip install keyboard
except Exception as e:
    print("Módulo 'keyboard' não encontrado. Rode: pip install keyboard")
    raise

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Arquivo compartilhado
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "output.json")

_running_lock = threading.Lock()
_is_running = False

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
    """Grava o resultado do seeker em output.json"""
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump({"result": data, "timestamp": time.time()}, f, ensure_ascii=False, indent=4)
        logging.info("Resultado salvo em %s", OUTPUT_FILE)
    except Exception as ex:
        logging.exception("Erro ao salvar output.json: %s", ex)

def run_seeker():
    global _is_running
    seeker_path = find_seeker_path()
    if not seeker_path:
        logging.error("Não encontrou 'root/seeker.py' nem 'seeker.py'.")
        return

    if not _running_lock.acquire(blocking=False):
        logging.info("Execução em andamento — ignorando trigger.")
        return

    _is_running = True
    logging.info("Iniciando seeker: %s", seeker_path)

    try:
        # Executa seeker.py
        cmd = [sys.executable, seeker_path]
        completed = subprocess.run(cmd, capture_output=True, text=True)

        # Log no console
        logging.info("Seeker finalizado. returncode=%s", completed.returncode)
        if completed.stdout:
            logging.info("stdout:\n%s", completed.stdout.strip())
        if completed.stderr:
            logging.warning("stderr:\n%s", completed.stderr.strip())

        # Salva no arquivo JSON
        result_text = completed.stdout.strip() if completed.stdout else completed.stderr.strip()
        save_output(result_text or "[vazio]")

        # Executa cognix.py
        cognix_path = find_cognix_path()
        if cognix_path:
            logging.info("Executando cognix.py...")
            subprocess.run([sys.executable, cognix_path])
        else:
            logging.warning("cognix.py não encontrado.")

    except Exception as ex:
        logging.exception("Erro ao executar seeker.py ou cognix.py: %s", ex)
    finally:
        _is_running = False
        _running_lock.release()
        logging.info("Aguardando próxima combinação Alt+C+X...")

def hotkey_handler():
    t = threading.Thread(target=run_seeker, daemon=True)
    t.start()

def main():
    logging.info("Hotkey listener iniciado. Pressione Alt + C + X para executar root/seeker.py")
    keyboard.add_hotkey('alt+c+x', hotkey_handler)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Finalizando por KeyboardInterrupt...")
    finally:
        logging.info("Saindo.")

if __name__ == "__main__":
    main()


## PROMPT   V V V

# Você é um assistente inteligente. Sua tarefa é analisar a mensagem que receber e responder da forma adequada:

# 1. Primeiro, identifique se a mensagem é uma pergunta de prova teste algo assim, ou relacionado a você mesmo ou coisas do dia a dia.
# 2. Se for uma pergunta de prova teste questionário etc, determine do que ela trata (assunto ou contexto).
# 3. Verifique se a pergunta é de múltipla escolha (alternativa) ou dissertativa:
#    - Se for **alternativa**, responda **somente com a letra da opção correta**, no formato "a)", "b)", "c)" (e a resposta na questao) mesmo que no texto enviado nao tenha o numero de cada opção, então fique atento para entender se é uma pergunta de alternativa etc.
#    - Se for **dissertativa**, escreva uma resposta **humana, clara e simples**, que explique a ideia principal e seja fácil de entender, e em caso de logica, explique a questão apenas se pedido na pergunta, caso contrario apenas a resposta.
# sem explicação, apenas resposta, e no caso de ser uma pergunta de alternativa, antes da sua resposta ponha um 🟢, e caso nenhuma das alternativas esteja correta apenas envie 🔴como um não entendi, então pense novamente antes de enviar isso pra garantir a melhor resposta
# 4. Sempre que possível, **pesquise mentalmente ou considere a melhor resposta** antes de escrever, para entregar informação correta.

# Não forneça explicações adicionais quando a pergunta for de múltipla escolha; apenas a letra correta.

# limite para respostas que precisam de escrita, 30 - 50 palavras, caso seja uma pergunta de redação ou que um texto deve ser escrito, escreva de forma 
# humana e de 50 - 500 palavras, a não ser que na pergunta tenha o numero limite e seja maior de 500 palavras, e de logica, apenas de a resposta, não explique, 
# apenas se a pergunta pedir, e a resposta deve ser humana como se o usuário tivesse escrito a resposta, "pois bla bla bla" explicação clara, e sempre use palavras
#  claras caso a pergunta precise de resposta escrita, nao use palavras dificeis 