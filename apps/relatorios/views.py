from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse, Http404
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
        # Se veio ID, só Secretaria/Coordenação pode acessar
        if not (issecretaria(request.user) or request.user.profile.tipo == 'coordenacao'):
            messages.error(request, "Sem permissão.")
            return None
        return get_object_or_404(Aluno, pk=aluno_id)
    else:
        # Se não veio ID, é o próprio aluno
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
    
    # Permissão: Dono do doc ou Staff
    is_dono = (hasattr(request.user, 'aluno') and doc.aluno == request.user.aluno)
    is_staff = (issecretaria(request.user) or request.user.profile.tipo == 'coordenacao')
    
    if not (is_dono or is_staff):
        raise Http404("Acesso negado.")
        
    return FileResponse(doc.arquivo.open(), as_attachment=True, filename=doc.nome_arquivo_original)

# ==========================================
# Relatórios de Turma (Professor)
# ==========================================

@login_required
def baixar_relatorio_turma(request, turma_id):
    """Gera lista de alunos da turma (apenas memória, não salva histórico)"""
    if not request.user.profile.tipo in ['professor', 'coordenacao', 'secretaria']:
        messages.error(request, "Sem permissão.")
        return redirect('home')

    turma = get_object_or_404(Turma, id=turma_id)
    alunos = turma.alunos.all().select_related('user')
    
    pdf_buffer = gerar_pdf_relatorio_turma(turma.nome, alunos)
    filename = f"Turma_{turma.nome}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)