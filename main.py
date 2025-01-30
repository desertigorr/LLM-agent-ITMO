from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Модель запроса
class UserRequest(BaseModel):
    id: int
    query: str

@app.post("/api/request")
def handle_request(request: UserRequest):
    """
    Если query = "1", сервер отвечает "2".
    В остальных случаях сервер отвечает "3".
    """
    if request.query == "ангуляй":
        response = "энвилоуп"
    else:
        response = "не энвилоуп"

    return {
        "id": request.id,
        "answer": response
    }