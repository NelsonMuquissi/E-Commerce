import os
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from orders.models import Order
from .models import Payment
from .prontu_client import ProntuClient


@transaction.atomic
def start_prontu_payment(user, order_id: int, *, return_url: str = "", cancel_url: str = "") -> Payment:
    order = Order.objects.select_for_update().get(id=order_id, user=user)

    if order.status != Order.Status.CREATED:
        raise ValueError("Só é possível pagar pedidos no estado CREATED.")

    payment, _ = Payment.objects.get_or_create(order=order)
    payment.provider = "prontu"
    payment.status = Payment.Status.PENDING
    payment.save()

    client = ProntuClient()
    token = client.get_token()

    # Standard Checkout: currency, amount e (opcional) reference_id, email, phone, nome etc. :contentReference[oaicite:7]{index=7}
    currency = os.getenv("PRONTU_CURRENCY", "AOA")

    # expiration_date é UTC com formato YYYY-MM-DDThh:mm:ssZ
    # e só é recomendado usar se o General Callback estiver configurado/testado. :contentReference[oaicite:8]{index=8}
    expiration_utc = (timezone.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "currency": currency,
        "amount": float(order.total),
        "reference_id": str(order.id),     # “Partner’s transaction ID” :contentReference[oaicite:9]{index=9}
        "source": 0,                       # doc diz default 0 (se presente, MUST be 0) :contentReference[oaicite:10]{index=10}
        "expiration_date": expiration_utc,
        "return_url": return_url,
        "cancel_url": cancel_url,
    }

    resp = client.create_standard_checkout(token, payload)

    payment.prontu_checkout_id = resp.get("id") or ""
    data = resp.get("data") or {}
    payment.prontu_url = data.get("url") or ""
    payment.prontu_reference_id = data.get("reference_id") or ""
    payment.prontu_entity_id = data.get("entity_id") or ""
    payment.save()

    return payment
