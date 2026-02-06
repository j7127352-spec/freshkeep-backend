from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/api/shopping-list",
    tags=["Shopping List"]
)

# This is a temporary list. In a future step, we can link this to your database.
temp_shopping_db = []

class ShoppingItem(BaseModel):
    name: str

@router.get("/", response_model=List[str])
def get_shopping_list():
    return temp_shopping_db

@router.post("/")
def add_item(item: ShoppingItem):
    if item.name not in temp_shopping_db:
        temp_shopping_db.append(item.name)
    return {"message": f"Added {item.name} to list"}

@router.delete("/{item_name}")
def delete_item(item_name: str):
    if item_name in temp_shopping_db:
        temp_shopping_db.remove(item_name)
    return {"message": "Deleted"}