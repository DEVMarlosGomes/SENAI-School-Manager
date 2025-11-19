from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from django.core.files.base import ContentFile
from django.conf import settings
import io
import os


class GeradorPDFSENAI:
    """Classe para gerar PDFs profissionais para o SENAI"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._criar_estilos_customizados()
        
    def _criar_estilos_customizados(self):
        """Cria estilos customizados para os documentos"""
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
            name='Normal',
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
        
        self.styles.add(ParagraphStyle(
            name='Rodape',
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
    
    def gerar_relatorio_aluno(self, aluno):
        """Gera relatório de desempenho do aluno"""
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
        
        elementos.append(Paragraph(
            "RELATÓRIO DE ALUNO",
            self.styles['Titulo']
        ))
        
        elementos.append(Spacer(1, 0.2*inch))
        
        dados_aluno = [
            ['Nome Completo:', aluno.user.get_full_name() or aluno.user.username],
            ['RA/Matrícula:', aluno.RA_aluno if hasattr(aluno, 'RA_aluno') else 'N/A'],
            ['Email:', aluno.user.email],
            ['Status:', aluno.status_matricula if hasattr(aluno, 'status_matricula') else 'N/A'],
            ['Data do Relatório:', datetime.now().strftime('%d/%m/%Y às %H:%M')],
        ]
        
        tabela_aluno = Table(dados_aluno, colWidths=[2.5*inch, 3.5*inch])
        tabela_aluno.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elementos.append(tabela_aluno)
        elementos.append(Spacer(1, 0.3*inch))
        
        elementos.append(Paragraph(
            "Informações Acadêmicas",
            self.styles['Subtitulo']
        ))
        
        elementos.append(Spacer(1, 0.1*inch))
        
        dados_academicos = [
            ['Turma:', getattr(aluno, 'turma_atual', 'N/A')],
            ['Status Matrícula:', getattr(aluno, 'status_matricula', 'N/A')],
            ['Data de Criação:', aluno.user.date_joined.strftime('%d/%m/%Y')],
        ]
        
        tabela_academica = Table(dados_academicos, colWidths=[2.5*inch, 3.5*inch])
        tabela_academica.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e0e0e0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        elementos.append(tabela_academica)
        elementos.append(Spacer(1, 0.5*inch))
        
        elementos.append(Paragraph(
            f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} pelo Sistema SENAI",
            self.styles['Rodape']
        ))
        
        pdf.build(elementos)
        
        buffer.seek(0)
        return buffer
    
    def gerar_relatorio_turma(self, turma, alunos):
        """Gera relatório de uma turma com lista de alunos"""
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
        
        elementos.append(Paragraph(
            "RELATÓRIO DE TURMA",
            self.styles['Titulo']
        ))
        
        elementos.append(Spacer(1, 0.2*inch))
        
        elementos.append(Paragraph(
            f"Turma: {turma}",
            self.styles['Subtitulo']
        ))
        
        elementos.append(Spacer(1, 0.1*inch))
        
        dados_turma = [['#', 'Nome', 'RA/Matrícula', 'Email', 'Status']]
        
        for idx, aluno in enumerate(alunos, 1):
            ra = aluno.RA_aluno if hasattr(aluno, 'RA_aluno') else 'N/A'
            status = aluno.status_matricula if hasattr(aluno, 'status_matricula') else 'N/A'
            dados_turma.append([
                str(idx),
                aluno.user.get_full_name() or aluno.user.username,
                ra,
                aluno.user.email,
                status
            ])
        
        tabela_turma = Table(dados_turma, colWidths=[0.5*inch, 1.5*inch, 1.2*inch, 1.8*inch, 1*inch])
        tabela_turma.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c41e3a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        elementos.append(tabela_turma)
        elementos.append(Spacer(1, 0.3*inch))
        
        elementos.append(Paragraph(
            f"Total de Alunos: {len(alunos)}",
            self.styles['Subtitulo']
        ))
        
        elementos.append(Spacer(1, 0.5*inch))
        
        elementos.append(Paragraph(
            f"Relatório gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} pelo Sistema SENAI",
            self.styles['Rodape']
        ))
        
        pdf.build(elementos)
        
        buffer.seek(0)
        return buffer
    
    def gerar_certificado_aluno(self, aluno, curso, data_conclusao):
        """Gera certificado de conclusão para o aluno"""
        buffer = io.BytesIO()
        
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=1*inch,
            bottomMargin=1*inch,
            leftMargin=1*inch,
            rightMargin=1*inch
        )
        
        elementos = []
        
        elementos.append(Spacer(1, 0.5*inch))
        
        elementos.append(Paragraph(
            "CERTIFICADO DE CONCLUSÃO",
            self.styles['Titulo']
        ))
        
        elementos.append(Spacer(1, 0.3*inch))
        
        nome_aluno = aluno.user.get_full_name() or aluno.user.username
        
        texto_certificado = f"""
        <p align="center">
            <b>Certificamos que</b>
        </p>
        <p align="center" style="font-size: 16px; margin-top: 30px;">
            <b>{nome_aluno}</b>
        </p>
        <p align="center" style="margin-top: 30px;">
            completou com sucesso o curso de
        </p>
        <p align="center" style="font-size: 16px; margin-top: 20px;">
            <b>{curso}</b>
        </p>
        <p align="center" style="margin-top: 30px;">
            em {data_conclusao.strftime('%d de %B de %Y')}
        </p>
        <p align="center" style="margin-top: 50px;">
            ___________________________<br/>
            Assinatura Autorizada<br/>
            SENAI
        </p>
        """
        
        elementos.append(Paragraph(texto_certificado, self.styles['Normal']))
        
        elementos.append(Spacer(1, 0.5*inch))
        
        elementos.append(Paragraph(
            f"Documento gerado em {datetime.now().strftime('%d/%m/%Y')}",
            self.styles['Rodape']
        ))
        
        pdf.build(elementos)
        
        buffer.seek(0)
        return buffer


def gerar_pdf_relatorio_aluno(aluno):
    """Função auxiliar para gerar PDF de relatório de aluno"""
    gerador = GeradorPDFSENAI()
    return gerador.gerar_relatorio_aluno(aluno)


def gerar_pdf_relatorio_turma(turma, alunos):
    """Função auxiliar para gerar PDF de relatório de turma"""
    gerador = GeradorPDFSENAI()
    return gerador.gerar_relatorio_turma(turma, alunos)


def gerar_pdf_certificado(aluno, curso, data_conclusao):
    """Função auxiliar para gerar certificado em PDF"""
    gerador = GeradorPDFSENAI()
    return gerador.gerar_pdf_certificado_aluno(aluno, curso, data_conclusao)
