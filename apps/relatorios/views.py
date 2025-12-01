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
from decimal import Decimal
from django.db.models import Avg, Sum

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
    """Gera relatório geral do professor."""
    from .pdf_service import GeradorPDFSENAI

    gerador = GeradorPDFSENAI()
    pdf_buffer = gerador.gerar_relatorio_professor(request.user)
    filename = "Relatorio_Atividades_Docente.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

@login_required
def relatorio_secretaria_geral_pdf(request):
    """Gera relatório geral da secretaria."""
    from .pdf_service import GeradorPDFSENAI

    gerador = GeradorPDFSENAI()
    pdf_buffer = gerador.gerar_relatorio_secretaria(request.user)
    filename = "Relatorio_Secretaria.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)


# Previews de Relatórios (em HTML para visualização antes de download)
@login_required
def preview_relatorio_aluno(request, aluno_id=None):
    """Prévia do relatório do aluno em HTML."""
    aluno = _get_aluno_or_403(request, aluno_id)
    if not aluno:
        return redirect('home')
    
    from apps.academico.models import Historico, RegistroOcorrencia
    from apps.payments.models import Pagamento
    from apps.relatorios.models import DocumentoEmitido
    
    historicos = aluno.historico.select_related('turma_disciplina_professor__disciplina').all()
    media_geral = historicos.aggregate(avg=Avg('media_final'))['avg'] or 0
    faltas_total = historicos.aggregate(total=Sum('total_faltas'))['total'] or 0
    
    pagamentos = Pagamento.objects.filter(aluno=aluno.user).order_by('-data_criacao')
    total_pendente = Decimal('0.00')
    total_recebido = Decimal('0.00')
    for p in pagamentos.filter(status='pendente'):
        total_pendente += (p.valor or Decimal('0.00'))
    for p in pagamentos.filter(status='pago'):
        total_recebido += (p.valor or Decimal('0.00'))
    
    docs = DocumentoEmitido.objects.filter(aluno=aluno).order_by('-data_emissao')
    ocorrencias = RegistroOcorrencia.objects.filter(aluno=aluno).order_by('-data_registro')[:5]
    
    context = {
        'aluno': aluno,
        'historicos': historicos,
        'media_geral': media_geral,
        'faltas_total': faltas_total,
        'total_recebido': total_recebido,
        'total_pendente': total_pendente,
        'pagamentos_count': pagamentos.count(),
        'docs': docs,
        'ocorrencias': ocorrencias,
    }
    return render(request, 'relatorios/preview_aluno.html', context)

@login_required
def preview_relatorio_coordenacao(request, user_id):
    """Prévia do relatório de coordenação em HTML."""
    from apps.academico.models import Aluno, Turma, Professor, Curso, Historico
    
    total_alunos = Aluno.objects.count()
    total_alunos_ativos = Aluno.objects.filter(status_matricula__iexact='Ativo').count()
    total_turmas = Turma.objects.count()
    total_professores = Professor.objects.count()
    
    historicos_agg = Historico.objects.filter(id_aluno__status_matricula__iexact='Ativo').values('id_aluno').annotate(
        avg_media=Avg('media_final'), avg_freq=Avg('frequencia_percentual')
    )
    alunos_com_historico = historicos_agg.count()
    alunos_risco = sum(1 for h in historicos_agg if (h.get('avg_media') is not None and h.get('avg_media') < 5) or (h.get('avg_freq') is not None and h.get('avg_freq') < 75))
    
    cursos = Curso.objects.all()
    cursos_data = []
    for c in cursos:
        historicos_curso = Historico.objects.filter(turma_disciplina_professor__turma__id_curso=c)
        alunos_distintos = historicos_curso.values_list('id_aluno', flat=True).distinct().count()
        aprovados = historicos_curso.filter(status_aprovacao__iexact='Aprovado').values_list('id_aluno', flat=True).distinct().count()
        recuperacao = historicos_curso.filter(status_aprovacao__iexact='Recuperação').values_list('id_aluno', flat=True).distinct().count()
        reprovados = historicos_curso.filter(status_aprovacao__iexact='Reprovado').values_list('id_aluno', flat=True).distinct().count()
        cursos_data.append({
            'nome': c.nome_curso,
            'aprovados': aprovados,
            'recuperacao': recuperacao,
            'reprovados': reprovados,
            'total': alunos_distintos
        })
    
    context = {
        'total_alunos': total_alunos,
        'total_alunos_ativos': total_alunos_ativos,
        'total_turmas': total_turmas,
        'total_professores': total_professores,
        'alunos_com_historico': alunos_com_historico,
        'alunos_risco': alunos_risco,
        'cursos': cursos_data,
        'user_id': user_id,
    }
    return render(request, 'relatorios/preview_coordenacao.html', context)

@login_required
def preview_relatorio_professor(request):
    """Prévia do relatório do professor em HTML."""
    from apps.academico.models import TurmaDisciplinaProfessor, Historico, Professor
    
    try:
        professor = Professor.objects.get(user=request.user)
        formacao = professor.formacao
        reg_funcional = professor.registro_funcional
    except:
        formacao = 'N/A'
        reg_funcional = 'N/A'
    
    alocacoes = TurmaDisciplinaProfessor.objects.filter(professor__user=request.user)
    historicos = Historico.objects.filter(turma_disciplina_professor__professor__user=request.user)
    
    turmas_desemp = []
    for turma_info in historicos.values('turma_disciplina_professor__turma').distinct():
        turma = turma_info['turma_disciplina_professor__turma']
        hist_turma = historicos.filter(turma_disciplina_professor__turma=turma)
        total = hist_turma.values_list('id_aluno', flat=True).distinct().count()
        media = hist_turma.aggregate(m=Avg('media_final'))['m'] or 0
        freq = hist_turma.aggregate(f=Avg('frequencia_percentual'))['f'] or 0
        aprovados = hist_turma.filter(status_aprovacao__iexact='Aprovado').values_list('id_aluno', flat=True).distinct().count()
        turmas_desemp.append({
            'nome': hist_turma.first().turma_disciplina_professor.turma.nome,
            'total': total,
            'media': media,
            'freq': freq,
            'aprovados': aprovados
        })
    
    context = {
        'formacao': formacao,
        'reg_funcional': reg_funcional,
        'alocacoes': alocacoes,
        'turmas_desemp': turmas_desemp,
    }
    return render(request, 'relatorios/preview_professor.html', context)

@login_required
def preview_relatorio_secretaria(request):
    """Prévia do relatório da secretaria em HTML."""
    from apps.academico.models import Aluno, Turma, Curso, Historico
    from apps.payments.models import Pagamento
    
    total_alunos = Aluno.objects.count()
    total_ativos = Aluno.objects.filter(status_matricula__iexact='Ativo').count()
    total_inativos = total_alunos - total_ativos
    total_turmas = Turma.objects.count()
    total_cursos = Curso.objects.count()
    
    pagamentos_total = Pagamento.objects.aggregate(t=Sum('valor'))['t'] or Decimal('0.00')
    pagamentos_pago = Pagamento.objects.filter(status='pago').aggregate(t=Sum('valor'))['t'] or Decimal('0.00')
    pagamentos_pendente = pagamentos_total - pagamentos_pago
    taxa_receb = (pagamentos_pago/pagamentos_total*100) if pagamentos_total > 0 else 0
    
    cursos_data = []
    for c in Curso.objects.all():
        alunos_curso = Aluno.objects.filter(turma_atual__id_curso=c).count()
        turmas_curso = Turma.objects.filter(id_curso=c).count()
        cursos_data.append({
            'nome': c.nome_curso,
            'alunos': alunos_curso,
            'turmas': turmas_curso,
            'status': 'Ativo' if c.credenciamento_ativo else 'Inativo'
        })
    
    context = {
        'total_alunos': total_alunos,
        'total_ativos': total_ativos,
        'total_inativos': total_inativos,
        'total_turmas': total_turmas,
        'total_cursos': total_cursos,
        'pagamentos_total': pagamentos_total,
        'pagamentos_pago': pagamentos_pago,
        'pagamentos_pendente': pagamentos_pendente,
        'taxa_recebimento': taxa_receb,
        'cursos': cursos_data,
    }
    return render(request, 'relatorios/preview_secretaria.html', context)