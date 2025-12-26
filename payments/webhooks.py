import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

from payments.models import PaymentEvent
from payments.models import Payment
from orders.models import Order


@csrf_exempt
def prontu_general_callback(request, secret: str):
    # Segurança simples: segredo na URL
    if secret != os.getenv("PRONTU_CALLBACK_SECRET"):
        return JsonResponse({"detail": "unauthorized"}, status=401)

    if request.method != "POST":
        return JsonResponse({"detail": "method not allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        # responde 200 para evitar retry infinito
        return JsonResponse({"ok": True}, status=200)

    result = (payload or {}).get("result") or {}
    operation = result.get("operation")
    status_ = result.get("status")
    reference_id = result.get("reference_id")
    prontu_tx_id = result.get("prontu_transaction_id")

    PaymentEvent.objects.create(
    provider="prontu",
    order_id=str(reference_id or ""),
    prontu_transaction_id=str(prontu_tx_id or ""),
    status=str(status_ or ""),
    operation=str(operation or ""),
    payload=payload,
    )

    # Só processa operações de pagamento
    if operation not in ("receive", "reference"):
        return JsonResponse({"ok": True}, status=200)

    # No teu projeto, reference_id = order.id
    try:
        order_id = int(reference_id)
    except Exception:
        return JsonResponse({"ok": True}, status=200)

    with transaction.atomic():
        payment = Payment.objects.select_for_update().filter(order_id=order_id).first()
        if not payment:
            return JsonResponse({"ok": True}, status=200)

        payment.prontu_transaction_id = prontu_tx_id or payment.prontu_transaction_id
        payment.raw_last_callback = payload

        # Gray zone: accepted pode chegar depois de expired -> accepted vence
        if status_ == "accepted":
            payment.status = Payment.Status.SUCCESS
            payment.save(update_fields=["status", "prontu_transaction_id", "raw_last_callback", "updated_at"])
            Order.objects.filter(id=order_id).update(status=Order.Status.PAID)

        elif status_ == "rejected":
            if payment.status != Payment.Status.SUCCESS:
                payment.status = Payment.Status.FAILED
                payment.save(update_fields=["status", "prontu_transaction_id", "raw_last_callback", "updated_at"])

        elif status_ == "expired":
            if payment.status != Payment.Status.SUCCESS:
                payment.status = Payment.Status.EXPIRED
                payment.save(update_fields=["status", "prontu_transaction_id", "raw_last_callback", "updated_at"])

    # IMPORTANTE: sempre responder 200
    return JsonResponse({"ok": True}, status=200)
