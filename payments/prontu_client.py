import os
import httpx

PRONTU_BASE_URL = "https://api.prontu.io"

class ProntuClient:
    def __init__(self):
        self.email = os.getenv("PRONTU_EMAIL")
        self.password = os.getenv("PRONTU_PASSWORD")
        self.env = int(os.getenv("PRONTU_ENV", "0"))

    def get_token(self) -> str:
        # /v1/merchants/get_token (POST) com email/password/env :contentReference[oaicite:4]{index=4}
        url = f"{PRONTU_BASE_URL}/v1/merchants/get_token"
        payload = {"email": self.email, "password": self.password, "env": self.env}

        with httpx.Client(timeout=30) as client:
            r = client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["token"]

    def create_standard_checkout(self, token: str, payload: dict) -> dict:
        # /v1/hosts/transactions-receive (POST) Authorization=token :contentReference[oaicite:5]{index=5}
        url = f"{PRONTU_BASE_URL}/v1/hosts/transactions-receive"
        headers = {"Authorization": token}

        with httpx.Client(timeout=30) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            return r.json()
