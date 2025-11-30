# apps/payments/views.py
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from apps.dashboards.views import issecretaria
from .models import Pagamento
from .services.stripe_service import StripeService
import stripe

@login_required
def iniciar_pagamento(request, pagamento_id):
    """
    Busca o pagamento no banco e redireciona o usuário para o Stripe.
    """
    pagamento = get_object_or_404(Pagamento, id=pagamento_id, aluno=request.user)
    
    # Define o domínio atual (em produção, isso deve ser ajustado)
    domain_url = f"{request.scheme}://{request.get_host()}"
    
    session_id, session_url = StripeService.criar_sessao_checkout(
        pagamento_id=pagamento.id,
        valor_decimal=pagamento.valor,
        descricao=pagamento.descricao,
        email_usuario=request.user.email,
        domain_url=domain_url
    )

    if session_url:
        # Salva o ID da sessão para referência futura
        pagamento.stripe_checkout_id = session_id
        pagamento.save()
        return redirect(session_url)
    else:
        return render(request, 'pagamentos/erro.html', {'message': 'Erro ao conectar com Stripe'})

@login_required
def pagamento_sucesso(request):
    return render(request, 'pagamentos/sucesso.html')

@login_required
def pagamento_cancelado(request):
    return render(request, 'pagamentos/cancelado.html')

@csrf_exempt
def stripe_webhook(request):
    """
    Recebe avisos do Stripe quando um pagamento é confirmado.
    Atualiza o status no banco de dados automaticamente.
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400) # Payload inválido
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400) # Assinatura inválida

    # Verifica se o evento é de sessão completada
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Recupera o ID do pagamento que enviamos nos metadados
        pagamento_id = session.get('metadata', {}).get('pagamento_id')
        
        if pagamento_id:
            try:
                pagamento = Pagamento.objects.get(id=pagamento_id)
                pagamento.status = 'pago'
                pagamento.stripe_payment_intent = session.get('payment_intent')
                pagamento.save()
                print(f"Pagamento {pagamento_id} confirmado!")
            except Pagamento.DoesNotExist:
                pass

    return HttpResponse(status=200)

@login_required
@require_POST
def criar_pagamento(request):
    """
    Endpoint para a Secretaria criar uma nova cobrança manualmente.
    Recebe JSON: { 'aluno_id': 1, 'descricao': '...', 'valor': '100.00', 'vencimento': '...' }
    """
    # 1. Segurança: Só secretaria pode criar
    if not issecretaria(request.user):
        return JsonResponse({'success': False, 'error': 'Acesso negado.'}, status=403)

    try:
        data = json.loads(request.body)
        
        # 2. Validação básica
        aluno_id = data.get('aluno_id')
        valor = data.get('valor')
        descricao = data.get('descricao')
        
        if not all([aluno_id, valor, descricao]):
            return JsonResponse({'success': False, 'error': 'Todos os campos são obrigatórios.'})

        aluno = User.objects.get(pk=aluno_id)
        
        # 3. Cria o pagamento no banco (Status Pendente)
        novo_pagamento = Pagamento.objects.create(
            aluno=aluno,
            descricao=descricao,
            valor=valor,
            status='pendente'
            # Se tiver campo 'data_vencimento' no model, adicione aqui:
            # data_vencimento=data.get('vencimento')
        )
        
        return JsonResponse({'success': True, 'message': 'Cobrança gerada com sucesso!'})

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Aluno não encontrado.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})