import logging
import os
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

client = genai.Client(api_key=GEMINI_API_KEY)
logger = logging.getLogger(__name__)


async def generate_text(prompt: str) -> str:
    """
    Вызывает Google Gemini для генерации текста по заданному prompt.
    """
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text  # type: ignore
    except Exception as e:
        logger.error(f"Ошибка при генерации текста через Gemini: {e}")
        raise


if __name__ == "__main__":
    async def main():
        test_prompt = "Напиши короткое приветствие от лица бота."
        print("=== TEST PROMPT ===")
        print(test_prompt)
        try:
            result = await generate_text(test_prompt)
            print("=== RESPONSE ===")
            print(result)
        except Exception as e:
            print(f"Произошла ошибка во время тестового запуска: {e}")

    asyncio.run(main())
