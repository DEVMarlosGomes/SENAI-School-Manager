from django.db import models
from django.conf import settings


class Material(models.Model):
	TIPO_CHOICES = (
		('PDF', 'PDF'),
		('PPT', 'PPT'),
		('Vídeo', 'Vídeo'),
		('Link', 'Link'),
		('Arquivo', 'Arquivo'),
		('Outro', 'Outro'),
	)

	titulo = models.CharField(max_length=200)
	descricao = models.TextField(blank=True)
	disciplina = models.CharField(max_length=150, blank=True)
	tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='PDF')
	arquivo = models.FileField(upload_to='materiais/', null=True, blank=True)
	autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
	criado_em = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = 'Material'
		verbose_name_plural = 'Materiais'
		ordering = ['-criado_em']

	def __str__(self):
		return self.titulo
