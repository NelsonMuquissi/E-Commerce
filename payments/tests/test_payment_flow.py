import os
import json
import pytest
from django.urls import reverse
from orders.models import Order
from payments.models import Payment

@pytest.mark.django_db
def test_prontu_webhook_marks_order_paid(client, user):
    order = Order.objects.create(user=user, status=Order.Status.CREATED, total=1000)
    Payment.objects.create(order=order, provider="prontu", status=Payment.Status.PENDING)

    secret = os.getenv("PRONTU_CALLBACK_SECRET", "testsecret")
    url = f"/api/webhooks/prontu/{secret}/"

    payload = {
        "result": {
            "operation": "receive",
            "status": "accepted",
            "reference_id": str(order.id),
            "prontu_transaction_id": "tx_001",
        }
    }

    resp = client.post(url, data=json.dumps(payload), content_type="application/json")
    assert resp.status_code == 200

    order.refresh_from_db()
    assert order.status == Order.Status.PAID
