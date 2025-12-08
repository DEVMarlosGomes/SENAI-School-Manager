import os
from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.payments'
    # Esta linha corrige o erro "multiple filesystem locations"
    path = os.path.dirname(os.path.abspath(__file__))