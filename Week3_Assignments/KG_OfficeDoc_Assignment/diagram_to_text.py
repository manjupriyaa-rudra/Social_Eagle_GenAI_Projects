# diagram_to_text.py
import base64
import asyncio
import os

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def image_to_text(image_path: str) -> str:
    """
    Convert architecture diagram image to structured text using OpenAI Vision.
    """
    try:
        with open(image_path, "rb") as f:
            image_base64 = base64.b64encode(f.read()).decode()

        # Call OpenAI Vision model (GPT-4.1-mini)
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert software architect."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Describe this architecture diagram in detail. "
                                        "Extract services, components, data flow, dependencies."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ]
            )
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Error processing image: {e}"
