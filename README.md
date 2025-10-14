<p align="center"> <img src="images/Cognix.png" alt="Cognix Logo" width="850"/> </p>

# .                     Cognix ⌨️
### Deep thinker keyboard v0.1

Teclado com integração a IA via Token, open source, rodando **Raspberry Pi Zero 2 W**, com capacidade de leitura de arquivos no PC conectado e execução de códigos em geral.

---

## Instalação
**Baixe as dependências:** 
- Python 3.x
- Bibliotecas necessárias:
```
pip install google.generativeai pyperclip keyboard Pillow
```
- Conta no gemeni com token premium (temporário até termos um banco de dados local)

---

## Configuração e execução — obtendo a API Key do Gemini (Google)

1. Entre em https://aistudio.google.com e faça login com sua conta Google.

2. Abra *Projects* e importe/crie um projeto do Google Cloud (cada chave fica vinculada a um projeto).

3. Vá em *API Keys* (ou *Get API key*) e clique em **Create API Key**.

4. Escolha criar a chave em um projeto existente ou criar um novo projeto, aceite os termos e confirme.

5. Copie a API Key gerada e salve em local seguro — você vai precisar dela para o `cognix.py`.

6. Substitua a área **API_KEY = [API key AQUI]** pela sua API key criada:

7. Entre na pasta do código:

```
cd src
```

8. Execute o script:

```
py listener.py
```

---

<p align="center"> <img src="images/Cognix.png" alt="Cognix Logo" width="850"/> </p>
