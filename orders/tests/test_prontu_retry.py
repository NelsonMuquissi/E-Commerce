import pytest
from orders.models import Order
from payments.models import Payment
from payments.services_prontu import start_prontu_payment

@pytest.mark.django_db
def test_retry_pay_allows_failed_payment(user, monkeypatch):
    order = Order.objects.create(user=user, status=Order.Status.CREATED, total=1000)
    payment = Payment.objects.create(order=order, provider="prontu", status=Payment.Status.FAILED)

    # mock do client pra não chamar API real
    class FakeClient:
        def get_token(self): return "tok"
        def create_standard_checkout(self, token, payload):
            return {"id": "chk_1", "data": {"url": "https://pay.test/?id=chk_1", "reference_id": str(order.id), "entity_id": "ent_1"}}

    monkeypatch.setattr("payments.services_prontu.ProntuClient", FakeClient)

    p2 = start_prontu_payment(user, order.id)
    assert p2.id == payment.id
    assert p2.prontu_checkout_id == "chk_1"
    assert p2.prontu_url.startswith("https://pay.test")
