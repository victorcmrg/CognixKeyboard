import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer (TOKEN AQUI)",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "(MODELO AQUI)",
    "messages": [
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": "busque na internet e me de um link de uma imagem do espaço no google"
          },
        #   {
        #     "type": "image_url",
        #      "image_url": {
        #        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
        #      }
        #    }
        ]
      }
    ],
  })
)

# print("Status code:", response.status_code)
print("Resposta:", response.text)
