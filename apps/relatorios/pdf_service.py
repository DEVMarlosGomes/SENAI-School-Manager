from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from datetime import datetime
import io

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