from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 1. IMPORT THE ROUTERS ---
# This grabs the code from the 'routers' folder
from routers import recipes
from routers import shopping_list  # <-- Added this line

app = FastAPI()

# --- 2. CONFIGURE SECURITY (CORS) ---
# This allows your phone to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 3. PLUG IN THE ROUTERS (CRITICAL STEP) ---
# We are now including both the Recipe logic and the Shopping List logic
app.include_router(recipes.router)
app.include_router(shopping_list.router) # <-- Added this line

# Root check
@app.get("/")
def read_root():
    return {"message": "FreshKeep API is running 🥬"}