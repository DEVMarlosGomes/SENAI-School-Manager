from django import forms
from .models import Aluno  # 'Matricula' foi removido porque não existe no novo models.py
from django.contrib.auth.models import User

# NOTA: Estas são versões básicas dos seus formulários para
# corrigir o Import Error. A lógica interna (para criar User, etc.)
# precisará ser ajustada depois das migrações.

class AlunoForm(forms.ModelForm):
    # Campos do User que queremos no formulário de *criação*
    first_name = forms.CharField(max_length=100, label="Primeiro Nome")
    last_name = forms.CharField(max_length=100, label="Sobrenome")
    email = forms.EmailField(label="Email")
    username = forms.CharField(max_length=150, label="Nome de Usuário (Login)")
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")

    class Meta:
        model = Aluno
        # Definimos os campos que vêm do modelo Aluno
        fields = [
            'RA_aluno', 'RG_aluno', 'data_nascimento', 'genero', 'etinia', 
            'deficiencia', 'estado_civil', 'conclusao_EM', 
            'cod_endereco', 'responsavel_legal'
        ]

    def __init__(self, *args, **kwargs):
        super(AlunoForm, self).__init__(*args, **kwargs)
        # Ajustar para não obrigar campos que podem ser nulos
        self.fields['conclusao_EM'].required = False
        self.fields['etinia'].required = False
        self.fields['deficiencia'].required = False
        self.fields['cod_endereco'].required = False
        self.fields['responsavel_legal'].required = False

class AlunoEditForm(forms.ModelForm):
    # Campos do User que queremos no formulário de *edição*
    first_name = forms.CharField(max_length=100, label="Primeiro Nome")
    last_name = forms.CharField(max_length=100, label="Sobrenome")
    email = forms.EmailField(label="Email")
    username = forms.CharField(max_length=150, label="Nome de Usuário (Login)", disabled=True)

    class Meta:
        model = Aluno
        # Em edição, podemos querer editar a turma e o status
        fields = [
            'RA_aluno', 'RG_aluno', 'data_nascimento', 'genero', 'etinia', 
            'deficiencia', 'estado_civil', 'conclusao_EM', 'status_matricula',
            'turma_atual', 'cod_endereco', 'responsavel_legal'
        ]
    
    def __init__(self, *args, **kwargs):
        # Pré-popula os campos do User quando o formulário é carregado
        instance = kwargs.get('instance')
        if instance:
            initial = kwargs.get('initial', {})
            initial['first_name'] = instance.user.first_name
            initial['last_name'] = instance.user.last_name
            initial['email'] = instance.user.email
            initial['username'] = instance.user.username
            kwargs['initial'] = initial
            
        super(AlunoEditForm, self).__init__(*args, **kwargs)
        # Ajustar para não obrigar campos que podem ser nulos
        self.fields['conclusao_EM'].required = False
        self.fields['etinia'].required = False
        self.fields['deficiencia'].required = False
        self.fields['turma_atual'].required = False
        self.fields['cod_endereco'].required = False
        self.fields['responsavel_legal'].required = False