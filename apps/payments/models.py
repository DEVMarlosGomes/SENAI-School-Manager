# payments/models.py
from django.db import models

class FinancialPayment(models.Model):
    local_id = models.CharField(max_length=80, blank=True, null=True)  # seu id interno
    asaas_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=40)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    raw_payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.local_id or self.id} - {self.asaas_id} - {self.status}"
