import pytest
from rest_framework.test import APIClient
from orders.models import Order
from payments.models import Payment

@pytest.mark.django_db
def test_get_order_payment_status(user):
    client = APIClient()
    client.force_authenticate(user=user)

    order = Order.objects.create(user=user, status=Order.Status.CREATED, total=1000)
    Payment.objects.create(order=order, provider="prontu", status=Payment.Status.PENDING)

    resp = client.get(f"/api/my-orders/{order.id}/payment/")
    assert resp.status_code == 200
    assert resp.data["status"] == "PENDING"
