from django.db import models
from django.conf import settings
import uuid
import os

class DocumentoEmitido(models.Model):
    TIPO_CHOICES = [
        ('BOLETIM', 'Boletim Escolar'),
        ('DECLARACAO', 'Declaração de Matrícula'),
        ('HISTORICO', 'Histórico Escolar Completo'),
        ('CERTIFICADO', 'Certificado de Conclusão'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aluno = models.ForeignKey(
        'academico.Aluno', 
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='documentos_solicitados',
        help_text="Quem pediu o documento (o próprio aluno ou secretaria)"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    arquivo = models.FileField(upload_to='documentos/%Y/%m/')
    codigo_validacao = models.CharField(max_length=32, unique=True, editable=False)
    data_emissao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_emissao']
        verbose_name = 'Documento Emitido'
        verbose_name_plural = 'Documentos Emitidos'

    def save(self, *args, **kwargs):
        if not self.codigo_validacao:
            # Gera um código único simples para validação
            self.codigo_validacao = str(uuid.uuid4().hex)[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.aluno} ({self.data_emissao.strftime('%d/%m/%Y')})"
    
    @property
    def nome_arquivo_original(self):
        return os.path.basename(self.arquivo.name)