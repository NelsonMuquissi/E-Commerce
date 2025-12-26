import pytest

@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        email="test@example.com",
        password="1234"
    )
