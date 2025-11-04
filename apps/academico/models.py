from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Curso(models.Model):
    NIVEL_CHOICES = (
        ('tecnico', 'Técnico'),
        ('superior', 'Superior'),
        ('aperfeicoamento', 'Aperfeiçoamento'),
    )
    
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES)
    duracao = models.IntegerField(help_text='Duração em meses')
    ativo = models.BooleanField(default=True)
    imagem = models.ImageField(upload_to='cursos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Turma(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT)
    codigo = models.CharField(max_length=20, unique=True)
    ano = models.IntegerField()
    semestre = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(2)])
    professor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        limit_choices_to={'profile__tipo': 'professor'}
    )
    data_inicio = models.DateField()
    data_fim = models.DateField()
    vagas = models.IntegerField()
    ativa = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        ordering = ['-ano', '-semestre', 'codigo']

    def __str__(self):
        return f'{self.codigo} - {self.curso.nome} ({self.ano}.{self.semestre})'

class Aluno(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__tipo': 'aluno'}
    )
    matricula = models.CharField(max_length=20, unique=True)
    turmas = models.ManyToManyField(Turma, through='Matricula')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        ordering = ['user__first_name']

    def __str__(self):
        return f'{self.matricula} - {self.user.get_full_name()}'

class Matricula(models.Model):
    STATUS_CHOICES = (
        ('ativa', 'Ativa'),
        ('trancada', 'Trancada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
    )

    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='matriculas')
    turma = models.ForeignKey(Turma, on_delete=models.PROTECT, related_name='matriculas')
    data_matricula = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['aluno', 'turma']
        ordering = ['-data_matricula']

    def __str__(self):
        return f'{self.aluno} - {self.turma}'

class Nota(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    data = models.DateField()
    observacao = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        ordering = ['-data']

    def __str__(self):
        return f'{self.matricula.aluno} - {self.descricao}: {self.valor}'

class Frequencia(models.Model):
    matricula = models.ForeignKey(Matricula, on_delete=models.CASCADE)
    data = models.DateField()
    presenca = models.BooleanField(default=True)
    justificativa = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Frequência'
        verbose_name_plural = 'Frequências'
        unique_together = ['matricula', 'data']
        ordering = ['-data']

    def __str__(self):
        status = 'Presente' if self.presenca else 'Ausente'
        return f'{self.matricula.aluno} - {self.data}: {status}'
