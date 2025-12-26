import pytest
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from cart.models import Cart, CartItem
from orders.services import create_order_from_cart


@pytest.mark.django_db
def test_create_order_reduces_stock_and_deactivates_cart():
    User = get_user_model()
    user = User.objects.create_user(email="a@a.com", password="123456")

    cat = Category.objects.create(name="Tech", slug="tech")
    p = Product.objects.create(category=cat, name="Mouse", slug="mouse", price="10.00", stock=5, is_active=True)

    cart = Cart.objects.create(user=user, is_active=True)
    CartItem.objects.create(cart=cart, product=p, quantity=2)

    order = create_order_from_cart(user)

    p.refresh_from_db()
    cart.refresh_from_db()

    assert order.total == 20
    assert p.stock == 3
    assert cart.is_active is False
    assert order.items.count() == 1
