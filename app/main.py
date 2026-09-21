from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List

# Initialize the live web server
app = FastAPI(title="Retail Platform API")

# --- In-Memory Database State ---
PRODUCTS_DB: Dict[int, dict] = {
    1: {"id": 1, "name": "Wireless Mouse", "price": 25.0, "stock": 10},
    2: {"id": 2, "name": "Mechanical Keyboard", "price": 75.0, "stock": 5}
}

# --- Data Validation Schemas (Pydantic) ---
class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")
    stock: int = Field(ge=0, description="Stock cannot be negative")

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be at least 1")

# --- Web Server Endpoints ---

@app.get("/health")
def health_check():
    """
    Mandatory Health Check endpoint for Jenkins verification.
    """
    return {"status": "healthy", "platform": "retail-core"}

@app.get("/products", response_model=List[Product])
def get_all_products():
    """
    Fetch all items in the store catalog.
    """
    return list(PRODUCTS_DB.values())

@app.post("/checkout")
def checkout_cart(cart: List[CartItem]):
    """
    Processes checkout atomically, validating stock limits safely.
    """
    if not cart:
        raise HTTPException(status_code=400, detail="Cart cannot be empty")
        
    # Phase 1: Verify all stock constraints before modifying anything
    for item in cart:
        if item.product_id not in PRODUCTS_DB:
            raise HTTPException(
                status_code=404, 
                detail=f"Product with ID {item.product_id} not found"
            )
        
        product = PRODUCTS_DB[item.product_id]
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient stock for {product['name']}. Available: {product['stock']}"
            )
            
    # Phase 2: Deduct items from stock safely
    total_price = 0.0
    for item in cart:
        product = PRODUCTS_DB[item.product_id]
        product["stock"] -= item.quantity
        total_price += product["price"] * item.quantity
        
    return {
        "message": "Checkout successful",
        "total_amount": total_price,
        "remaining_catalog": list(PRODUCTS_DB.values())
    }
