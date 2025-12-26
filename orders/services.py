from decimal import Decimal
from django.db import transaction
from cart.models import Cart
from .models import Order, OrderItem



@transaction.atomic
def create_order_from_cart(user) -> Order:
    cart = (
        Cart.objects
        .select_for_update()
        .prefetch_related("items__product")
        .get(user=user, is_active=True)
    )

    if not cart.items.exists():
        raise ValueError("Carrinho vazio.")

    order = Order.objects.create(user=user, total=Decimal("0"))
    total = Decimal("0")

    for item in cart.items.all():
        product = item.product

        if not product.is_active:
            raise ValueError(f"Produto inativo: {product.name}")

        if product.stock < item.quantity:
            raise ValueError(f"Sem stock para {product.name}")

        OrderItem.objects.create(
            order=order,
            product=product,
            price=product.price,   # congela preço no pedido
            quantity=item.quantity
        )

        product.stock -= item.quantity
        product.save(update_fields=["stock"])

        total += product.price * item.quantity

    order.total = total
    order.save(update_fields=["total"])

    cart.is_active = False
    cart.save(update_fields=["is_active"])

    return order


@transaction.atomic
def cancel_order(user, order_id: int) -> Order:
    order = (
        Order.objects
        .select_for_update()
        .prefetch_related("items__product")
        .get(id=order_id, user=user)
    )

    if order.status != Order.Status.CREATED:
        raise ValueError("Só é possível cancelar pedidos no estado CREATED.")

    # devolve stock
    for item in order.items.all():
        product = item.product
        product.stock += item.quantity
        product.save(update_fields=["stock"])

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status"])

    return order