import requests
import xml.etree.ElementTree as ET
import os
from fastapi import FastAPI
from pydantic import BaseModel

# Загружаем переменные окружения
API_KEY = os.getenv("API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")

# Инициализируем FastAPI
app = FastAPI()

# Модель запроса
class SearchRequest(BaseModel):
    query: str

# Функция для поиска
def search_yandex(query):
    url = "https://yandex.ru/search/xml"
    params = {
        "folderid": FOLDER_ID,
        "apikey": API_KEY,
        "text": query,
        "lang": "ru",
        "type": "web",
        "limit": 5
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=3)
        response.raise_for_status()

        # Парсим XML-ответ
        root = ET.fromstring(response.text)
        results = root.findall('.//doc')

        extracted_results = []
        for doc in results:
            title_element = doc.find("title")
            url_element = doc.find("url")
            snippet_element = doc.find(".//passages/pass")

            title = title_element.text if title_element is not None else "Нет заголовка"
            url = url_element.text if url_element is not None else "Нет URL"
            snippet = snippet_element.text if snippet_element is not None else "Нет описания"

            extracted_results.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        return extracted_results

    except requests.exceptions.RequestException as e:
        return [{"error": f"Ошибка запроса: {e}"}]
    except ET.ParseError as e:
        return [{"error": f"Ошибка парсинга XML: {e}"}]
    except Exception as e:
        return [{"error": f"Неожиданная ошибка: {e}"}]

# API эндпоинт
@app.post("/search")
def search_api(request: SearchRequest):
    results = search_yandex(request.query)
    return {"query": request.query, "results": results}
