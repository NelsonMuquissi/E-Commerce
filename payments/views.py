from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from .serializers import PaymentSerializer
from .services import create_payment, confirm_payment, fail_payment
from .models import Payment


class MyOrderPaymentViewSet(ViewSet):
    #permission_classes = [IsAuthenticated]
    permission_classes = [IsAdminUser]

    @action(detail=True, methods=["post"], url_path="pay")
    def pay(self, request, pk=None):
        # pk = order_id
        provider = request.data.get("provider", "manual")
        try:
            payment = create_payment(request.user, int(pk), provider=provider)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({"detail": "Pedido não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentAdminActionsViewSet(ViewSet):
    """
    Stub de confirmação/falha (simula gateway).
    Em produção, isso viraria webhook do provedor.
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm(self, request, pk=None):
        try:
            payment = confirm_payment(int(pk))
        except Exception:
            return Response({"detail": "Pagamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)

    @action(detail=True, methods=["post"], url_path="fail")
    def fail(self, request, pk=None):
        try:
            payment = fail_payment(int(pk))
        except Exception:
            return Response({"detail": "Pagamento não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        return Response(PaymentSerializer(payment).data)
