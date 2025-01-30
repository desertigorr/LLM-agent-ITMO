from fastapi import FastAPI
from pydantic import BaseModel
import os

API_KEY = os.getenv("DEEPSEEK_API_KEY")
app = FastAPI()



# Модель запроса
class UserRequest(BaseModel):
    id: int
    query: str

@app.post("/api/request")
def handle_request(request: UserRequest):

    if request.query == "ангуляй":
        response = "энвилоуп"
    elif request.query == "ключ":
        response = f"{API_KEY}"
    else:  
        response = "не энвилоуп"

    return {
        "id": request.id,
        "answer": response
    }