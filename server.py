from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import uvicorn
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
SECRET_KEY = os.environ.get('JWT_SECRET', 'freshkeep-secret-key-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

# Create the main app
app = FastAPI(title="FreshKeep API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== MODELS ====================

# User Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    is_premium: bool
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Pantry Item Models
class PantryItemCreate(BaseModel):
    name: str
    category: str
    expiry_date: str  # ISO format date string
    quantity: int = 1
    barcode: Optional[str] = None

class PantryItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    expiry_date: Optional[str] = None
    quantity: Optional[int] = None
    status: Optional[str] = None
    barcode: Optional[str] = None

class PantryItemResponse(BaseModel):
    id: str
    user_id: str
    name: str
    category: str
    expiry_date: str
    quantity: int
    barcode: Optional[str] = None
    status: str
    created_at: datetime

# Shopping List Models
class ShoppingItemCreate(BaseModel):
    item_name: str

class ShoppingItemUpdate(BaseModel):
    item_name: Optional[str] = None
    is_purchased: Optional[bool] = None

class ShoppingItemResponse(BaseModel):
    id: str
    user_id: str
    item_name: str
    is_purchased: bool
    created_at: datetime

# ==================== HELPER FUNCTIONS ====================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": user_id, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "is_premium": False,
        "created_at": datetime.utcnow()
    }
    await db.users.insert_one(user)
    
    # Create token
    access_token = create_access_token(user_id)
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user_id,
            email=user_data.email,
            is_premium=False,
            created_at=user["created_at"]
        )
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    user = await db.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(user["id"])
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            is_premium=user["is_premium"],
            created_at=user["created_at"]
        )
    )

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        is_premium=current_user["is_premium"],
        created_at=current_user["created_at"]
    )

# ==================== USER ROUTES ====================

@api_router.post("/user/upgrade-premium", response_model=UserResponse)
async def upgrade_to_premium(current_user: dict = Depends(get_current_user)):
    """Mock purchase - upgrades user to premium"""
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"is_premium": True}}
    )
    
    updated_user = await db.users.find_one({"id": current_user["id"]})
    return UserResponse(
        id=updated_user["id"],
        email=updated_user["email"],
        is_premium=updated_user["is_premium"],
        created_at=updated_user["created_at"]
    )

# ==================== PANTRY ROUTES ====================

@api_router.get("/pantry", response_model=List[PantryItemResponse])
async def get_pantry_items(current_user: dict = Depends(get_current_user)):
    items = await db.pantry_items.find({"user_id": current_user["id"]}).to_list(1000)
    return [PantryItemResponse(**item) for item in items]

@api_router.post("/pantry", response_model=PantryItemResponse)
async def create_pantry_item(item: PantryItemCreate, current_user: dict = Depends(get_current_user)):
    item_id = str(uuid.uuid4())
    pantry_item = {
        "id": item_id,
        "user_id": current_user["id"],
        "name": item.name,
        "category": item.category,
        "expiry_date": item.expiry_date,
        "quantity": item.quantity,
        "barcode": item.barcode,
        "status": "fresh",
        "created_at": datetime.utcnow()
    }
    await db.pantry_items.insert_one(pantry_item)
    return PantryItemResponse(**pantry_item)

@api_router.put("/pantry/{item_id}", response_model=PantryItemResponse)
async def update_pantry_item(
    item_id: str,
    item_update: PantryItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    existing = await db.pantry_items.find_one({"id": item_id, "user_id": current_user["id"]})
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = {k: v for k, v in item_update.dict().items() if v is not None}
    
    # If marking as consumed or wasted, add to shopping list
    if item_update.status in ["consumed", "wasted"]:
        shopping_item = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "item_name": existing["name"],
            "is_purchased": False,
            "created_at": datetime.utcnow()
        }
        await db.shopping_list.insert_one(shopping_item)
    
    if update_data:
        await db.pantry_items.update_one({"id": item_id}, {"$set": update_data})
    
    updated = await db.pantry_items.find_one({"id": item_id})
    return PantryItemResponse(**updated)

@api_router.delete("/pantry/{item_id}")
async def delete_pantry_item(item_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.pantry_items.delete_one({"id": item_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

# ==================== SHOPPING LIST ROUTES ====================

@api_router.get("/shopping", response_model=List[ShoppingItemResponse])
async def get_shopping_list(current_user: dict = Depends(get_current_user)):
    items = await db.shopping_list.find({"user_id": current_user["id"]}).to_list(1000)
    return [ShoppingItemResponse(**item) for item in items]

@api_router.post("/shopping", response_model=ShoppingItemResponse)
async def create_shopping_item(item: ShoppingItemCreate, current_user: dict = Depends(get_current_user)):
    item_id = str(uuid.uuid4())
    shopping_item = {
        "id": item_id,
        "user_id": current_user["id"],
        "item_name": item.item_name,
        "is_purchased": False,
        "created_at": datetime.utcnow()
    }
    await db.shopping_list.insert_one(shopping_item)
    return ShoppingItemResponse(**shopping_item)

@api_router.put("/shopping/{item_id}", response_model=ShoppingItemResponse)
async def update_shopping_item(
    item_id: str,
    item_update: ShoppingItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    existing = await db.shopping_list.find_one({"id": item_id, "user_id": current_user["id"]})
    if not existing:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = {k: v for k, v in item_update.dict().items() if v is not None}
    if update_data:
        await db.shopping_list.update_one({"id": item_id}, {"$set": update_data})
    
    updated = await db.shopping_list.find_one({"id": item_id})
    return ShoppingItemResponse(**updated)

@api_router.delete("/shopping/{item_id}")
async def delete_shopping_item(item_id: str, current_user: dict = Depends(get_current_user)):
    result = await db.shopping_list.delete_one({"id": item_id, "user_id": current_user["id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}

@api_router.delete("/shopping/clear/purchased")
async def clear_purchased_items(current_user: dict = Depends(get_current_user)):
    result = await db.shopping_list.delete_many({"user_id": current_user["id"], "is_purchased": True})
    return {"message": f"Cleared {result.deleted_count} purchased items"}

# ==================== ROOT & HEALTH ====================

@api_router.get("/")
async def root():
    return {"message": "FreshKeep API is running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

    # ==================== START SERVER ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
