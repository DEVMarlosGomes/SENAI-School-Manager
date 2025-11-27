import json
from unittest.mock import patch

from rest_framework.test import APIRequestFactory, APITestCase

from apps.payments.views import create_payment_view


class PaymentViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

    @patch("apps.payments.views.create_payment")
    def test_create_payment_view_success(self, mock_create):
        mock_create.return_value = {"id": "asaas_1", "status": "PENDING"}
        data = {
            "local_id": "local123",
            "customer": "cust_1",
            "dueDate": "2025-12-31",
            "value": 150.0,
            "description": "Teste"
        }
        request = self.factory.post('/create/', data, format='json')
        response = create_payment_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('asaas_id', response.data)
        self.assertEqual(response.data['asaas_id'], 'asaas_1')

    @patch("apps.payments.views.create_payment")
    def test_create_payment_view_handles_client_error(self, mock_create):
        mock_create.side_effect = Exception("timeout")
        data = {
            "local_id": "local123",
            "customer": "cust_1",
            "dueDate": "2025-12-31",
            "value": 150.0,
            "description": "Teste"
        }
        request = self.factory.post('/create/', data, format='json')
        response = create_payment_view(request)
        # devolve 502 quando o client falha
        self.assertEqual(response.status_code, 502)
