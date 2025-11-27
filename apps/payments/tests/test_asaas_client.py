import unittest
from unittest.mock import patch

from apps.payments.services import asaas_client


class MockResponse:
    def __init__(self, json_data=None, status_code=200):
        self._json = json_data or {}
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if not (200 <= self.status_code < 300):
            raise Exception(f"HTTP {self.status_code}")


class AsaasClientTests(unittest.TestCase):
    def setUp(self):
        # garantir que a chave exista durante os testes
        asaas_client.ASAAS_API_KEY = "testkey"
        asaas_client.HEADERS["access_token"] = "testkey"

    @patch("apps.payments.services.asaas_client.requests.post")
    def test_create_payment_success(self, mock_post):
        mock_post.return_value = MockResponse(json_data={"id": "abc123", "status": "PENDING"}, status_code=201)
        payload = {"customer": "cust1", "billingType": "BOLETO", "dueDate": "2025-12-31", "value": 100.0}
        resp = asaas_client.create_payment(payload)
        self.assertEqual(resp.get("id"), "abc123")
        self.assertEqual(resp.get("status"), "PENDING")
        mock_post.assert_called_once()

    @patch("apps.payments.services.asaas_client.requests.get")
    def test_get_payment_success(self, mock_get):
        mock_get.return_value = MockResponse(json_data={"id": "abc123", "status": "CONFIRMED"}, status_code=200)
        resp = asaas_client.get_payment("abc123")
        self.assertEqual(resp.get("status"), "CONFIRMED")
        mock_get.assert_called_once()

    def test_ensure_api_key_raises_when_missing(self):
        # guardar e limpar
        old = asaas_client.ASAAS_API_KEY
        asaas_client.ASAAS_API_KEY = None
        try:
            with self.assertRaises(RuntimeError):
                asaas_client._ensure_api_key()
        finally:
            asaas_client.ASAAS_API_KEY = old


if __name__ == "__main__":
    unittest.main()
