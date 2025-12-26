from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "order",
            "provider",
            "status",

            # Prontu
            "prontu_checkout_id",
            "prontu_url",
            "prontu_reference_id",
            "prontu_entity_id",
            "prontu_transaction_id",

            "created_at",
            "updated_at",
        ]
