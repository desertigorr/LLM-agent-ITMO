import requests
import xml.etree.ElementTree as ET
import os
from fastapi import FastAPI
from pydantic import BaseModel


LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_KEY = os.getenv("API_KEY")
FOLDER_ID = os.getenv("FOLDER_ID")



# Создаем FastAPI
app = FastAPI()

# Класс для запроса
class SearchRequest(BaseModel):
    query: str
    id: int

# 🔎 Функция для запроса в Yandex Search API
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

        root = ET.fromstring(response.text)
        results = []

        # Поиск результатов в XML
        docs = root.findall('.//doc')[:3]

        for doc in docs:
            title = doc.find('title').text if doc.find('title') is not None else 'Нет заголовка'
            url = doc.find('url').text if doc.find('url') is not None else 'Нет URL'
            extended_text = doc.find('.//extended-text')
            snippet = extended_text.text if extended_text is not None else 'Нет описания'

            results.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        return results  # ✅ API получит корректные данные

    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return []
    except ET.ParseError as e:
        print(f"Ошибка парсинга XML: {e}")
        return []
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return []

# 🔥 Функция запроса в LLM
def query_llm(query, sources):
    URL = "https://api.together.xyz/v1/chat/completions"
    HEADERS = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json"
    }

    # Формируем промпт для LLM
    formatted_query = f"""
    Ты - интеллектуальный ассистент, который отвечает на вопросы про Университет ИТМО.
    Вопрос может включать в себя варианты ответа 1-10 или может быть открытым (без вариантов ответа)
    Используй приведенные ниже источники данных и выбери правильный ответ.
    Формат вывода ответа:
    Если вопрос требует выбора варианта, верни ТОЛЬКО число, обозначающее номер ответа, например если варианты
    ответа - 1. А 2. Б - ты должен ответить "1." если правильный ответ "А". 
    Если вариантов ответа НЕТ - ответь ТОЛЬКО "-1".

    Вопрос: {query}
    Данные:
    {" | ".join([res["snippet"] for res in sources])}
    """
    reasoning_src = {" | ".join([res["snippet"] for res in sources])}
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [{"role": "user", "content": formatted_query}],
        "temperature": 0.5,
        "max_tokens": 400
    }

    response = requests.post(URL, headers=HEADERS, json=data)
    
    if response.status_code == 200:
        res = (response.json()["choices"][0]["message"]["content"], reasoning_src)
        return res
    else:
        return f"Ошибка: {response.status_code}, {response.json()}"

# 🌍 API для поиска и ответа
@app.post("/search")
def search_api(request: SearchRequest):
    results = search_yandex(request.query)

    if not results:
        return {"id": request.id, "answer": None, "reasoning": "Нет данных", "sources": []}

    # Отправляем в LLM
    response =  query_llm(request.query, results)
    llm_response = response[0]
    if llm_response == "-1":
        llm_response = "null"

    return {
        "id": request.id,
        "answer": llm_response,
        "reasoning": response[1],
        "sources": [res["url"] for res in results]
    }