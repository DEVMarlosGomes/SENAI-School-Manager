# Script to generate coordinator report PDF and save to workspace
from apps.relatorios.pdf_service import GeradorPDFSENAI
from django.contrib.auth import get_user_model
User = get_user_model()

u = User.objects.first()
if not u:
    print('No user found to act as solicitante')
else:
    g = GeradorPDFSENAI()
    buf = g.gerar_relatorio_coordenacao(solicitante_user=u)
    out = 'Relatorio_Geral_Coordenacao.pdf'
    with open(out, 'wb') as f:
        f.write(buf.read())
    print('SAVED', out)
