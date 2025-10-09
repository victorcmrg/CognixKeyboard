# -*- coding: utf-8 -*-
import pyperclip
import sys
import io
from PIL import ImageGrab
import os
import time

# Configuração de saída UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Caminho raiz do projeto
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(ROOT_DIR, "prompt", "imagem")

# Garante que a pasta exista
os.makedirs(IMAGE_DIR, exist_ok=True)


def main():
    image = ImageGrab.grabclipboard()

    if image is not None:
        # Cria nome único e salva na pasta prompt/imagem
        filename = f"imagem_clipboard_{int(time.time())}.png"
        filepath = os.path.join(IMAGE_DIR, filename)
        image.save(filepath, 'PNG')
        print(f"🟢 Imagem detectada e salva em: {filepath}")
    else:
        text = pyperclip.paste()
        if text:
            print(f"🟢 Texto detectado:\n{text}")
        else:
            print("🔴 Nenhum texto ou imagem encontrado na área de transferência.")


if __name__ == "__main__":
    main()
