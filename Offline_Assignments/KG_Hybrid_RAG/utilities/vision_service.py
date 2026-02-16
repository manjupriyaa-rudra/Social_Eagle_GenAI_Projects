import base64
from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def image_to_text(image_path: str) -> str:
    with open(image_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    response = client.chat.completions.create(
        model=settings.MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Extract all components, services, "
                            "and relationships from this architecture diagram."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img}"
                        }
                    }
                ]
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
