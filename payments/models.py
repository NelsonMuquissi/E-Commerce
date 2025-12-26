from django.db import models
from orders.models import Order

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
        EXPIRED = "EXPIRED"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=50, default="prontu")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    # Prontu
    prontu_checkout_id = models.CharField(max_length=80, blank=True)  # response "id"
    prontu_url = models.URLField(blank=True)                          # data.url
    prontu_reference_id = models.CharField(max_length=80, blank=True) # data.reference_id
    prontu_entity_id = models.CharField(max_length=80, blank=True)    # data.entity_id
    prontu_transaction_id = models.CharField(max_length=80, blank=True) # callback: prontu_transaction_id

    raw_last_callback = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
