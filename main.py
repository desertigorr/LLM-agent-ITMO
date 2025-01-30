import requests
import xml.etree.ElementTree as ET
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_KEY = os.getenv("API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")


# ✅ Инициализируем FastAPI
app = FastAPI()

# 🔎 Модель запроса
class SearchRequest(BaseModel):
    query: str

# типа RAG
def search_yandex(query):
    # запрос
    query = "Когда ИТМО получил статус национального исследовательского университета?"

    # URL для запроса к Yandex Search API
    url = f"https://yandex.ru/search/xml?folderid={FOLDER_ID}&apikey={API_KEY}&query={query}"

    # Параметры запроса
    params = {
        "text": query,
        "lang": "ru",
        "type": "web",
        "limit": 1,
    }

    # добавляем обработку headeroв на всякий
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        # Отправка GET-запроса с параметрами в URL
        response = requests.get(url, params=params, timeout=1)
        response.raise_for_status()

        # Выводим полученный XML
        print("Полученный XML ответ:")
        print(response.text)
        print("-" * 50)

        # Парсинг XML ответа
        root = ET.fromstring(response.text)
        
        
        # Поиск результатов в XML
        results = root.findall('.//doc')
        
        # Выводим только первые три результата
        if results:
            for i, doc in enumerate(results[:3]):
                title = doc.find('title').text if doc.find('title') is not None else 'Нет заголовка'
                url = doc.find('url').text if doc.find('url') is not None else 'Нет URL'
                
                # Ищем тег extended-text в properties
                extended_text = doc.find('.//extended-text')
                extended = extended_text.text if extended_text is not None and extended_text.text else 'Нет расширенного описания'
                
                print(f"\nРезультат {i+1}:")
                print(f"Title: {title}")
                print(f"URL: {url}")
                print(f"Extended text: {extended}")
                print("-" * 50)

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
    except ET.ParseError as e:
        print(f"Ошибка при парсинге XML: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")



@app.post("/search")
def search_api(request: SearchRequest):
    results = search_yandex(request.query)
    return {"query": request.query, "results": results}

