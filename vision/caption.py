import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("API_KEY"))

def generate_caption(image_input, prompt: str = "Describe this image in detail."):
    """Analyzes an image file and returns a caption and sample tags."""
    try:
        if isinstance(image_input, (str, os.PathLike)):
            with open(image_input, "rb") as f:
                image_bytes = f.read()
        else:
            image_bytes = image_input

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
                prompt
            ],
        )
        caption_text = response.text
        tags = ["gemini", "vision", "telegram-bot"]
        return caption_text, tags
    except Exception as e:
        return f"Error analyzing image: {str(e)}", []