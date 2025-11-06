from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Aluno, Matricula
from apps.usuarios.models import Profile

class AlunoEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='Nome')
    last_name = forms.CharField(max_length=150, label='Sobrenome')
    email = forms.EmailField(label='E-mail')
    cpf = forms.CharField(max_length=14, label='CPF')
    telefone = forms.CharField(max_length=15, label='Telefone')
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    endereco = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Endereço'
    )
    status = forms.ChoiceField(
        choices=Matricula.STATUS_CHOICES,
        label='Status da Matrícula'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['cpf'].initial = self.instance.profile.cpf
            self.fields['telefone'].initial = self.instance.profile.telefone
            self.fields['data_nascimento'].initial = self.instance.profile.data_nascimento
            self.fields['endereco'].initial = self.instance.profile.endereco
            if hasattr(self.instance, 'aluno'):
                matricula = self.instance.aluno.matriculas.first()
                if matricula:
                    self.fields['status'].initial = matricula.status

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = user.profile
            profile.cpf = self.cleaned_data['cpf']
            profile.telefone = self.cleaned_data['telefone']
            profile.data_nascimento = self.cleaned_data['data_nascimento']
            profile.endereco = self.cleaned_data['endereco']
            profile.save()

            matricula = user.aluno.matriculas.first()
            if matricula:
                matricula.status = self.cleaned_data['status']
                matricula.save()
        return user

class AlunoForm(UserCreationForm):
    cpf = forms.CharField(max_length=14, label='CPF')
    telefone = forms.CharField(max_length=15, label='Telefone')
    data_nascimento = forms.DateField(
        label='Data de Nascimento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    endereco = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Endereço'
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Criar ou atualizar perfil
            profile = Profile.objects.get_or_create(user=user)[0]
            profile.tipo = 'aluno'
            profile.cpf = self.cleaned_data.get('cpf')
            profile.telefone = self.cleaned_data.get('telefone')
            profile.data_nascimento = self.cleaned_data.get('data_nascimento')
            profile.endereco = self.cleaned_data.get('endereco')
            profile.save()
            
            # Criar registro de aluno
            matricula = f'ALU{user.id:06d}'
            Aluno.objects.create(user=user, matricula=matricula)
        return user