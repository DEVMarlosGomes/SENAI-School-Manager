from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# #############################################################################
# ### 1. Entidades de Base (Endereço, Telefone, Disciplina)
# #############################################################################

class Endereco(models.Model):
    cep = models.CharField(max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'
        db_table = 'academico_endereco' # Nome explícito da tabela

    def __str__(self):
        return f"{self.logradouro}, {self.numero} - {self.cidade}"

class Telefone(models.Model):
    num_telefone = models.CharField(max_length=20)
    tipo_telefone = models.CharField(max_length=20, blank=True, null=True)
    contato_principal = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Telefone'
        verbose_name_plural = 'Telefones'
        db_table = 'academico_telefone'

    def __str__(self):
        return self.num_telefone

class Disciplina(models.Model):
    cod_disciplina = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=100)
    carga_horaria = models.IntegerField(blank=True, null=True)
    ementa = models.TextField(blank=True, null=True)
    creditos = models.IntegerField(blank=True, null=True)
    status_curricular = models.CharField(max_length=50, blank=True, null=True)
    
    # Auto-relacionamento (N:1)
    pre_requisito_disciplina = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='pre_requisito_para'
    )

    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        db_table = 'academico_disciplina'

    def __str__(self):
        return f"{self.cod_disciplina} - {self.nome}"

# #############################################################################
# ### 2. Entidades de "Perfis" (Ligadas ao User)
# #############################################################################

# Nota: Usamos o 'settings.AUTH_USER_MODEL' que aponta para o 'User' do Django
# Isso implementa a "Herança" 1:1 da sua documentação.

class Coordenacao(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    registro_administrativo = models.CharField(max_length=50, unique=True)
    nivel_acesso = models.CharField(max_length=50)
    area_coordenacao = models.CharField(max_length=100, blank=True, null=True)
    data_inicio_funcao = models.DateField(blank=True, null=True)
    pode_finalizar_boletim = models.BooleanField(default=False)
    pode_aprovar_turma = models.BooleanField(default=False)
    pode_gerenciar_perfis = models.BooleanField(default=False)
    cod_endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Coordenação'
        verbose_name_plural = 'Coordenação'
        db_table = 'academico_coordenacao'

    def __str__(self):
        return self.user.get_full_name()

class Secretaria(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    registro_administrativo = models.CharField(max_length=50, unique=True)
    cargo = models.CharField(max_length=50)
    data_inicio_cargo = models.DateField(blank=True, null=True)
    pode_gerenciar_perfis = models.BooleanField(default=True)
    pode_acessar_relatorios_financeiros = models.BooleanField(default=False)
    cod_endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Secretaria'
        verbose_name_plural = 'Secretaria'
        db_table = 'academico_secretaria'

    def __str__(self):
        return self.user.get_full_name()

# #############################################################################
# ### 3. Entidades Acadêmicas (Departamento, Professor, Curso, Turma)
# #############################################################################

class Departamento(models.Model):
    nome_departamento = models.CharField(max_length=100, unique=True)
    cod_departamento = models.CharField(max_length=50, unique=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    status_ativo = models.BooleanField(default=True)
    coordenador = models.ForeignKey(Coordenacao, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'
        db_table = 'academico_departamento'

    def __str__(self):
        return self.nome_departamento

class Professor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    registro_funcional = models.CharField(max_length=50, unique=True)
    formacao = models.CharField(max_length=100)
    tipo_vinculo = models.CharField(max_length=50)
    data_contratacao = models.DateField()
    status_professor = models.CharField(max_length=20, default='Ativo')
    cod_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT) # Proteger para não apagar depto com professor
    cod_endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True)
    is_proponente_turma = models.BooleanField(default=False)
    etnia = models.CharField(max_length=50, blank=True, null=True)
    estado_civil = models.CharField(max_length=20, blank=True, null=True)
    deficiencia = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = 'Professor'
        verbose_name_plural = 'Professores'
        db_table = 'academico_professor'

    def __str__(self):
        return self.user.get_full_name()

class Curso(models.Model):
    cod_curso = models.CharField(max_length=50, unique=True)
    nome_curso = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    carga_horaria_total = models.IntegerField()
    modalidade = models.CharField(max_length=50)
    turno = models.CharField(max_length=20)
    tipo = models.CharField(max_length=50)
    data_inicio_validade = models.DateField(blank=True, null=True)
    cod_departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    credenciamento_ativo = models.BooleanField(default=True)
    
    # Relação N:M com Disciplina, usando a tabela 'CursoDisciplina'
    disciplinas = models.ManyToManyField(
        Disciplina, 
        through='CursoDisciplina',
        related_name='cursos'
    )

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        db_table = 'academico_curso'

    def __str__(self):
        return self.nome_curso

class Turma(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    periodo = models.CharField(max_length=50)
    ano_letivo = models.IntegerField()
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    capacidade_maxima = models.IntegerField(default=40)
    alunos_matriculados = models.IntegerField(default=0) # Idealmente, isso seria contado
    id_curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    status_aprovacao = models.CharField(max_length=50, default='Pendente')
    coordenacao_aprovacao = models.ForeignKey(Coordenacao, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Turma'
        verbose_name_plural = 'Turmas'
        db_table = 'academico_turma'

    def __str__(self):
        return f"{self.nome} ({self.id_curso.nome_curso})"

# #############################################################################
# ### 4. Entidades do Aluno (Responsavel, Aluno)
# #############################################################################

class Responsavel(models.Model):
    cpf = models.CharField(max_length=15, unique=True)
    nome_completo_responsavel = models.CharField(max_length=150)
    parentesco = models.CharField(max_length=50, blank=True, null=True)
    contato_principal = models.CharField(max_length=100, blank=True, null=True)
    responsavel_financeiro = models.BooleanField(default=False)
    cod_endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Relação N:M com Telefone
    telefones = models.ManyToManyField(Telefone, blank=True)

    class Meta:
        verbose_name = 'Responsável'
        verbose_name_plural = 'Responsáveis'
        db_table = 'academico_responsavel'

    def __str__(self):
        return self.nome_completo_responsavel

class Aluno(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    RA_aluno = models.CharField(max_length=50, unique=True)
    RG_aluno = models.CharField(max_length=20, unique=True)
    data_nascimento = models.DateField()
    genero = models.CharField(max_length=20)
    etinia = models.CharField(max_length=50, blank=True, null=True)
    deficiencia = models.CharField(max_length=100, blank=True, null=True)
    estado_civil = models.CharField(max_length=20)
    conclusao_EM = models.DateField(blank=True, null=True)
    data_matricula = models.DateField(auto_now_add=True)
    status_matricula = models.CharField(max_length=20, default='Ativo')
    turma_atual = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True, related_name='alunos')
    cod_endereco = models.ForeignKey(Endereco, on_delete=models.SET_NULL, null=True)
    responsavel_legal = models.ForeignKey(Responsavel, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'
        db_table = 'academico_aluno'

    def __str__(self):
        return self.user.get_full_name()

# #############################################################################
# ### 5. Entidades Associativas e de Registros
# #############################################################################

class CursoDisciplina(models.Model):
    """ Tabela "through" para N:M de Curso e Disciplina """
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    periodo_curso = models.IntegerField(blank=True, null=True)
    obrigatoria = models.BooleanField(default=True)
    status_na_matriz = models.CharField(max_length=50, default='Ativo')

    class Meta:
        verbose_name = 'Disciplina do Curso'
        verbose_name_plural = 'Disciplinas do Curso'
        db_table = 'academico_curso_disciplina'
        unique_together = ('curso', 'disciplina') # Garante que a disciplina só apareça uma vez por curso

class TurmaDisciplinaProfessor(models.Model):
    """ Tabela de alocação N:M:1 """
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True)
    status_alocacao = models.CharField(max_length=50, default='Alocado')

    class Meta:
        verbose_name = 'Alocação Professor-Turma-Disciplina'
        verbose_name_plural = 'Alocações'
        db_table = 'academico_turma_disciplina_professor'
        unique_together = ('turma', 'disciplina') # Só pode ter um professor por disciplina na turma

    def __str__(self):
        return f"{self.turma.nome} - {self.disciplina.nome} - {self.professor or 'A definir'}"

class Historico(models.Model):
    id_aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='historico')
    
    # FK para a alocação, como na doc
    turma_disciplina_professor = models.ForeignKey(
        TurmaDisciplinaProfessor, 
        on_delete=models.PROTECT # Proteger o histórico se a alocação for apagada
    )
    
    nota_final = models.FloatField(blank=True, null=True)
    media_final = models.FloatField(blank=True, null=True)
    frequencia_percentual = models.FloatField(blank=True, null=True)
    total_faltas = models.IntegerField(blank=True, null=True)
    status_aprovacao = models.CharField(max_length=50, blank=True, null=True)
    periodo_realizacao = models.CharField(max_length=50) # Ex: "2024.1"
    data_lancamento = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Histórico Escolar'
        verbose_name_plural = 'Históricos Escolares'
        db_table = 'academico_historico'
        unique_together = ('id_aluno', 'turma_disciplina_professor')

    def __str__(self):
        return f"Histórico de {self.id_aluno.user.get_full_name()} em {self.turma_disciplina_professor.disciplina.nome}"

class Boletim(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE)
    periodo_referencia = models.CharField(max_length=50) # Ex: "Bimestre 1"
    data_emissao = models.DateTimeField(blank=True, null=True)
    status_boletim = models.CharField(max_length=50, default='Em Aberto')
    coordenacao_finalizou = models.ForeignKey(Coordenacao, on_delete=models.SET_NULL, null=True, blank=True)
    data_finalizacao = models.DateTimeField(blank=True, null=True)
    observacoes_coordenacao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Boletim'
        verbose_name_plural = 'Boletins'
        db_table = 'academico_boletim'

    def __str__(self):
        return f"Boletim {self.periodo_referencia} - {self.turma.nome}"

class RegistroOcorrencia(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.SET_NULL, null=True) # Professor que registrou
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, blank=True) # Turma onde ocorreu
    tipo_ocorrencia = models.CharField(max_length=50) # Ex: "Advertência", "Observação"
    descricao = models.TextField()
    data_registro = models.DateTimeField(auto_now_add=True)
    status_intervencao = models.CharField(max_length=50, default='Pendente')
    coordenacao_revisou = models.ForeignKey(Coordenacao, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        verbose_name = 'Registro de Ocorrência'
        verbose_name_plural = 'Registros de Ocorrência'
        db_table = 'academico_registro_ocorrencia'

    def __str__(self):
        return f"{self.tipo_ocorrencia} para {self.aluno.user.get_full_name()} em {self.data_registro.strftime('%Y-%m-%d')}"