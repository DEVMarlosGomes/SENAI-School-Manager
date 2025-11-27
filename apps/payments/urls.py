# payments/urls.py
from django.urls import path
from .views import create_payment_view, asaas_webhook

urlpatterns = [
    path('create/', create_payment_view, name='create_payment'),
    path('webhook/asaas/', asaas_webhook, name='asaas_webhook'),
]
