from django.db import models
from django.contrib.auth.models import User

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_aluno')
    matricula = models.CharField(max_length=20, unique=True)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.matricula})"

class Curso(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.nome

class Professor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    disciplinas = models.ManyToManyField('Disciplina')
    
    def __str__(self):
        return self.user.get_full_name()

class Disciplina(models.Model):
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.nome