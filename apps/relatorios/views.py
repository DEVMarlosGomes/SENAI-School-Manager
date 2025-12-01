from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.academico.models import Aluno, Turma
from apps.dashboards.views import issecretaria
from .models import DocumentoEmitido
from .services import DocumentoService
from .pdf_service import gerar_pdf_relatorio_turma
from datetime import datetime

# ==========================================
# Emissão de Documentos (Gera e Salva)
# ==========================================

@login_required
def emitir_boletim(request, aluno_id=None):
    """Emite boletim (Aluno para si mesmo ou Secretaria para Aluno)"""
    aluno = _get_aluno_or_403(request, aluno_id)
    if not aluno: return redirect('home')

    try:
        documento = DocumentoService.emitir_novo_documento(
            aluno=aluno, tipo_documento='BOLETIM', solicitante=request.user
        )
        return redirect('download_documento', documento_id=documento.id)
    except Exception as e:
        messages.error(request, f"Erro: {str(e)}")
        return redirect('home')

@login_required
def emitir_declaracao_matricula(request, aluno_id=None):
    """Emite declaração de matrícula"""
    aluno = _get_aluno_or_403(request, aluno_id)
    if not aluno: return redirect('home')

    try:
        documento = DocumentoService.emitir_novo_documento(
            aluno=aluno, tipo_documento='DECLARACAO', solicitante=request.user
        )
        return redirect('download_documento', documento_id=documento.id)
    except Exception as e:
        messages.error(request, f"Erro: {str(e)}")
        return redirect('home')

def _get_aluno_or_403(request, aluno_id):
    """Helper para verificar permissão e retornar o aluno correto"""
    if aluno_id:
        if not (issecretaria(request.user) or request.user.profile.tipo == 'coordenacao'):
            messages.error(request, "Sem permissão.")
            return None
        return get_object_or_404(Aluno, pk=aluno_id)
    else:
        if not hasattr(request.user, 'aluno'):
            messages.error(request, "Perfil de aluno não encontrado.")
            return None
        return request.user.aluno

# ==========================================
# Download de Documentos (Arquivo Salvo)
# ==========================================

@login_required
def download_documento(request, documento_id):
    """Baixa um documento já gerado anteriormente"""
    doc = get_object_or_404(DocumentoEmitido, id=documento_id)
    
    is_dono = (hasattr(request.user, 'aluno') and doc.aluno == request.user.aluno)
    is_staff = (issecretaria(request.user) or request.user.profile.tipo == 'coordenacao')
    
    if not (is_dono or is_staff):
        raise Http404("Acesso negado.")
        
    return FileResponse(doc.arquivo.open(), as_attachment=True, filename=doc.nome_arquivo_original)

# ==========================================
# Relatórios Dinâmicos (Gera na hora)
# ==========================================

@login_required
def baixar_relatorio_turma(request, turma_id):
    """Gera lista de alunos da turma"""
    if not request.user.profile.tipo in ['professor', 'coordenacao', 'secretaria']:
        messages.error(request, "Sem permissão.")
        return redirect('home')

    turma = get_object_or_404(Turma, id=turma_id)
    alunos = turma.alunos.all().select_related('user')
    
    pdf_buffer = gerar_pdf_relatorio_turma(turma.nome, alunos)
    filename = f"Turma_{turma.nome}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

@login_required
def relatorio_coordenacao_pdf(request, user_id):
    """Gera relatório geral da coordenação (Correção de Erro de Rota)"""
    # Usar o gerador centralizado para relatório de coordenação
    from .pdf_service import GeradorPDFSENAI

    gerador = GeradorPDFSENAI()
    pdf_buffer = gerador.gerar_relatorio_coordenacao(solicitante_user=request.user)
    filename = "Relatorio_Geral_Coordenacao.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)


@login_required
def relatorio_aluno_geral_pdf(request, aluno_id=None):
    """Gera relatório completo do aluno (acadêmico, financeiro, documentos, ocorrências)."""
    aluno = _get_aluno_or_403(request, aluno_id)
    if not aluno:
        return redirect('home')

    from .pdf_service import GeradorPDFSENAI

    gerador = GeradorPDFSENAI()
    pdf_buffer = gerador.gerar_relatorio_geral_aluno(aluno)
    filename = f"Relatorio_Geral_Aluno_{getattr(aluno, 'RA_aluno', aluno.user.id)}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

@login_required
def relatorio_professor_geral_pdf(request):
    """Gera relatório geral do professor"""
    from reportlab.pdfgen import canvas
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatorio_Atividades_Docente.pdf"'
    
    p = canvas.Canvas(response)
    p.drawString(100, 800, "RELATÓRIO DE ATIVIDADES DOCENTES")
    p.drawString(100, 780, f"Professor: {request.user.get_full_name()}")
    p.drawString(100, 760, f"Data: {datetime.now().strftime('%d/%m/%Y')}")
    p.showPage()
    p.save()
    return response

@login_required
def relatorio_secretaria_geral_pdf(request):
    """Gera relatório geral da secretaria"""
    from reportlab.pdfgen import canvas
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Relatorio_Secretaria.pdf"'
    
    p = canvas.Canvas(response)
    p.drawString(100, 800, "RELATÓRIO DE GESTÃO - SECRETARIA ACADÊMICA")
    p.drawString(100, 780, f"Emitido por: {request.user.get_full_name()}")
    p.showPage()
    p.save()
    return response