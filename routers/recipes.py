from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

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
    # Convert all pantry ingredients to lowercase for easy searching
    pantry = [i.lower() for i in request.ingredients]
    
    # --- 1. CHICKEN LOGIC ---
    if any("chicken" in item for item in pantry):
        return {
            "title": "Roasted Garlic Chicken",
            "story": "Since you have chicken and garlic in your pantry, this aromatic roast is the perfect way to use them up!",
            "ingredients": ["Chicken", "Garlic (Minced)", "Olive Oil", "Salt", "Pepper"],
            "instructions": [
                "Preheat oven to 400°F.",
                "Rub the chicken with olive oil and plenty of minced garlic.",
                "Season generously with salt and pepper.",
                "Roast for 25-30 minutes until juices run clear.",
                "Let rest for 5 minutes before serving."
            ],
            "prep_time": "10 mins",
            "cook_time": "30 mins"
        }

    # --- 2. PASTA LOGIC ---
    elif any("pasta" in item for item in pantry) or any("spaghetti" in item for item in pantry):
        return {
            "title": "Pantry Pasta Aglio e Olio",
            "story": "A classic Italian 'poor man's meal' that turns simple pantry staples into a gourmet dinner.",
            "ingredients": ["Pasta", "Garlic", "Olive Oil", "Red Pepper Flakes (optional)"],
            "instructions": [
                "Boil a large pot of salted water and cook pasta until al dente.",
                "While pasta cooks, heat olive oil in a pan over medium heat.",
                "Sauté thinly sliced garlic until golden (don't burn it!).",
                "Toss the cooked pasta into the oil and garlic. Add a splash of pasta water to make it glossy."
            ],
            "prep_time": "5 mins",
            "cook_time": "10 mins"
        }

    # --- 3. TACO / MEXICAN LOGIC ---
    elif any("tortilla" in item for item in pantry) or any("bean" in item for item in pantry):
        return {
            "title": "Quick Pantry Quesadillas",
            "story": "Using your tortillas and pantry staples for a quick, cheesy, and satisfying meal.",
            "ingredients": ["Tortillas", "Cheese", "Beans", "Any leftover protein"],
            "instructions": [
                "Place a tortilla in a dry pan over medium heat.",
                "Sprinkle cheese and beans (and garlic!) on one half.",
                "Fold the tortilla over and cook until golden brown on both sides.",
                "Slice into triangles and serve."
            ],
            "prep_time": "5 mins",
            "cook_time": "6 mins"
        }

    # --- 4. SEAFOOD LOGIC ---
    elif any("shrimp" in item for item in pantry) or any("fish" in item for item in pantry) or any("salmon" in item for item in pantry):
        return {
            "title": "Lemon Garlic Butter Seafood",
            "story": "Seafood cooks fast! This recipe highlights the fresh flavors of your pantry ingredients.",
            "ingredients": ["Seafood of choice", "Butter or Oil", "Garlic", "Lemon (if available)"],
            "instructions": [
                "Pat the seafood dry with paper towels.",
                "Heat butter and garlic in a pan until fragrant.",
                "Sear the seafood for 2-3 minutes per side.",
                "Squeeze lemon over the top and serve immediately."
            ],
            "prep_time": "5 mins",
            "cook_time": "8 mins"
        }

    # --- 5. VEGGIE/EGG LOGIC (DEFAULT) ---
    else:
        return {
            "title": "FreshKeep Garden Scramble",
            "story": "A healthy way to use up your miscellaneous pantry items and eggs.",
            "ingredients": ["3 Eggs", "Miscellaneous Veggies", "Salt & Pepper"],
            "instructions": [
                "Whisk the eggs in a small bowl.",
                "Sauté your pantry veggies in a pan.",
                "Pour in eggs and scramble until fluffy.",
                "Season and serve immediately."
            ],
            "prep_time": "5 mins",
            "cook_time": "5 mins"
        }