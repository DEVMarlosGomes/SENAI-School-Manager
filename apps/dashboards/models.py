from django.db import models
from django.conf import settings
from datetime import datetime


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


class Aviso(models.Model):
	TIPO_CHOICES = (
		('Urgente', 'Urgente'),
		('Importante', 'Importante'),
		('Geral', 'Geral'),
		('Informativo', 'Informativo'),
	)
	
	USUARIO_TIPO_CHOICES = (
		('professor', 'Professor'),
		('coordenacao', 'Coordenação'),
		('secretaria', 'Secretaria'),
	)
	
	titulo = models.CharField(max_length=200)
	conteudo = models.TextField()
	tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Geral')
	criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	tipo_usuario_criador = models.CharField(max_length=20, choices=USUARIO_TIPO_CHOICES, default='secretaria')
	data_publicacao = models.DateTimeField(auto_now_add=True)
	data_inicio_visibilidade = models.DateTimeField(blank=True, null=True)
	data_fim_visibilidade = models.DateTimeField(blank=True, null=True)
	ativo = models.BooleanField(default=True)
	
	class Meta:
		verbose_name = 'Aviso'
		verbose_name_plural = 'Avisos'
		ordering = ['-data_publicacao']
	
	def __str__(self):
		return self.titulo


class EventoAcademico(models.Model):
	titulo = models.CharField(max_length=200)
	descricao = models.TextField(blank=True)
	data_evento = models.DateTimeField()
	criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
	tipo_usuario_criador = models.CharField(max_length=20, choices=[
		('professor', 'Professor'),
		('coordenacao', 'Coordenação'),
		('secretaria', 'Secretaria'),
	], default='secretaria')
	data_criacao = models.DateTimeField(auto_now_add=True)
	ativo = models.BooleanField(default=True)
	local = models.CharField(max_length=255, blank=True)
	
	class Meta:
		verbose_name = 'Evento Acadêmico'
		verbose_name_plural = 'Eventos Acadêmicos'
		ordering = ['data_evento']
	
	def __str__(self):
		return f"{self.titulo} ({self.data_evento.strftime('%d/%m/%Y')})"
