from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0, description="Price must be greater than zero")
    stock: int = Field(ge=0, description="Stock cannot be negative")

class CartItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be at least 1")

class Order(BaseModel):
    id: int
    items: List[CartItem]
    total_price: float
    status: str = "Pending"

class RetailPlatform:
    def __init__(self):
        self.products: Dict[int, Product] = {}
        self.orders: Dict[int, Order] = {}
        self._next_product_id = 1
        self._next_order_id = 1

    def add_product(self, name: str, price: float, stock: int) -> Product:
        product = Product(id=self._next_product_id, name=name, price=price, stock=stock)
        self.products[product.id] = product
        self._next_product_id += 1
        return product

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.products.get(product_id)

    def checkout(self, cart: List[CartItem]) -> Order:
        if not cart:
            raise ValueError("Cart is empty")

        total_price = 0.0
        # Validate stock and calculate total first
        for item in cart:
            product = self.get_product(item.product_id)
            if not product:
                raise ValueError(f"Product with ID {item.product_id} does not exist")
            if product.stock < item.quantity:
                raise ValueError(f"Insufficient stock for {product.name}. Available: {product.stock}")
            total_price += product.price * item.quantity

        # Deduct stock and finalize order
        for item in cart:
            product = self.get_product(item.product_id)
            product.stock -= item.quantity

        order = Order(id=self._next_order_id, items=cart, total_price=round(total_price, 2))
        self.orders[order.id] = order
        self._next_order_id += 1
        return order
