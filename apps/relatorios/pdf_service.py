from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import io
from decimal import Decimal
import os

# Django settings for SITE URL and base dir
from django.conf import settings

# QR code support
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics import renderPM
from django.db.models import Avg, Sum

class GeradorPDFSENAI:
    """Classe para gerar PDFs profissionais para o SENAI"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
        
    def _criar_estilos_customizados(self):
        self.styles.add(ParagraphStyle(
            name='Titulo',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#c41e3a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='NormalJustificado',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leading=18
        ))
        
        self.styles.add(ParagraphStyle(
            name='Rodape',
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def gerar_relatorio_aluno(self, aluno, codigo_validacao=None):
        """Gera boletim do aluno"""
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.75*inch,
            rightMargin=0.75*inch
        )
        
        elementos = []
        elementos.append(Paragraph("BOLETIM ESCOLAR", self.styles['Titulo']))
        elementos.append(Spacer(1, 0.2*inch))
        
        # Dados do Cabeçalho
        dados_aluno = [
            ['Nome Completo:', aluno.user.get_full_name() or aluno.user.username],
            ['RA/Matrícula:', aluno.RA_aluno if hasattr(aluno, 'RA_aluno') else 'N/A'],
            ['Turma:', str(aluno.turma_atual) if aluno.turma_atual else 'N/A'],
            ['Data de Emissão:', datetime.now().strftime('%d/%m/%Y')],
        ]
        
        tabela_aluno = Table(dados_aluno, colWidths=[2.5*inch, 3.5*inch])
        tabela_aluno.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elementos.append(tabela_aluno)
        elementos.append(Spacer(1, 0.3*inch))
        elementos.append(Paragraph("Desempenho Acadêmico", self.styles['Subtitulo']))
        
        # Tabela de Notas (Simplificada para exemplo)
        if hasattr(aluno, 'historico') and aluno.historico.exists():
            dados_notas = [['Disciplina', 'Média', 'Frequência', 'Situação']]
            for hist in aluno.historico.all():
                dados_notas.append([
                    hist.turma_disciplina_professor.disciplina.nome,
                    f"{hist.media_final:.1f}" if hist.media_final else "-",
                    f"{hist.frequencia_percentual:.0f}%" if hist.frequencia_percentual else "-",
                    hist.status_aprovacao or "Cursando"
                ])
            
            tabela_notas = Table(dados_notas, colWidths=[3*inch, 1*inch, 1*inch, 1.5*inch])
            tabela_notas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elementos.append(tabela_notas)
        else:
            elementos.append(Paragraph("Nenhum registro de notas encontrado.", self.styles['NormalJustificado']))

        elementos.append(Spacer(1, 1*inch))
        
        if codigo_validacao:
            elementos.append(Paragraph(f"Validação: <b>{codigo_validacao}</b>", self.styles['Rodape']))

        pdf.build(elementos)
        buffer.seek(0)
        return buffer

    def gerar_declaracao_matricula(self, aluno, codigo_validacao=None):
        """Gera declaração formal"""
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=1*inch,
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        
        elementos = []
        elementos.append(Paragraph("SENAI - Serviço Nacional de Aprendizagem Industrial", self.styles['Subtitulo']))
        elementos.append(Spacer(1, 0.5*inch))
        elementos.append(Paragraph("DECLARAÇÃO DE MATRÍCULA", self.styles['Titulo']))
        elementos.append(Spacer(1, 0.5*inch))
        
        nome = aluno.user.get_full_name().upper()
        ra = aluno.RA_aluno
        rg = aluno.RG_aluno or "Não informado"
        turma = aluno.turma_atual.nome if aluno.turma_atual else "Não definida"
        ano = datetime.now().year
        
        texto = f"""
        Declaramos para os devidos fins que <b>{nome}</b>, portador(a) do RG nº {rg} e matriculado(a) sob o RA <b>{ra}</b>,
        é aluno(a) regularmente matriculado(a) nesta instituição de ensino no ano letivo de {ano}, frequentando a turma <b>{turma}</b>.
        """
        elementos.append(Paragraph(texto, self.styles['NormalJustificado']))
        
        elementos.append(Spacer(1, 1.5*inch))
        elementos.append(Paragraph("_______________________________________________", self.styles['Rodape']))
        elementos.append(Paragraph("Secretaria Acadêmica", self.styles['Rodape']))
        
        if codigo_validacao:
            elementos.append(Spacer(1, 0.5*inch))
            elementos.append(Paragraph(f"Código de Autenticidade: {codigo_validacao}", self.styles['Rodape']))

        pdf.build(elementos)
        buffer.seek(0)
        return buffer

    def gerar_relatorio_geral_aluno(self, aluno):
        """
        Gera um relatório completo do aluno com: dados cadastrais, resumo acadêmico,
        histórico detalhado, situação financeira, documentos emitidos e ocorrências.
        """
        # Importar modelos localmente para evitar ciclos
        from apps.academico.models import Historico, RegistroOcorrencia
        from apps.payments.models import Pagamento
        from apps.relatorios.models import DocumentoEmitido

        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )

        elementos = []
        elementos.append(Paragraph("RELATÓRIO COMPLETO DO ALUNO", self.styles['Titulo']))
        elementos.append(Spacer(1, 0.1*inch))

        # Cabeçalho com dados básicos e Profile (telefone, cpf, endereço quando disponíveis)
        profile = getattr(aluno.user, 'profile', None)
        endereco_text = 'N/A'
        if profile:
            addr_parts = []
            if getattr(profile, 'logradouro', None):
                part = profile.logradouro
                if getattr(profile, 'numero', None):
                    part += f", {profile.numero}"
                addr_parts.append(part)
            if getattr(profile, 'bairro', None):
                addr_parts.append(profile.bairro)
            if getattr(profile, 'cidade', None) and getattr(profile, 'estado', None):
                addr_parts.append(f"{profile.cidade}/{profile.estado}")
            if getattr(profile, 'cep', None):
                addr_parts.append(f"CEP: {profile.cep}")
            endereco_text = ' - '.join(addr_parts) if addr_parts else 'N/A'

        dados_cab = [
            ['Nome:', aluno.user.get_full_name() or aluno.user.username],
            ['RA/Matrícula:', getattr(aluno, 'RA_aluno', 'N/A')],
            ['E-mail:', aluno.user.email or 'N/A'],
            ['Telefone:', getattr(profile, 'telefone', 'N/A') if profile else 'N/A'],
            ['CPF:', getattr(profile, 'cpf', 'N/A') if profile else 'N/A'],
            ['Endereço:', endereco_text],
            ['Turma Atual:', aluno.turma_atual.nome if aluno.turma_atual else 'N/A'],
            ['Status Matrícula:', getattr(aluno, 'status_matricula', 'N/A')],
            ['Data de Matrícula:', aluno.data_matricula.strftime('%d/%m/%Y') if getattr(aluno, 'data_matricula', None) else 'N/A']
        ]
        # Tentar carregar logo do projeto (static/img/logo.png ou static/img/senai-logo.png)
        logo_candidates = [
            os.path.join(getattr(settings, 'BASE_DIR', ''), 'static', 'img', 'logo.png'),
            os.path.join(getattr(settings, 'BASE_DIR', ''), 'static', 'img', 'senai-logo.png'),
            os.path.join(getattr(settings, 'BASE_DIR', ''), 'static', 'img', 'logo_senai.png'),
        ]
        logo_path = None
        for p in logo_candidates:
            if p and os.path.exists(p):
                logo_path = p
                break

        # Construir a tabela do cabeçalho; se houver logo, colocá-la à esquerda
        tabela_info = Table(dados_cab, colWidths=[2.0*inch, 4.0*inch])
        tabela_info.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f5f5f5')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey)
        ]))

        if logo_path:
            try:
                logo_img = RLImage(logo_path, width=1.2*inch, height=1.2*inch)
            except Exception:
                logo_img = Paragraph('', self.styles['Normal'])
            wrapper = Table([[logo_img, tabela_info]], colWidths=[1.4*inch, 4.6*inch])
            wrapper.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
            elementos.append(wrapper)
        else:
            elementos.append(tabela_info)
        elementos.append(Spacer(1, 0.2*inch))

        # Resumo Acadêmico
        elementos.append(Paragraph('Resumo Acadêmico', self.styles['Subtitulo']))
        historicos = aluno.historico.select_related('turma_disciplina_professor__disciplina').all()
        media_geral = historicos.aggregate(avg=Avg('media_final'))['avg'] or 0
        faltas_total = historicos.aggregate(total=Sum('total_faltas'))['total'] or 0

        resumo = [
            ['Média Geral:', f"{round(media_geral,1)}"],
            ['Total de Registros de Histórico:', str(historicos.count())],
            ['Total de Faltas:', str(faltas_total)]
        ]
        tabela_resumo = Table(resumo, colWidths=[2.0*inch, 4.0*inch])
        tabela_resumo.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f9f9f9')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.25, colors.grey)
        ]))
        elementos.append(tabela_resumo)
        elementos.append(Spacer(1, 0.2*inch))

        # Histórico detalhado
        elementos.append(Paragraph('Histórico Detalhado', self.styles['Subtitulo']))
        if historicos.exists():
            dados_h = [['Disciplina', 'Turma', 'Média', 'Frequência', 'Status', 'Data']]
            for h in historicos.order_by('periodo_realizacao'):
                disciplina = h.turma_disciplina_professor.disciplina.nome if h.turma_disciplina_professor and h.turma_disciplina_professor.disciplina else 'N/D'
                turma = h.turma_disciplina_professor.turma.nome if h.turma_disciplina_professor and h.turma_disciplina_professor.turma else 'N/D'
                dados_h.append([
                    disciplina,
                    turma,
                    f"{h.media_final:.1f}" if h.media_final is not None else '-',
                    f"{h.frequencia_percentual:.0f}%" if h.frequencia_percentual is not None else '-',
                    h.status_aprovacao or '-',
                    h.periodo_realizacao or '-'
                ])

            tabela_h = Table(dados_h, colWidths=[2.2*inch, 1.2*inch, 0.8*inch, 0.9*inch, 1.2*inch, 1.0*inch])
            tabela_h.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#c41e3a')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),9),
            ]))
            elementos.append(tabela_h)
        else:
            elementos.append(Paragraph('Nenhum registro de histórico encontrado.', self.styles['NormalJustificado']))

        elementos.append(Spacer(1, 0.2*inch))

        # Financeiro
        elementos.append(Paragraph('Resumo Financeiro', self.styles['Subtitulo']))
        pagamentos = Pagamento.objects.filter(aluno=aluno.user).order_by('-data_criacao')
        # Somar usando Decimal para manter precisão
        total_pendente = Decimal('0.00')
        total_recebido = Decimal('0.00')
        for p in pagamentos.filter(status='pendente'):
            total_pendente += (p.valor or Decimal('0.00'))
        for p in pagamentos.filter(status='pago'):
            total_recebido += (p.valor or Decimal('0.00'))
        dados_fin = [
            ['Total Recebido:', f"R$ {total_recebido:.2f}"],
            ['Total Pendente:', f"R$ {total_pendente:.2f}" ],
            ['Número de Lançamentos:', str(pagamentos.count())]
        ]
        tabela_fin = Table(dados_fin, colWidths=[2.0*inch, 4.0*inch])
        tabela_fin.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.25,colors.grey),
            ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f9f9f9')),
            ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ]))
        elementos.append(tabela_fin)

        elementos.append(Spacer(1, 0.2*inch))

        # Documentos emitidos
        elementos.append(Paragraph('Documentos Emitidos', self.styles['Subtitulo']))
        docs = DocumentoEmitido.objects.filter(aluno=aluno).order_by('-data_emissao')
        if docs.exists():
            dados_docs = [['Tipo', 'Data Emissão', 'Código Validação']]
            for d in docs:
                dados_docs.append([d.get_tipo_display(), d.data_emissao.strftime('%d/%m/%Y'), d.codigo_validacao])
            tabela_docs = Table(dados_docs, colWidths=[2.5*inch, 2.0*inch, 1.5*inch])
            tabela_docs.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.grey), ('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
            elementos.append(tabela_docs)
        else:
            elementos.append(Paragraph('Nenhum documento emitido para este aluno.', self.styles['NormalJustificado']))

        elementos.append(Spacer(1, 0.2*inch))

        # Ocorrências
        elementos.append(Paragraph('Registros de Ocorrência', self.styles['Subtitulo']))
        ocorrencias = RegistroOcorrencia.objects.filter(aluno=aluno).order_by('-data_registro')
        if ocorrencias.exists():
            for o in ocorrencias[:20]:
                texto = f"{o.data_registro.strftime('%d/%m/%Y %H:%M')} - {o.tipo_ocorrencia}: {o.descricao[:200]}"
                elementos.append(Paragraph(texto, self.styles['NormalJustificado']))
        else:
            elementos.append(Paragraph('Nenhum registro de ocorrência encontrado.', self.styles['NormalJustificado']))

        elementos.append(Spacer(1, 0.5*inch))

        # Adicionar QR Code com último código de validação, se houver
        ultimo_codigo = None
        if docs.exists():
            ultimo_codigo = docs.first().codigo_validacao
        if ultimo_codigo:
            # Gerar QR com URL de validação (preferir SITE_URL do settings)
            base = getattr(settings, 'SITE_URL', None) or 'https://example.com'
            validation_url = f"{base.rstrip('/')}/validacao/{ultimo_codigo}"
            try:
                qr = QrCodeWidget(validation_url)
                qr_size = 100
                d = Drawing(qr_size, qr_size)
                d.add(qr)
                png_data = renderPM.drawToString(d, fmt='PNG')
                img_buf = io.BytesIO(png_data)
                img = RLImage(img_buf, width=qr_size, height=qr_size)
                elementos.append(img)
                elementos.append(Spacer(1, 0.1*inch))
                elementos.append(Paragraph(f'Validação: {ultimo_codigo}', self.styles['NormalJustificado']))
                elementos.append(Paragraph(f'Acesse: {validation_url}', self.styles['NormalJustificado']))
            except Exception:
                elementos.append(Paragraph(f'Código de Validação: {ultimo_codigo}', self.styles['NormalJustificado']))

        elementos.append(Paragraph(f'Emitido em {datetime.now().strftime("%d/%m/%Y %H:%M")}', self.styles['Rodape']))

        # Rodapé com página
        def _rodape(canvas, doc):
            canvas.saveState()
            footer_text = f"Gerado por SENAI - Página {doc.page}"
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            canvas.drawCentredString(A4[0]/2.0, 0.4*inch, footer_text)
            canvas.restoreState()

        pdf.build(elementos, onFirstPage=_rodape, onLaterPages=_rodape)
        buffer.seek(0)
        return buffer

    def gerar_relatorio_coordenacao(self, solicitante_user=None):
        """Gera um relatório de coordenação com KPIs e eficiência por curso."""
        # Importar modelos localmente
        from apps.academico.models import Aluno, Turma, Professor, Curso, Historico

        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
            leftMargin=0.6*inch,
            rightMargin=0.6*inch
        )

        elementos = []
        elementos.append(Paragraph("RELATÓRIO GERAL - COORDENAÇÃO", self.styles['Titulo']))
        elementos.append(Spacer(1, 0.1*inch))

        if solicitante_user:
            elementos.append(Paragraph(f"Gerado por: {solicitante_user.get_full_name()}", self.styles['NormalJustificado']))
        elementos.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['NormalJustificado']))
        elementos.append(Spacer(1, 0.2*inch))

        # KPIs básicos
        total_alunos = Aluno.objects.count()
        total_alunos_ativos = Aluno.objects.filter(status_matricula__iexact='Ativo').count()
        total_turmas = Turma.objects.count()
        total_professores = Professor.objects.count()

        kpis = [
            ['Total de Alunos:', str(total_alunos)],
            ['Alunos Ativos:', str(total_alunos_ativos)],
            ['Total de Turmas:', str(total_turmas)],
            ['Total de Professores:', str(total_professores)],
        ]
        tabela_kpis = Table(kpis, colWidths=[3*inch, 3*inch])
        tabela_kpis.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f5f5f5')),
            ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('GRID',(0,0),(-1,-1),0.25,colors.grey)
        ]))
        elementos.append(tabela_kpis)
        elementos.append(Spacer(1, 0.2*inch))

        # Análise de risco (média <5 ou frequência <75) considerando alunos ativos
        historicos_agg = Historico.objects.filter(id_aluno__status_matricula__iexact='Ativo').values('id_aluno').annotate(
            avg_media=Avg('media_final'), avg_freq=Avg('frequencia_percentual')
        )
        alunos_com_historico = historicos_agg.count()
        alunos_risco = sum(1 for h in historicos_agg if (h.get('avg_media') is not None and h.get('avg_media') < 5) or (h.get('avg_freq') is not None and h.get('avg_freq') < 75))

        elementos.append(Paragraph('Indicadores de Risco', self.styles['Subtitulo']))
        dados_risco = [
            ['Alunos com histórico (ativos):', str(alunos_com_historico)],
            ['Alunos em risco (critério média<5 ou freq<75):', str(alunos_risco)],
        ]
        tabela_risco = Table(dados_risco, colWidths=[3*inch, 3*inch])
        tabela_risco.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.25,colors.grey), ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f9f9f9'))]))
        elementos.append(tabela_risco)
        elementos.append(Spacer(1, 0.2*inch))

        # Eficiência por curso (aprovados/recuperação/reprovados)
        elementos.append(Paragraph('Eficiência por Curso', self.styles['Subtitulo']))
        cursos = Curso.objects.all()
        dados_cursos = [['Curso', 'Aprovados', 'Recuperação', 'Reprovados', 'Alunos no Curso']]
        for c in cursos:
            # considerar turmas do curso
            historicos_curso = Historico.objects.filter(turma_disciplina_professor__turma__id_curso=c)
            alunos_distintos = historicos_curso.values_list('id_aluno', flat=True).distinct().count()
            aprovados = historicos_curso.filter(status_aprovacao__iexact='Aprovado').values_list('id_aluno', flat=True).distinct().count()
            recuperacao = historicos_curso.filter(status_aprovacao__iexact='Recuperação').values_list('id_aluno', flat=True).distinct().count()
            reprovados = historicos_curso.filter(status_aprovacao__iexact='Reprovado').values_list('id_aluno', flat=True).distinct().count()
            dados_cursos.append([c.nome_curso, str(aprovados), str(recuperacao), str(reprovados), str(alunos_distintos)])

        tabela_cursos = Table(dados_cursos, colWidths=[2.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
        tabela_cursos.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.25,colors.grey),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#c41e3a')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),9),
        ]))
        elementos.append(tabela_cursos)

        elementos.append(Spacer(1, 0.3*inch))

        elementos.append(Paragraph('Observações: Este relatório é gerado dinamicamente e reflete os dados atuais do sistema.', self.styles['NormalJustificado']))

        # Rodapé simples
        def _rodape(canvas, doc):
            canvas.saveState()
            footer_text = f"Relatório de Coordenação - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            canvas.drawCentredString(A4[0]/2.0, 0.35*inch, footer_text)
            canvas.restoreState()

        pdf.build(elementos, onFirstPage=_rodape, onLaterPages=_rodape)
        buffer.seek(0)
        return buffer

    def gerar_relatorio_professor(self, professor_user):
        """Gera um relatório de atividades do professor com desempenho das turmas."""
        from apps.academico.models import TurmaDisciplinaProfessor, Historico, Professor
        
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
            leftMargin=0.6*inch,
            rightMargin=0.6*inch
        )

        elementos = []
        elementos.append(Paragraph("RELATÓRIO DE ATIVIDADES DOCENTES", self.styles['Titulo']))
        elementos.append(Spacer(1, 0.1*inch))

        # Dados básicos do professor
        try:
            professor = Professor.objects.get(user=professor_user)
            nome_prof = professor_user.get_full_name()
            reg_funcional = professor.registro_funcional
            formacao = professor.formacao
        except:
            nome_prof = professor_user.get_full_name()
            reg_funcional = 'N/A'
            formacao = 'N/A'

        dados_prof = [
            ['Professor:', nome_prof],
            ['Registro Funcional:', reg_funcional],
            ['Formação:', formacao],
            ['Data Emissão:', datetime.now().strftime('%d/%m/%Y %H:%M')],
        ]
        tabela_prof = Table(dados_prof, colWidths=[3*inch, 3*inch])
        tabela_prof.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f5f5f5')),
            ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('GRID',(0,0),(-1,-1),0.25,colors.grey)
        ]))
        elementos.append(tabela_prof)
        elementos.append(Spacer(1, 0.2*inch))

        # Turmas e disciplinas alocadas
        elementos.append(Paragraph('Alocações Atuais', self.styles['Subtitulo']))
        alocacoes = TurmaDisciplinaProfessor.objects.filter(professor__user=professor_user)
        
        if alocacoes.exists():
            dados_aloc = [['Turma', 'Disciplina', 'Status']]
            for aloc in alocacoes:
                dados_aloc.append([
                    aloc.turma.nome,
                    aloc.disciplina.nome,
                    aloc.status_alocacao or 'Alocado'
                ])
            
            tabela_aloc = Table(dados_aloc, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
            tabela_aloc.setStyle(TableStyle([
                ('GRID',(0,0),(-1,-1),0.25,colors.grey),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#c41e3a')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),9),
            ]))
            elementos.append(tabela_aloc)
        else:
            elementos.append(Paragraph('Nenhuma alocação registrada.', self.styles['NormalJustificado']))

        elementos.append(Spacer(1, 0.2*inch))

        # Desempenho das turmas
        elementos.append(Paragraph('Desempenho das Turmas', self.styles['Subtitulo']))
        historicos = Historico.objects.filter(turma_disciplina_professor__professor__user=professor_user)
        
        if historicos.exists():
            turmas_unicas = historicos.values('turma_disciplina_professor__turma__nome').distinct()
            dados_desemp = [['Turma', 'Total Alunos', 'Média Geral', 'Frequência Média', 'Aprovados']]
            
            for turma_info in turmas_unicas:
                turma_nome = turma_info['turma_disciplina_professor__turma__nome']
                hist_turma = historicos.filter(turma_disciplina_professor__turma__nome=turma_nome)
                total = hist_turma.values_list('id_aluno', flat=True).distinct().count()
                media = hist_turma.aggregate(m=Avg('media_final'))['m'] or 0
                freq = hist_turma.aggregate(f=Avg('frequencia_percentual'))['f'] or 0
                aprovados = hist_turma.filter(status_aprovacao__iexact='Aprovado').values_list('id_aluno', flat=True).distinct().count()
                
                dados_desemp.append([
                    turma_nome,
                    str(total),
                    f"{media:.1f}",
                    f"{freq:.1f}%",
                    str(aprovados)
                ])
            
            tabela_desemp = Table(dados_desemp, colWidths=[1.8*inch, 1.2*inch, 1.2*inch, 1.5*inch, 1.3*inch])
            tabela_desemp.setStyle(TableStyle([
                ('GRID',(0,0),(-1,-1),0.25,colors.grey),
                ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#c41e3a')),
                ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
                ('FONTSIZE',(0,0),(-1,-1),9),
            ]))
            elementos.append(tabela_desemp)
        else:
            elementos.append(Paragraph('Nenhum histórico de alunos registrado.', self.styles['NormalJustificado']))

        elementos.append(Spacer(1, 0.3*inch))
        elementos.append(Paragraph('Relatório gerado automaticamente pelo sistema SENAI.', self.styles['NormalJustificado']))

        def _rodape_prof(canvas, doc):
            canvas.saveState()
            footer_text = f"Relatório do Professor - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            canvas.drawCentredString(A4[0]/2.0, 0.35*inch, footer_text)
            canvas.restoreState()

        pdf.build(elementos, onFirstPage=_rodape_prof, onLaterPages=_rodape_prof)
        buffer.seek(0)
        return buffer

    def gerar_relatorio_secretaria(self, secretaria_user):
        """Gera um relatório de gestão da secretaria com KPIs financeiros e acadêmicos."""
        from apps.academico.models import Aluno, Turma, Curso, Historico
        from apps.payments.models import Pagamento
        
        buffer = io.BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
            leftMargin=0.6*inch,
            rightMargin=0.6*inch
        )

        elementos = []
        elementos.append(Paragraph("RELATÓRIO DE GESTÃO - SECRETARIA ACADÊMICA", self.styles['Titulo']))
        elementos.append(Spacer(1, 0.1*inch))

        elementos.append(Paragraph(f"Emitido por: {secretaria_user.get_full_name()}", self.styles['NormalJustificado']))
        elementos.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", self.styles['NormalJustificado']))
        elementos.append(Spacer(1, 0.2*inch))

        # KPIs Acadêmicos
        elementos.append(Paragraph('KPIs Acadêmicos', self.styles['Subtitulo']))
        total_alunos = Aluno.objects.count()
        total_ativos = Aluno.objects.filter(status_matricula__iexact='Ativo').count()
        total_inativos = total_alunos - total_ativos
        total_turmas = Turma.objects.count()
        total_cursos = Curso.objects.count()

        kpis_acad = [
            ['Total de Alunos:', str(total_alunos)],
            ['Alunos Ativos:', str(total_ativos)],
            ['Alunos Inativos:', str(total_inativos)],
            ['Total de Turmas:', str(total_turmas)],
            ['Total de Cursos:', str(total_cursos)],
        ]
        tabela_kpis = Table(kpis_acad, colWidths=[3*inch, 3*inch])
        tabela_kpis.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f5f5f5')),
            ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),11),
            ('GRID',(0,0),(-1,-1),0.25,colors.grey)
        ]))
        elementos.append(tabela_kpis)
        elementos.append(Spacer(1, 0.2*inch))

        # KPIs Financeiros
        elementos.append(Paragraph('KPIs Financeiros', self.styles['Subtitulo']))
        pagamentos_total = Pagamento.objects.aggregate(t=Sum('valor'))['t'] or Decimal('0.00')
        pagamentos_pago = Pagamento.objects.filter(status='pago').aggregate(t=Sum('valor'))['t'] or Decimal('0.00')
        pagamentos_pendente = pagamentos_total - pagamentos_pago

        kpis_fin = [
            ['Total Faturado:', f"R$ {pagamentos_total:.2f}"],
            ['Recebido:', f"R$ {pagamentos_pago:.2f}"],
            ['Pendente:', f"R$ {pagamentos_pendente:.2f}"],
            ['Taxa Recebimento:', f"{(pagamentos_pago/pagamentos_total*100) if pagamentos_total > 0 else 0:.1f}%"],
        ]
        tabela_fin = Table(kpis_fin, colWidths=[3*inch, 3*inch])
        tabela_fin.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.25,colors.grey),
            ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#f9f9f9')),
            ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ]))
        elementos.append(tabela_fin)
        elementos.append(Spacer(1, 0.2*inch))

        # Status de Cursos
        elementos.append(Paragraph('Status dos Cursos', self.styles['Subtitulo']))
        cursos = Curso.objects.all()
        dados_cursos = [['Curso', 'Alunos', 'Turmas', 'Status']]
        for c in cursos:
            alunos_curso = Aluno.objects.filter(turma_atual__id_curso=c).count()
            turmas_curso = Turma.objects.filter(id_curso=c).count()
            status = 'Ativo' if c.credenciamento_ativo else 'Inativo'
            dados_cursos.append([c.nome_curso, str(alunos_curso), str(turmas_curso), status])

        tabela_cursos = Table(dados_cursos, colWidths=[3*inch, 1*inch, 1*inch, 1*inch])
        tabela_cursos.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),0.25,colors.grey),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#c41e3a')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),9),
        ]))
        elementos.append(tabela_cursos)

        elementos.append(Spacer(1, 0.3*inch))

        def _rodape_sec(canvas, doc):
            canvas.saveState()
            footer_text = f"Relatório Secretaria - Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            canvas.setFont('Helvetica', 8)
            canvas.setFillColor(colors.HexColor('#666666'))
            canvas.drawCentredString(A4[0]/2.0, 0.35*inch, footer_text)
            canvas.restoreState()

        pdf.build(elementos, onFirstPage=_rodape_sec, onLaterPages=_rodape_sec)
        buffer.seek(0)
        return buffer

def gerar_pdf_relatorio_turma(nome_turma, alunos):
    """Gera lista de chamada para professores"""
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    elementos = []
    elementos.append(Paragraph(f"Lista de Chamada - Turma {nome_turma}", styles['Heading1']))
    elementos.append(Spacer(1, 20))
    
    dados = [['#', 'RA', 'Nome do Aluno', 'Assinatura']]
    for idx, aluno in enumerate(alunos, 1):
        dados.append([
            str(idx),
            aluno.RA_aluno,
            aluno.user.get_full_name(),
            "__________________________"
        ])
    
    tabela = Table(dados, colWidths=[40, 80, 200, 200])
    tabela.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    
    elementos.append(tabela)
    pdf.build(elementos)
    buffer.seek(0)
    return buffer