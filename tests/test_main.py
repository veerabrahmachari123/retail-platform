import pytest
from app.main import RetailPlatform, CartItem

@pytest.fixture
def platform():
    p = RetailPlatform()
    p.add_product("Laptop", 999.99, 10)
    p.add_product("Mouse", 25.50, 50)
    return p

def test_add_product(platform):
    product = platform.add_product("Keyboard", 45.00, 20)
    assert product.id == 3
    assert product.name == "Keyboard"
    assert platform.get_product(3) is not None

def test_checkout_success(platform):
    cart = [
        CartItem(product_id=1, quantity=1),
        CartItem(product_id=2, quantity=2)
    ]
    order = platform.checkout(cart)
    
    assert order.id == 1
    assert order.total_price == 1050.99
    assert platform.get_product(1).stock == 9
    assert platform.get_product(2).stock == 48

def test_checkout_insufficient_stock(platform):
    cart = [CartItem(product_id=1, quantity=11)]
    with pytest.raises(ValueError, match="Insufficient stock"):
        platform.checkout(cart)

def test_checkout_invalid_product(platform):
    cart = [CartItem(product_id=99, quantity=1)]
    with pytest.raises(ValueError, match="does not exist"):
        platform.checkout(cart)

def test_checkout_empty_cart(platform):
    with pytest.raises(ValueError, match="Cart is empty"):
        platform.checkout([])
