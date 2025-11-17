import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def consultar_cep(request):
    """
    View para consultar CEP via API ViaCEP
    Retorna os dados do endereço em formato JSON
    """
    cep = request.GET.get('cep', '')
    
    # Remove caracteres não numéricos do CEP
    cep = ''.join(filter(str.isdigit, cep))
    
    # Valida se o CEP tem 8 dígitos
    if len(cep) != 8:
        return JsonResponse({
            'erro': True,
            'mensagem': 'CEP inválido. Digite 8 dígitos.'
        }, status=400)
    
    try:
        # Faz a requisição para o ViaCEP
        url = f'https://viacep.com.br/ws/{cep}/json/'
        resposta = requests.get(url, timeout=5)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Verifica se o CEP foi encontrado
            if 'erro' in dados:
                return JsonResponse({
                    'erro': True,
                    'mensagem': 'CEP não encontrado.'
                }, status=404)
            
            # Retorna os dados do endereço
            return JsonResponse({
                'erro': False,
                'logradouro': dados.get('logradouro', ''),
                'complemento': dados.get('complemento', ''),
                'bairro': dados.get('bairro', ''),
                'cidade': dados.get('localidade', ''),
                'estado': dados.get('uf', ''),
                'cep': dados.get('cep', '')
            })
        else:
            return JsonResponse({
                'erro': True,
                'mensagem': 'Erro ao consultar CEP.'
            }, status=500)
            
    except requests.exceptions.Timeout:
        return JsonResponse({
            'erro': True,
            'mensagem': 'Tempo de consulta excedido. Tente novamente.'
        }, status=408)
    except Exception as e:
        return JsonResponse({
            'erro': True,
            'mensagem': f'Erro inesperado: {str(e)}'
        }, status=500)
