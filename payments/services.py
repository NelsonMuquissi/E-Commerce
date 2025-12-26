from django.db import transaction
from orders.models import Order
from .models import Payment

@transaction.atomic
def create_payment(user, order_id: int, provider: str = "manual") -> Payment:
    order = Order.objects.select_for_update().get(id=order_id, user=user)

    if order.status != Order.Status.CREATED:
        raise ValueError("Só é possível pagar pedidos no estado CREATED.")

    payment, _ = Payment.objects.get_or_create(order=order)
    payment.status = Payment.Status.PENDING
    payment.provider = provider
    payment.save()

    return payment


@transaction.atomic
def confirm_payment(payment_id: int) -> Payment:
    payment = Payment.objects.select_for_update().select_related("order").get(id=payment_id)

    if payment.status == Payment.Status.SUCCESS:
        return payment  # idempotente

    payment.status = Payment.Status.SUCCESS
    payment.reference = payment.reference or f"CONF-{payment.id}"
    payment.save(update_fields=["status", "reference"])

    order = payment.order
    order.status = Order.Status.PAID
    order.save(update_fields=["status"])

    return payment


@transaction.atomic
def fail_payment(payment_id: int) -> Payment:
    payment = Payment.objects.select_for_update().select_related("order").get(id=payment_id)

    payment.status = Payment.Status.FAILED
    payment.save(update_fields=["status"])

    return payment
