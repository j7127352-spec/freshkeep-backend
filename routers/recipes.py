from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import time

# NOTE: We removed 'from database import...' so this file is safe!

router = APIRouter(
    prefix="/api/recipes",
    tags=["Recipes"]
)

class RecipeRequest(BaseModel):
    ingredients: List[str]

class RecipeResponse(BaseModel):
    title: str
    story: str
    ingredients: List[str]
    instructions: List[str]
    prep_time: str
    cook_time: str

@router.post("/generate", response_model=RecipeResponse)
def generate_recipe(request: RecipeRequest):
    # 1. Simulate "Thinking" Delay (so you see the spinner on your phone)
    time.sleep(2) 

    # 2. Return the Recipe
    return {
        "title": "Zero-Waste Pantry Frittata",
        "story": "A delicious, fluffy egg dish designed to rescue your expiring vegetables. Perfect for breakfast or a quick dinner!",
        "ingredients": [
            "3 Eggs (Use up expiring ones!)",
            "1/2 Onion, diced",
            "1/2 Bell Pepper, chopped",
            "Salt & Black Pepper",
            "1 tbsp Olive Oil"
        ],
        "instructions": [
            "Crack eggs into a bowl, whisk with salt and pepper.",
            "Heat olive oil in a pan over medium heat.",
            "Sauté onion and peppers until soft (about 5 mins).",
            "Pour eggs over the veggies. Tilt pan to spread evenly.",
            "Cook for 3-4 mins until edges are set, then flip or finish under a broiler.",
            "Serve hot and enjoy your saved food!"
        ],
        "prep_time": "5 mins",
        "cook_time": "10 mins"
    }