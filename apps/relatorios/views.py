from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.db.models import Count
from apps.academico.models import (
    Aluno, Professor, Secretaria, Coordenacao, Historico, 
    Turma, TurmaDisciplinaProfessor, RegistroOcorrencia, Boletim, Responsavel
)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io

# =============================================================================
# ESTILOS GERAIS COMPARTILHADOS
# =============================================================================
def get_custom_styles():
    styles = getSampleStyleSheet()
    return {
        'Title': ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=20, textColor=colors.HexColor('#c41e3a'), spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Bold'),
        'Subtitle': ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#c41e3a'), spaceAfter=10, spaceBefore=15, fontName='Helvetica-Bold'),
        'Normal': ParagraphStyle('NormalSmall', parent=styles['Normal'], fontSize=9, alignment=TA_LEFT),
        'Footer': ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER),
    }

# =============================================================================
# RELATÓRIO DO ALUNO
# =============================================================================
@login_required
@require_GET
def relatorio_aluno_pdf(request, aluno_id):
    """Gera PDF do relatório completo e detalhado de um aluno"""
    
    try:
        aluno = Aluno.objects.select_related(
            'user', 'turma_atual', 'turma_atual__id_curso', 'responsavel_legal', 'cod_endereco'
        ).get(user_id=aluno_id)
    except Aluno.DoesNotExist:
        return HttpResponse("Aluno não encontrado.", status=404)
    
    if request.user != aluno.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elementos = []
    st = get_custom_styles()
    
    # CABEÇALHO
    elementos.append(Paragraph(f"DOSSIÊ DO ALUNO: {aluno.user.get_full_name().upper()}", st['Title']))
    elementos.append(Paragraph(f"RA: {aluno.RA_aluno} | Data de Emissão: {datetime.now().strftime('%d/%m/%Y')}", st['Normal']))
    elementos.append(Spacer(1, 0.2*inch))
    
    # 1. DADOS PESSOAIS E CONTATO
    elementos.append(Paragraph("1. Dados Pessoais e Endereço", st['Subtitle']))
    endereco_str = str(aluno.cod_endereco) if aluno.cod_endereco else "Endereço não cadastrado"
    
    dados_pessoais = [
        ['E-mail:', aluno.user.email or '-'],
        ['RG:', getattr(aluno, 'RG_aluno', '-')],
        ['Nascimento:', aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else '-'],
        ['Endereço:', endereco_str]
    ]
    t_pessoais = Table(dados_pessoais, colWidths=[1.5*inch, 5.5*inch])
    t_pessoais.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elementos.append(t_pessoais)
    
    # 2. RESPONSÁVEL LEGAL (Novo)
    if aluno.responsavel_legal:
        elementos.append(Paragraph("2. Responsável Legal", st['Subtitle']))
        resp = aluno.responsavel_legal
        dados_resp = [
            ['Nome:', resp.nome_completo_responsavel],
            ['Parentesco:', resp.parentesco or '-'],
            ['Contato:', resp.contato_principal or '-'],
            ['CPF:', resp.cpf]
        ]
        t_resp = Table(dados_resp, colWidths=[1.5*inch, 5.5*inch])
        t_resp.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        elementos.append(t_resp)

    # 3. SITUAÇÃO ACADÊMICA ATUAL
    elementos.append(Paragraph("3. Matrícula Atual", st['Subtitle']))
    curso = aluno.turma_atual.id_curso.nome_curso if aluno.turma_atual and aluno.turma_atual.id_curso else "Não matriculado"
    turma = aluno.turma_atual.nome if aluno.turma_atual else "-"
    
    dados_matr = [
        ['Curso:', curso, 'Turma:', turma],
        ['Status:', aluno.status_matricula, 'Data Matrícula:', aluno.data_matricula.strftime('%d/%m/%Y')]
    ]
    t_matr = Table(dados_matr, colWidths=[1*inch, 2.5*inch, 1*inch, 2.5*inch])
    t_matr.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.aliceblue),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elementos.append(t_matr)
    
    # 4. HISTÓRICO DE NOTAS E FREQUÊNCIA (Melhorado)
    elementos.append(Paragraph("4. Desempenho Disciplinar (Histórico)", st['Subtitle']))
    historicos = Historico.objects.filter(id_aluno=aluno).select_related('turma_disciplina_professor__disciplina').order_by('-periodo_realizacao')
    
    if historicos.exists():
        dados_hist = [['Período', 'Disciplina', 'Média Final', 'Freq. (%)', 'Situação']]
        for h in historicos:
            disc = h.turma_disciplina_professor.disciplina.nome
            media = f"{h.media_final:.1f}" if h.media_final is not None else "-"
            freq = f"{h.frequencia_percentual:.0f}%" if h.frequencia_percentual is not None else "-"
            sit = h.status_aprovacao or "Cursando"
            
            # Cor da linha baseada na situação
            bg_color = colors.white
            if sit == 'Reprovado': bg_color = colors.mistyrose
            elif sit == 'Aprovado': bg_color = colors.honeydew
            
            dados_hist.append([h.periodo_realizacao, disc[:35], media, freq, sit])
            
        t_hist = Table(dados_hist, colWidths=[1*inch, 3*inch, 1*inch, 1*inch, 1*inch])
        t_hist.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_hist)
    else:
        elementos.append(Paragraph("Nenhum registro de histórico encontrado.", st['Normal']))

    # 5. OCORRÊNCIAS DISCIPLINARES (Novo)
    elementos.append(Paragraph("5. Registro de Ocorrências", st['Subtitle']))
    ocorrencias = RegistroOcorrencia.objects.filter(aluno=aluno).order_by('-data_registro')
    
    if ocorrencias.exists():
        dados_oc = [['Data', 'Tipo', 'Descrição Resumida']]
        for o in ocorrencias:
            desc = (o.descricao[:50] + '...') if len(o.descricao) > 50 else o.descricao
            dados_oc.append([o.data_registro.strftime('%d/%m/%Y'), o.tipo_ocorrencia, desc])
        
        t_oc = Table(dados_oc, colWidths=[1.5*inch, 1.5*inch, 4*inch])
        t_oc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_oc)
    else:
        elementos.append(Paragraph("Nenhuma ocorrência registrada.", st['Normal']))

    elementos.append(Spacer(1, 0.5*inch))
    elementos.append(Paragraph("Documento gerado eletronicamente pelo SENAI School Manager.", st['Footer']))
    
    pdf.build(elementos)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="dossie_aluno_{aluno.user.username}.pdf"'
    return response

# =============================================================================
# RELATÓRIO DO PROFESSOR
# =============================================================================
@login_required
@require_GET
def relatorio_professor_pdf(request, professor_id):
    """Gera PDF detalhado do professor"""
    
    try:
        professor = Professor.objects.select_related('user', 'cod_departamento').get(user_id=professor_id)
    except Professor.DoesNotExist:
        return HttpResponse("Professor não encontrado.", status=404)
    
    if request.user != professor.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elementos = []
    st = get_custom_styles()
    
    elementos.append(Paragraph(f"RELATÓRIO DOCENTE: {professor.user.get_full_name().upper()}", st['Title']))
    elementos.append(Paragraph(f"Registro Funcional: {professor.registro_funcional} | Data: {datetime.now().strftime('%d/%m/%Y')}", st['Normal']))
    elementos.append(Spacer(1, 0.2*inch))
    
    # 1. DADOS CONTRATUAIS
    elementos.append(Paragraph("1. Dados Contratuais e Lotação", st['Subtitle']))
    dados_prof = [
        ['Departamento:', professor.cod_departamento.nome_departamento if professor.cod_departamento else 'Não alocado'],
        ['Formação:', professor.formacao],
        ['Vínculo:', professor.tipo_vinculo],
        ['Admissão:', professor.data_contratacao.strftime('%d/%m/%Y')],
        ['Status:', professor.status_professor]
    ]
    t_prof = Table(dados_prof, colWidths=[2*inch, 5*inch])
    t_prof.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elementos.append(t_prof)
    
    # 2. CARGA HORÁRIA E TURMAS
    elementos.append(Paragraph("2. Atribuição de Aulas (Turmas Ativas)", st['Subtitle']))
    
    # Buscando turmas onde o professor leciona
    alocacoes = TurmaDisciplinaProfessor.objects.filter(professor=professor).select_related('turma', 'disciplina', 'turma__id_curso')
    
    if alocacoes.exists():
        dados_turmas = [['Disciplina', 'Turma / Curso', 'Turno', 'Alunos', 'Status']]
        for aloc in alocacoes:
            disc = aloc.disciplina.nome
            turma_curso = f"{aloc.turma.nome}\n({aloc.turma.id_curso.nome_curso[:20]}...)"
            turno = aloc.turma.id_curso.turno
            alunos = str(aloc.turma.alunos_matriculados)
            status = aloc.status_alocacao
            
            dados_turmas.append([disc, turma_curso, turno, alunos, status])
            
        t_turmas = Table(dados_turmas, colWidths=[2*inch, 2.5*inch, 1*inch, 0.8*inch, 1*inch])
        t_turmas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_turmas)
    else:
        elementos.append(Paragraph("Nenhuma turma atribuída no momento.", st['Normal']))
        
    # 3. ATIVIDADE RECENTE (Intervenções)
    elementos.append(Paragraph("3. Intervenções Registradas (Últimas 10)", st['Subtitle']))
    ocorrencias_reg = RegistroOcorrencia.objects.filter(professor=professor).select_related('aluno__user').order_by('-data_registro')[:10]
    
    if ocorrencias_reg.exists():
        dados_reg = [['Data', 'Aluno', 'Ocorrência', 'Status']]
        for o in ocorrencias_reg:
            nome_aluno = o.aluno.user.get_full_name()
            dados_reg.append([o.data_registro.strftime('%d/%m/%Y'), nome_aluno, o.tipo_ocorrencia, o.status_intervencao])
            
        t_reg = Table(dados_reg, colWidths=[1*inch, 2.5*inch, 2*inch, 1.5*inch])
        t_reg.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        elementos.append(t_reg)
    else:
        elementos.append(Paragraph("Nenhuma ocorrência registrada por este professor recentemente.", st['Normal']))

    elementos.append(Spacer(1, 0.5*inch))
    elementos.append(Paragraph("SENAI School Manager - Relatório Docente", st['Footer']))
    
    pdf.build(elementos)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_docente_{professor.user.username}.pdf"'
    return response

# =============================================================================
# RELATÓRIO DA SECRETARIA
# =============================================================================
@login_required
@require_GET
def relatorio_secretaria_pdf(request, secretaria_id):
    """Gera PDF gerencial da secretaria com estatísticas"""
    
    try:
        secretaria = Secretaria.objects.select_related('user').get(user_id=secretaria_id)
    except Secretaria.DoesNotExist:
        return HttpResponse("Secretaria não encontrada.", status=404)
    
    if request.user != secretaria.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elementos = []
    st = get_custom_styles()
    
    elementos.append(Paragraph("RELATÓRIO GERENCIAL - SECRETARIA ACADÊMICA", st['Title']))
    elementos.append(Paragraph(f"Gerado por: {secretaria.user.get_full_name()} | Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", st['Normal']))
    elementos.append(Spacer(1, 0.2*inch))
    
    # 1. RESUMO GERAL
    elementos.append(Paragraph("1. Quadro Geral de Ocupação", st['Subtitle']))
    
    total_alunos = Aluno.objects.count()
    ativos = Aluno.objects.filter(status_matricula='Ativo').count()
    professores = Professor.objects.count()
    turmas = Turma.objects.count()
    
    dados_resumo = [
        ['Total de Alunos', 'Alunos Ativos', 'Professores', 'Turmas'],
        [str(total_alunos), str(ativos), str(professores), str(turmas)]
    ]
    t_resumo = Table(dados_resumo, colWidths=[1.8*inch]*4)
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    elementos.append(t_resumo)
    
    # 2. ALUNOS POR CURSO (Stats)
    elementos.append(Paragraph("2. Distribuição de Alunos por Curso", st['Subtitle']))
    
    # Agregação via Django ORM
    alunos_por_curso = Aluno.objects.values('turma_atual__id_curso__nome_curso').annotate(total=Count('user')).order_by('-total')
    
    if alunos_por_curso:
        dados_curso = [['Curso', 'Total de Alunos']]
        for item in alunos_por_curso:
            nome_curso = item['turma_atual__id_curso__nome_curso'] or "Sem Curso/Turma Definida"
            total = str(item['total'])
            dados_curso.append([nome_curso, total])
            
        t_curso = Table(dados_curso, colWidths=[5*inch, 2*inch])
        t_curso.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'), # Centralizar números
        ]))
        elementos.append(t_curso)
    else:
        elementos.append(Paragraph("Sem dados de distribuição por curso.", st['Normal']))

    # 3. NOVAS MATRÍCULAS (Recentes)
    elementos.append(Paragraph("3. Últimas Matrículas Realizadas (Recentes)", st['Subtitle']))
    novos_alunos = Aluno.objects.select_related('user', 'turma_atual').order_by('-data_matricula')[:15]
    
    if novos_alunos:
        dados_novos = [['RA', 'Nome do Aluno', 'Data Matrícula', 'Turma Alocada']]
        for a in novos_alunos:
            ra = a.RA_aluno
            nome = a.user.get_full_name()
            dt = a.data_matricula.strftime('%d/%m/%Y')
            turma = a.turma_atual.nome if a.turma_atual else "Pendente"
            dados_novos.append([ra, nome, dt, turma])
            
        t_novos = Table(dados_novos, colWidths=[1.5*inch, 3*inch, 1.2*inch, 1.5*inch])
        t_novos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.aliceblue),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(t_novos)
    else:
        elementos.append(Paragraph("Nenhuma matrícula recente encontrada.", st['Normal']))

    # 4. MONITORAMENTO DE TURMAS LOTADAS
    elementos.append(Paragraph("4. Alerta: Turmas Próximas da Capacidade Máxima", st['Subtitle']))
    # Filtro Python simples para calcular ocupação > 90% (já que não temos campo calculado no banco)
    turmas_cheias = []
    todas_turmas = Turma.objects.all()
    for t in todas_turmas:
        if t.capacidade_maxima > 0:
            ocupacao = (t.alunos_matriculados / t.capacidade_maxima) * 100
            if ocupacao >= 80: # Alerta acima de 80%
                turmas_cheias.append([t.nome, f"{t.alunos_matriculados}/{t.capacidade_maxima}", f"{ocupacao:.1f}%"])

    if turmas_cheias:
        dados_cheias = [['Turma', 'Ocupação', '% Uso']] + turmas_cheias
        t_cheias = Table(dados_cheias, colWidths=[3*inch, 2*inch, 2*inch])
        t_cheias.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        elementos.append(t_cheias)
    else:
        elementos.append(Paragraph("Todas as turmas estão com ocupação abaixo de 80%.", st['Normal']))

    elementos.append(Spacer(1, 0.5*inch))
    elementos.append(Paragraph("SENAI School Manager - Controle Acadêmico", st['Footer']))
    
    pdf.build(elementos)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_secretaria_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response

# =============================================================================
# RELATÓRIO DA COORDENAÇÃO (Já Otimizado - Mantido e Integrado)
# =============================================================================
@login_required
@require_GET
def relatorio_coordenacao_pdf(request, coordenacao_id):
    """Gera PDF do relatório da coordenação - Versão Estendida"""
    
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user_id=coordenacao_id)
    except Coordenacao.DoesNotExist:
        return HttpResponse("Coordenação não encontrada.", status=404)
    
    if request.user != coordenacao.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch, leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    elementos = []
    st = get_custom_styles()
    
    elementos.append(Paragraph("RELATÓRIO GERAL - COORDENAÇÃO ACADÊMICA", st['Title']))
    elementos.append(Paragraph(f"Responsável: {coordenacao.user.get_full_name()} | Data: {datetime.now().strftime('%d/%m/%Y')}", st['Normal']))
    elementos.append(Spacer(1, 0.2*inch))
    
    # 1. INDICADORES GERAIS
    elementos.append(Paragraph("1. Indicadores Gerais", st['Subtitle']))
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    dados_indicadores = [
        ['Alunos Matriculados', 'Professores Ativos', 'Turmas Registradas'],
        [str(total_alunos), str(total_professores), str(total_turmas)]
    ]
    
    t_ind = Table(dados_indicadores, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
    t_ind.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elementos.append(t_ind)
    elementos.append(Spacer(1, 0.2*inch))

    # 2. STATUS DAS TURMAS (Ativas/Recentes)
    elementos.append(Paragraph("2. Status das Turmas (Recentes)", st['Subtitle']))
    try:
        turmas_recentes = Turma.objects.all().select_related('id_curso').order_by('-ano_letivo', '-data_inicio')[:10]
        if turmas_recentes.exists():
            dados_turmas = [['Turma', 'Curso', 'Ocupação', 'Status Aprovação']]
            for t in turmas_recentes:
                ocupacao = f"{t.alunos_matriculados}/{t.capacidade_maxima}"
                dados_turmas.append([t.nome, t.id_curso.nome_curso[:30], ocupacao, t.status_aprovacao])
            
            t_turmas = Table(dados_turmas, colWidths=[2*inch, 3*inch, 1*inch, 1.5*inch])
            t_turmas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elementos.append(t_turmas)
        else:
            elementos.append(Paragraph("Nenhuma turma registrada recentemente.", st['Normal']))
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao carregar turmas: {e}", st['Normal']))

    # 3. OCORRÊNCIAS DISCIPLINARES
    elementos.append(Paragraph("3. Ocorrências Disciplinares Recentes", st['Subtitle']))
    try:
        ocorrencias = RegistroOcorrencia.objects.all().select_related('aluno__user').order_by('-data_registro')[:10]
        if ocorrencias.exists():
            dados_oc = [['Data', 'Aluno', 'Tipo', 'Status']]
            for o in ocorrencias:
                data_fmt = o.data_registro.strftime('%d/%m/%Y')
                nome_aluno = o.aluno.user.get_full_name() if o.aluno and o.aluno.user else "N/A"
                dados_oc.append([data_fmt, nome_aluno, o.tipo_ocorrencia, o.status_intervencao])
            
            t_oc = Table(dados_oc, colWidths=[1*inch, 3*inch, 2*inch, 1.5*inch])
            t_oc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elementos.append(t_oc)
        else:
            elementos.append(Paragraph("Nenhuma ocorrência registrada recentemente.", st['Normal']))
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao carregar ocorrências: {e}", st['Normal']))

    # 4. MONITORAMENTO DE BOLETINS
    elementos.append(Paragraph("4. Boletins Pendentes (Em Aberto)", st['Subtitle']))
    try:
        boletins = Boletim.objects.filter(status_boletim='Em Aberto').select_related('turma').order_by('data_emissao')[:10]
        if boletins.exists():
            dados_bol = [['Turma', 'Período Ref.', 'Data Emissão']]
            for b in boletins:
                data_fmt = b.data_emissao.strftime('%d/%m/%Y') if b.data_emissao else "N/A"
                dados_bol.append([b.turma.nome, b.periodo_referencia, data_fmt])
            
            t_bol = Table(dados_bol, colWidths=[3*inch, 2.5*inch, 2*inch])
            t_bol.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elementos.append(t_bol)
        else:
            elementos.append(Paragraph("Não há boletins pendentes de fechamento.", st['Normal']))
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao carregar boletins: {e}", st['Normal']))

    # 5. DESEMPENHO RECENTE (Histórico)
    elementos.append(Paragraph("5. Últimos Lançamentos de Notas", st['Subtitle']))
    try:
        historicos = Historico.objects.filter(
            turma_disciplina_professor__turma__coordenacao_aprovacao=coordenacao
        ).select_related(
            'id_aluno__user', 
            'turma_disciplina_professor__disciplina', 
            'turma_disciplina_professor__turma'
        ).order_by('-data_lancamento')[:15]

        if historicos.exists():
            dados_historico = [['Aluno', 'Disciplina', 'Turma', 'Nota', 'Status']]
            for h in historicos:
                nome_aluno = h.id_aluno.user.get_full_name() if h.id_aluno and h.id_aluno.user else "N/A"
                nome_disc = h.turma_disciplina_professor.disciplina.nome if h.turma_disciplina_professor and h.turma_disciplina_professor.disciplina else "N/A"
                nome_turma = h.turma_disciplina_professor.turma.nome if h.turma_disciplina_professor and h.turma_disciplina_professor.turma else "N/A"
                nota = str(h.nota_final) if h.nota_final is not None else "-"
                status = h.status_aprovacao or "-"
                dados_historico.append([nome_aluno, nome_disc, nome_turma, nota, status])
                
            tabela_hist = Table(dados_historico, colWidths=[2.5*inch, 2*inch, 1.5*inch, 0.8*inch, 1.2*inch])
            tabela_hist.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elementos.append(tabela_hist)
        else:
            elementos.append(Paragraph("Nenhum registro de histórico recente encontrado para turmas desta coordenação.", st['Normal']))
    
    except Exception as e:
        elementos.append(Paragraph(f"Erro ao carregar dados de desempenho: {str(e)}", st['Normal']))

    elementos.append(Spacer(1, 0.5*inch))
    elementos.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", st['Footer']))
    
    pdf.build(elementos)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_coordenacao_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response