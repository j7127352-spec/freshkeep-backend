from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter(
    prefix="/api/shopping", # Change from shopping-list to shopping
    tags=["Shopping"]
)

# This needs to persist while the app is running
temp_shopping_db = []

class ShoppingItem(BaseModel):
    item_name: str # Change from 'name' to 'item_name' to match your interface

@router.get("")
def get_shopping_list():
    # Return a list of objects to match your 'ShoppingItem' interface
    return [{"id": str(i), "item_name": name, "is_purchased": False} for i, name in enumerate(temp_shopping_db)]

@router.post("")
def add_item(item: ShoppingItem):
    if item.item_name not in temp_shopping_db:
        temp_shopping_db.append(item.item_name)
    return {"message": "Added"}

# Add this to handle your 'Clear Purchased' button logic
@router.delete("/clear/purchased")
def clear_purchased():
    # Since we aren't tracking 'purchased' in this simple array yet, 
    # we'll just clear the whole thing for now
    temp_shopping_db.clear()
    return {"message": "Cleared"}