import requests
import xml.etree.ElementTree as ET
import os
from fastapi import FastAPI
from pydantic import BaseModel


LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_KEY = os.getenv("API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")

app = FastAPI()

class SearchRequest(BaseModel):
    query: str

def search_yandex(query):
    url = f"https://yandex.ru/search/xml?folderid={FOLDER_ID}&apikey={API_KEY}&query={query}"

    params = {
        "text": query,
        "lang": "ru",
        "type": "web",
        "limit": 3,
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=3)
        response.raise_for_status()

        # Дебаг: Сырые данные от Yandex
        print("📡 Полученный XML ответ:")
        print(response.text)
        print("-" * 50)

        root = ET.fromstring(response.text)
        results = []

        # Дебаг: Проверяем, какие теги есть в XML
        print("🔎 Все найденные теги в XML:")
        for child in root.iter():
            print(f"Найден тег: {child.tag}")

        # Дебаг: Ищем в XML данные о результатах
        docs = root.findall('.//doc')
        if not docs:
            print("❌ Внимание! В XML нет тега <doc>. Попробуй изменить поиск!")
        
        # Обрабатываем каждый результат
        for doc in docs:
            title = doc.find('title').text if doc.find('title') is not None else 'Нет заголовка'
            url = doc.find('url').text if doc.find('url') is not None else 'Нет URL'
            extended_text = doc.find('.//extended-text')
            snippet = extended_text.text if extended_text is not None else 'Нет расширенного описания'
            
            results.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        return results  # ✅ Теперь API получит данные

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return []
    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return []

@app.post("/search")
def search_api(request: SearchRequest):
    results = search_yandex(request.query)
    return {"query": request.query, "results": results}
