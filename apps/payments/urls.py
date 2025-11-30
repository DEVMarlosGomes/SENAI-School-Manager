from django.urls import path
from . import views

urlpatterns = [
    # Rota para o Aluno pagar (Checkout do Stripe)
    path('iniciar/<int:pagamento_id>/', views.iniciar_pagamento, name='iniciar_pagamento'),
    
    # Rota para a Secretaria criar a cobrança (Usada no Modal)
    path('criar/', views.criar_pagamento, name='criar_pagamento'),
    
    # Rotas de Retorno do Stripe
    path('sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('cancelado/', views.pagamento_cancelado, name='pagamento_cancelado'),
    
    # Webhook
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]