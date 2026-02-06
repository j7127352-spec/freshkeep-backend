from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- 1. IMPORT THE RECIPE ROUTER ---
# This grabs the code from the 'routers' folder
from routers import recipes

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

# --- 3. PLUG IN THE ROUTER (CRITICAL STEP) ---
# Without this line, the app ignores your recipes.py file!
app.include_router(recipes.router)

# Root check
@app.get("/")
def read_root():
    return {"message": "FreshKeep API is running 🥬"}