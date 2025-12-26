import pytest
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from cart.models import Cart, CartItem
from orders.services import create_order_from_cart, cancel_order


@pytest.mark.django_db
def test_cancel_order_returns_stock():
    User = get_user_model()
    user = User.objects.create_user(email="c@c.com", password="123456")

    cat = Category.objects.create(name="Tech3", slug="tech3")
    p = Product.objects.create(category=cat, name="Monitor", slug="monitor", price="100.00", stock=10, is_active=True)

    cart = Cart.objects.create(user=user, is_active=True)
    CartItem.objects.create(cart=cart, product=p, quantity=4)

    order = create_order_from_cart(user)
    p.refresh_from_db()
    assert p.stock == 6

    cancel_order(user, order.id)
    p.refresh_from_db()
    assert p.stock == 10
