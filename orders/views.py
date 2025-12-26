from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .serializers import OrderSerializer
from .services import create_order_from_cart, cancel_order

from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.services_prontu import start_prontu_payment

from orders.models import Order


class MyOrdersViewSet(ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        qs = request.user.orders.prefetch_related("items__product").order_by("-id")
        return Response(OrderSerializer(qs, many=True).data)

    def create(self, request):
        try:
            order = create_order_from_cart(request.user)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        try:
            order = cancel_order(request.user, int(pk))
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        try:
            payment = start_prontu_payment(request.user, int(pk))
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {
                "payment": PaymentSerializer(payment).data,
                "checkout_url": payment.prontu_url,
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="payment")
    def payment(self, request, pk=None):
        # Como é ViewSet, buscamos direto no ORM (sem get_queryset)
        order = Order.objects.filter(id=pk, user=request.user).first()
        if not order:
            return Response({"detail": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        payment = Payment.objects.filter(order=order).first()
        if not payment:
            return Response({"detail": "Pagamento ainda não iniciado."}, status=status.HTTP_404_NOT_FOUND)

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)
