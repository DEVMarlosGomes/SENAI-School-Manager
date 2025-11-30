# apps/payments/services/stripe_service.py
import stripe
from django.conf import settings
from django.urls import reverse

# Configura a chave secreta uma única vez
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    @staticmethod
    def criar_sessao_checkout(pagamento_id, valor_decimal, descricao, email_usuario, domain_url):
        """
        Cria uma sessão de checkout no Stripe.
        Retorna a URL para onde o usuário deve ser redirecionado.
        """
        try:
            # Converte valor para centavos (Stripe trabalha com inteiros)
            # Ex: 100.00 vira 10000
            valor_em_centavos = int(valor_decimal * 100)

            checkout_session = stripe.checkout.Session.create(
                customer_email=email_usuario,
                payment_method_types=['card'], # Adicione 'boleto' se tiver ativado no painel do Stripe
                line_items=[{
                    'price_data': {
                        'currency': 'brl',
                        'product_data': {
                            'name': descricao,
                        },
                        'unit_amount': valor_em_centavos,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                # URLs de retorno
                success_url=f"{domain_url}/pagamentos/sucesso?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{domain_url}/pagamentos/cancelado",
                # Metadados para identificar o pagamento depois no Webhook
                metadata={
                    'pagamento_id': pagamento_id,
                }
            )
            return checkout_session.id, checkout_session.url
            
        except Exception as e:
            print(f"Erro ao criar sessão Stripe: {e}")
            return None, None