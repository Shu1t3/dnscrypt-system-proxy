import logging
import os
import asyncio
import socket
from typing import Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in environment")

client = genai.Client(api_key=GEMINI_API_KEY)
logger = logging.getLogger(__name__)

app = FastAPI(title="DNS Leak & Proxy Test Service")


async def generate_text(prompt: str) -> str:
    """
    Вызывает Google Gemini для генерации текста по заданному prompt.
    """
    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text  # type: ignore
    except Exception as e:
        logger.error(f"Ошибка при генерации текста через Gemini: {e}")
        raise


def get_dns_info() -> Dict[str, Any]:
    """
    Получает информацию о разрешении DNS и текущих настройках.
    Помогает определить DNS-утечки.
    """
    info = {
        "dns_servers": [],
        "hostname": socket.gethostname(),
        "test_domains": {}
    }
    
    # Попытка получить текущие DNS серверы
    try:
        import socket as sock_module
        # На Linux это может быть из /etc/resolv.conf
        with open('/etc/resolv.conf', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('nameserver'):
                    dns_ip = line.split()[1]
                    info["dns_servers"].append(dns_ip)
    except Exception as e:
        info["dns_servers"].append(f"Ошибка чтения DNS: {e}")
    
    # Тестирование разрешения доменов
    test_domains = ["google.com", "cloudflare.com", "8.8.8.8.in-addr.arpa"]
    for domain in test_domains:
        try:
            ip = socket.gethostbyname(domain)
            info["test_domains"][domain] = {"resolved_to": ip, "status": "OK"}
        except Exception as e:
            info["test_domains"][domain] = {"status": "FAILED", "error": str(e)}
    
    return info


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/dns-info")
async def dns_info():
    """
    Возвращает информацию о текущих DNS серверах и результаты тестов разрешения.
    Используется для проверки DNS-утечек.
    """
    return JSONResponse(content=get_dns_info())


@app.post("/ask")
async def ask(prompt: str):
    """
    Отправляет запрос к Gemini API через прокси и возвращает ответ.
    Проверяет корректность маршрутизации через squid.
    """
    try:
        result = await generate_text(prompt)
        dns_info = get_dns_info()
        return {
            "prompt": prompt,
            "response": result,
            "dns_info": dns_info,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test():
    """
    Выполняет комплексный тест: проверяет DNS, разрешает домены,
    и отправляет запрос к Gemini API.
    """
    test_prompt = "Напиши короткое приветствие от лица бота."
    try:
        result = await generate_text(test_prompt)
        dns_info = get_dns_info()
        return {
            "test": "comprehensive",
            "prompt": test_prompt,
            "response": result,
            "dns_info": dns_info,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Ошибка при тесте: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
