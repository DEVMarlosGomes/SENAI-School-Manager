from django import forms
from django.forms import modelformset_factory
from .models import Aluno, Historico, RegistroOcorrencia
from django.contrib.auth.models import User

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

# Novo Form para o Diário de Classe
class DiarioClasseForm(forms.ModelForm):
    class Meta:
        model = Historico
        # Vamos permitir editar Nota Final e Total de Faltas
        fields = ['nota_final', 'total_faltas']
        widgets = {
            'nota_final': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10, 'step': 0.01}),
            'total_faltas': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

# Factory que cria o conjunto de formulários
DiarioClasseFormSet = modelformset_factory(
    Historico,
    form=DiarioClasseForm,
    extra=0,  # Não queremos linhas vazias extras, apenas os alunos existentes
    can_delete=False
)

class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = RegistroOcorrencia
        fields = ['tipo_ocorrencia', 'descricao']
        labels = {
            'tipo_ocorrencia': 'Tipo',
            'descricao': 'Observações Detalhadas'
        }
        widgets = {
            'tipo_ocorrencia': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva o que aconteceu...'}),
        }