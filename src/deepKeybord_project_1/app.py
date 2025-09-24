import requests
import json

response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer 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",
    "Content-Type": "application/json",
  },
  data=json.dumps({
    "model": "x-ai/grok-4-fast:free",
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