from django.core.files.base import ContentFile
from django.utils.timezone import now
from .models import DocumentoEmitido
from .pdf_service import GeradorPDFSENAI

class DocumentoService:
    @staticmethod
    def emitir_novo_documento(aluno, tipo_documento, solicitante):
        """
        Gera o PDF, salva no banco e retorna a instância.
        """
        # 1. Cria o registro no banco (gera o ID e Código)
        novo_doc = DocumentoEmitido(
            aluno=aluno,
            solicitante=solicitante,
            tipo=tipo_documento
        )
        novo_doc.save()
        
        # 2. Gera o PDF com o código de validação
        gerador = GeradorPDFSENAI()
        pdf_buffer = None
        nome_arquivo = ""
        
        if tipo_documento == 'BOLETIM':
            pdf_buffer = gerador.gerar_relatorio_aluno(aluno, codigo_validacao=novo_doc.codigo_validacao)
            nome_arquivo = f"Boletim_{aluno.RA_aluno}_{now().strftime('%Y%m%d')}.pdf"
            
        elif tipo_documento == 'DECLARACAO':
            pdf_buffer = gerador.gerar_declaracao_matricula(aluno, codigo_validacao=novo_doc.codigo_validacao)
            nome_arquivo = f"Declaracao_{aluno.RA_aluno}_{now().strftime('%Y%m%d')}.pdf"
            
        else:
            novo_doc.delete()
            raise ValueError("Tipo inválido")
            
        # 3. Salva o arquivo físico
        novo_doc.arquivo.save(nome_arquivo, ContentFile(pdf_buffer.getvalue()))
        
        return novo_doc