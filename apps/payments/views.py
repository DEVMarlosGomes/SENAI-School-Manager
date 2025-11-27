# payments/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .services.asaas_client import create_payment
from .models import FinancialPayment

@api_view(['POST'])
def create_payment_view(request):
    """
    Espera body JSON com:
    { "local_id": "123", "customer": "<asaasCustomerId>", "dueDate":"YYYY-MM-DD", "value": 100.0, "description":"..." }
    """
    data = request.data
    payload = {
        "customer": data.get("customer"),
        "billingType": data.get("billingType", "BOLETO"),
        "dueDate": data.get("dueDate"),
        "value": data.get("value"),
        "description": data.get("description", "")
    }
    # validação simples
    if not payload.get("customer") or not payload.get("dueDate") or not payload.get("value"):
        return Response({"detail": "customer, dueDate and value are required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        resp = create_payment(payload)
    except Exception as e:
        # já logado no client, apenas retornar erro apropriado
        return Response({"detail": "Error creating payment with Asaas", "error": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    # salvar no DB
    asaas_id = resp.get("id")
    payment_status = resp.get("status")
    fp = FinancialPayment.objects.create(
        local_id=data.get("local_id"),
        asaas_id=asaas_id,
        amount=data.get("value"),
        status=payment_status,
        due_date=data.get("dueDate"),
        raw_payload=resp
    )
    return Response({"asaas_id": asaas_id, "status": payment_status})

# payments/views.py (append)
from django.views.decorators.csrf import csrf_exempt
import os
from django.http import HttpResponse
from django.utils import timezone

@csrf_exempt
def asaas_webhook(request):
    # validar token enviado pelo Asaas no header 'asaas-access-token'
    webhook_token = os.getenv("ASAAS_WEBHOOK_TOKEN")
    header_token = request.headers.get("asaas-access-token") or request.META.get("HTTP_ASAAS_ACCESS_TOKEN")
    if not webhook_token or header_token != webhook_token:
        return HttpResponse(status=401)

    import json
    payload = json.loads(request.body.decode('utf-8'))

    # Exemplo: payload tem 'event' e 'payment'
    event = payload.get("event")
    payment = payload.get("payment") or {}
    asaas_id = payment.get("id")

    if asaas_id:
        try:
            fp = FinancialPayment.objects.get(asaas_id=asaas_id)
            fp.status = payment.get("status", fp.status)
            paid_date = payment.get("dateCreated") or payment.get("paymentDate")
            # se houver paid date, parse -> set paid_date
            fp.raw_payload = payment
            fp.save()
        except FinancialPayment.DoesNotExist:
            # opcional: criar registro se não existir
            FinancialPayment.objects.create(
                local_id=None,
                asaas_id=asaas_id,
                amount=payment.get("value") or 0,
                status=payment.get("status"),
                raw_payload=payment
            )

    return HttpResponse(status=200)
