import pytest
from django.contrib.auth import get_user_model
from catalog.models import Category, Product
from cart.models import Cart, CartItem
from orders.services import create_order_from_cart
from payments.services import create_payment, confirm_payment
from orders.models import Order


@pytest.mark.django_db
def test_confirm_payment_marks_order_paid():
    User = get_user_model()
    user = User.objects.create_user(email="d@d.com", password="123456")

    cat = Category.objects.create(name="Tech4", slug="tech4")
    p = Product.objects.create(category=cat, name="Headset", slug="headset", price="30.00", stock=3, is_active=True)

    cart = Cart.objects.create(user=user, is_active=True)
    CartItem.objects.create(cart=cart, product=p, quantity=1)

    order = create_order_from_cart(user)
    assert order.status == Order.Status.CREATED

    payment = create_payment(user, order.id, provider="manual")
    confirm_payment(payment.id)

    order.refresh_from_db()
    assert order.status == Order.Status.PAID
