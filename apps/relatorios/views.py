from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from apps.academico.models import Aluno, Professor, Secretaria, Coordenacao, Historico, Turma, TurmaDisciplinaProfessor
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from datetime import datetime
import io


@login_required
@require_GET
def relatorio_aluno_pdf(request, aluno_id):
    """Gera PDF do relatório completo de um aluno"""
    
    try:
        aluno = Aluno.objects.select_related('user', 'turma_atual', 'turma_atual__id_curso').get(user_id=aluno_id)
    except Aluno.DoesNotExist:
        return HttpResponse("Aluno não encontrado.", status=404)
    
    if request.user != aluno.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    elementos = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#c41e3a'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#c41e3a'), spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold')
    
    elementos.append(Paragraph("RELATÓRIO ACADÊMICO COMPLETO", titulo_style))
    elementos.append(Paragraph("SENAI - Serviço Nacional de Aprendizagem Industrial", styles['Normal']))
    elementos.append(Spacer(1, 0.3*inch))
    
    # DADOS PESSOAIS
    elementos.append(Paragraph("1. Dados Pessoais", subtitulo_style))
    elementos.append(Spacer(1, 0.1*inch))
    
    dados_pessoais = [
        ['Nome Completo:', aluno.user.get_full_name() or aluno.user.username],
        ['Nome de Usuário:', aluno.user.username],
        ['Email:', aluno.user.email or 'Não informado'],
        ['RA/Matrícula:', getattr(aluno, 'RA_aluno', 'N/A')],
        ['RG:', getattr(aluno, 'RG_aluno', 'Não informado') or 'Não informado'],
        ['Data de Nascimento:', aluno.data_nascimento.strftime('%d/%m/%Y') if hasattr(aluno, 'data_nascimento') and aluno.data_nascimento else 'Não informado'],
        ['Gênero:', getattr(aluno, 'genero', 'Não informado')],
    ]
    
    tabela_pessoais = Table(dados_pessoais, colWidths=[2*inch, 4*inch])
    tabela_pessoais.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_pessoais)
    elementos.append(Spacer(1, 0.3*inch))
    
    # INFORMAÇÕES ACADÊMICAS
    elementos.append(Paragraph("2. Informações Acadêmicas", subtitulo_style))
    elementos.append(Spacer(1, 0.1*inch))
    
    curso_nome = 'Não matriculado'
    if hasattr(aluno, 'turma_atual') and aluno.turma_atual and hasattr(aluno.turma_atual, 'id_curso') and aluno.turma_atual.id_curso:
        curso_nome = aluno.turma_atual.id_curso.nome_curso
    
    turma_nome = str(aluno.turma_atual.nome) if hasattr(aluno, 'turma_atual') and aluno.turma_atual else 'Não matriculado'
    
    dados_academicos = [
        ['Curso:', curso_nome],
        ['Turma Atual:', turma_nome],
        ['Status da Matrícula:', getattr(aluno, 'status_matricula', 'Não informado')],
        ['Data de Matrícula:', aluno.data_matricula.strftime('%d/%m/%Y') if hasattr(aluno, 'data_matricula') and aluno.data_matricula else 'Não informado'],
        ['Conclusão Ens. Médio:', aluno.conclusao_EM.strftime('%d/%m/%Y') if hasattr(aluno, 'conclusao_EM') and aluno.conclusao_EM else 'Não informado'],
        ['Data de Cadastro:', aluno.user.date_joined.strftime('%d/%m/%Y')],
        ['Último Acesso:', aluno.user.last_login.strftime('%d/%m/%Y %H:%M') if aluno.user.last_login else 'Nunca'],
    ]
    
    tabela_academicos = Table(dados_academicos, colWidths=[2*inch, 4*inch])
    tabela_academicos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_academicos)
    elementos.append(Spacer(1, 0.5*inch))
    
    # RODAPÉ
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elementos.append(Paragraph(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} - Sistema SENAI", rodape_style))
    
    pdf.build(elementos)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_aluno_{aluno.user.username}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
@require_GET
def relatorio_professor_pdf(request, professor_id):
    """Gera PDF do relatório do professor"""
    
    try:
        professor = Professor.objects.select_related('user').get(user_id=professor_id)
    except Professor.DoesNotExist:
        return HttpResponse("Professor não encontrado.", status=404)
    
    if request.user != professor.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    elementos = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#c41e3a'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#c41e3a'), spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold')
    
    elementos.append(Paragraph("RELATÓRIO DO PROFESSOR", titulo_style))
    elementos.append(Paragraph("SENAI - Sistema de Gestão Educacional", styles['Normal']))
    elementos.append(Spacer(1, 0.3*inch))
    
    # DADOS DO PROFESSOR
    elementos.append(Paragraph("1. Dados do Professor", subtitulo_style))
    elementos.append(Spacer(1, 0.1*inch))
    
    dados_professor = [
        ['Nome:', professor.user.get_full_name() or professor.user.username],
        ['Email:', professor.user.email or 'Não informado'],
        ['Usuário:', professor.user.username],
        ['Data de Cadastro:', professor.user.date_joined.strftime('%d/%m/%Y')],
        ['Último Acesso:', professor.user.last_login.strftime('%d/%m/%Y %H:%M') if professor.user.last_login else 'Nunca'],
    ]
    
    tabela_professor = Table(dados_professor, colWidths=[2*inch, 4*inch])
    tabela_professor.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_professor)
    elementos.append(Spacer(1, 0.3*inch))
    
    # TURMAS
    elementos.append(Paragraph("2. Turmas e Disciplinas", subtitulo_style))
    elementos.append(Spacer(1, 0.1*inch))
    
    try:
        turmas_disciplinas = TurmaDisciplinaProfessor.objects.filter(id_professor=professor).select_related('id_turma', 'id_disciplina')
        
        if turmas_disciplinas.exists():
            dados_turmas = [['Turma', 'Disciplina', 'Alunos']]
            
            for td in turmas_disciplinas:
                turma_nome = td.id_turma.nome if td.id_turma else 'N/A'
                disciplina_nome = td.id_disciplina.nome if td.id_disciplina else 'N/A'
                num_alunos = td.id_turma.alunos_matriculados if td.id_turma and hasattr(td.id_turma, 'alunos_matriculados') else 0
                
                dados_turmas.append([turma_nome, disciplina_nome, str(num_alunos)])
            
            tabela_turmas = Table(dados_turmas, colWidths=[2*inch, 2.5*inch, 1.5*inch])
            tabela_turmas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elementos.append(tabela_turmas)
        else:
            elementos.append(Paragraph("Nenhuma turma atribuída.", styles['Normal']))
    except Exception:
        elementos.append(Paragraph("Informações não disponíveis.", styles['Normal']))
    
    elementos.append(Spacer(1, 0.5*inch))
    
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elementos.append(Paragraph(f"Documento gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", rodape_style))
    
    pdf.build(elementos)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_professor_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
@require_GET
def relatorio_secretaria_pdf(request, secretaria_id):
    """Gera PDF do relatório da secretaria"""
    
    try:
        secretaria = Secretaria.objects.select_related('user').get(user_id=secretaria_id)
    except Secretaria.DoesNotExist:
        return HttpResponse("Secretaria não encontrada.", status=404)
    
    if request.user != secretaria.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    elementos = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#c41e3a'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#c41e3a'), spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold')
    
    elementos.append(Paragraph("RELATÓRIO GERENCIAL - SECRETARIA", titulo_style))
    elementos.append(Paragraph("SENAI - Sistema de Gestão Educacional", styles['Normal']))
    elementos.append(Spacer(1, 0.3*inch))
    
    elementos.append(Paragraph("1. Informações do Usuário", subtitulo_style))
    elementos.append(Spacer(1, 0.1*inch))
    
    dados_secretaria = [
        ['Nome:', secretaria.user.get_full_name() or secretaria.user.username],
        ['Email:', secretaria.user.email or 'Não informado'],
        ['Cargo:', 'Secretaria Acadêmica'],
    ]
    
    tabela_secretaria = Table(dados_secretaria, colWidths=[2*inch, 4*inch])
    tabela_secretaria.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_secretaria)
    elementos.append(Spacer(1, 0.3*inch))
    
    elementos.append(Paragraph("2. Estatísticas do Sistema", subtitulo_style))
    
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    dados_stats = [
        ['Total de Alunos:', str(total_alunos)],
        ['Total de Professores:', str(total_professores)],
        ['Total de Turmas:', str(total_turmas)],
    ]
    
    tabela_stats = Table(dados_stats, colWidths=[2*inch, 4*inch])
    tabela_stats.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_stats)
    elementos.append(Spacer(1, 0.5*inch))
    
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elementos.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", rodape_style))
    
    pdf.build(elementos)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_secretaria_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response


@login_required
@require_GET
def relatorio_coordenacao_pdf(request, coordenacao_id):
    """Gera PDF do relatório da coordenação"""
    
    try:
        coordenacao = Coordenacao.objects.select_related('user').get(user_id=coordenacao_id)
    except Coordenacao.DoesNotExist:
        return HttpResponse("Coordenação não encontrada.", status=404)
    
    if request.user != coordenacao.user and not request.user.is_staff:
        return HttpResponse("Sem permissão.", status=403)
    
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch, leftMargin=0.75*inch, rightMargin=0.75*inch)
    
    elementos = []
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, textColor=colors.HexColor('#c41e3a'), spaceAfter=30, alignment=TA_CENTER, fontName='Helvetica-Bold')
    subtitulo_style = ParagraphStyle('Subtitulo', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#c41e3a'), spaceAfter=12, spaceBefore=20, fontName='Helvetica-Bold')
    
    elementos.append(Paragraph("RELATÓRIO ESTRATÉGICO - COORDENAÇÃO", titulo_style))
    elementos.append(Paragraph("SENAI - Sistema de Gestão Educacional", styles['Normal']))
    elementos.append(Spacer(1, 0.3*inch))
    
    elementos.append(Paragraph("1. Informações do Coordenador", subtitulo_style))
    
    dados_coord = [
        ['Nome:', coordenacao.user.get_full_name() or coordenacao.user.username],
        ['Email:', coordenacao.user.email or 'Não informado'],
        ['Cargo:', 'Coordenação Acadêmica'],
    ]
    
    tabela_coord = Table(dados_coord, colWidths=[2*inch, 4*inch])
    tabela_coord.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_coord)
    elementos.append(Spacer(1, 0.3*inch))
    
    elementos.append(Paragraph("2. Indicadores Acadêmicos", subtitulo_style))
    
    total_alunos = Aluno.objects.count()
    total_professores = Professor.objects.count()
    total_turmas = Turma.objects.count()
    
    dados_indicadores = [
        ['Total de Alunos:', str(total_alunos)],
        ['Total de Professores:', str(total_professores)],
        ['Total de Turmas:', str(total_turmas)],
    ]
    
    tabela_indicadores = Table(dados_indicadores, colWidths=[3*inch, 3*inch])
    tabela_indicadores.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('PADDING', (0, 0), (-1, -1), 12),
    ]))
    
    elementos.append(tabela_indicadores)
    elementos.append(Spacer(1, 0.5*inch))
    
    rodape_style = ParagraphStyle('Rodape', parent=styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    elementos.append(Paragraph(f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}", rodape_style))
    
    pdf.build(elementos)
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="relatorio_coordenacao_{datetime.now().strftime("%Y%m%d")}.pdf"'
    return response
