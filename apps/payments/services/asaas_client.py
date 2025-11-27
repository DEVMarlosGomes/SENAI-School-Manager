# payments/services/asaas_client.py
import os
import logging
import requests

logger = logging.getLogger(__name__)

ASAAS_BASE_URL = os.getenv("ASAAS_BASE_URL", "https://api-sandbox.asaas.com/v3")
# Espera-se que a chave esteja em uma variável de ambiente chamada ASAAS_API_KEY
ASAAS_API_KEY = os.getenv("ASAAS_API_KEY")

HEADERS = {
    "Content-Type": "application/json"
}
if ASAAS_API_KEY:
    HEADERS["access_token"] = ASAAS_API_KEY


def _ensure_api_key():
    if not ASAAS_API_KEY:
        raise RuntimeError("ASAAS_API_KEY environment variable is not set. Set it in your .env or environment.")


def create_payment(payload: dict) -> dict:
    """
    payload exemplo:
    {
      "customer": "<customerId>",
      "billingType": "BOLETO",
      "dueDate": "2025-12-31",
      "value": 100.0,
      "description": "Descrição"
    }
    """
    _ensure_api_key()
    url = f"{ASAAS_BASE_URL}/payments"
    try:
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.exception("Error creating Asaas payment: %s", e)
        # Propagar para a view lidar com o erro
        raise

def get_payment(asaas_id: str) -> dict:
    _ensure_api_key()
    url = f"{ASAAS_BASE_URL}/payments/{asaas_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.exception("Error fetching Asaas payment %s: %s", asaas_id, e)
        raise
