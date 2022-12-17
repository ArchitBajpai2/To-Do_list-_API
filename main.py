from fastapi import FastAPI
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from bson.objectid import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

client = MongoClient("mongodb+srv://username:<password>cluster0.86tzwxv.mongodb.net/?retryWrites=true&w=majority")
db = client["todo-db"]
todo_items = db["todo-items"]

class TodoItem(BaseModel):
    title: str
    description: Optional[str] = None
    completed: Optional[bool] = False

@app.post("/todo-items/")
async def create_todo_item(item: TodoItem):
    try:
        result = todo_items.insert_one(item.dict())
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Item already exists")
    return {"_id": str(result.inserted_id)}

@app.get("/todo-items/{todo_id}")
async def read_todo_item(todo_id: str):
    todo_item = todo_items.find_one({"_id": ObjectId(todo_id)})
    if todo_item:
        return todo_item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.put("/todo-items/{todo_id}")
async def update_todo_item(todo_id: str, item: TodoItem):
    todo_item = todo_items.find_one_and_update(
        {"_id": ObjectId(todo_id)}, {"$set": item.dict()}, return_document=True
    )
    if todo_item:
        return todo_item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/todo-items/{todo_id}")
async def delete_todo_item(todo_id: str):
    result = todo_items.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "success"}