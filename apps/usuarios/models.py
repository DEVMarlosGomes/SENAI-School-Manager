from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

class Profile(models.Model):
    TIPOS_PERFIL = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
        ('coordenacao', 'Coordenação'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tipo = models.CharField(max_length=20, choices=TIPOS_PERFIL)
    
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True)
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=30, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=80, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    
    endereco = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.user.username} - {self.get_tipo_display()}'
    
    def save(self, *args, **kwargs):
        parts = [p for p in [self.logradouro, self.numero, self.bairro, self.cidade, self.estado] if p]
        self.endereco = " - ".join(parts) if parts else self.endereco
        super().save(*args, **kwargs)

class DocumentoUsuario(models.Model):
    TIPOS_DOC = (
        ('rg', 'RG / Cartão Cidadão'),
        ('cpf', 'CPF'),
        ('comprovante_residencia', 'Comprovativo de Morada'),
        ('historico', 'Histórico Escolar'),
        ('foto', 'Foto de Perfil'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=30, choices=TIPOS_DOC)
    arquivo = models.FileField(upload_to='documentos_usuarios/%Y/%m/')
    data_upload = models.DateTimeField(auto_now_add=True)
    validado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.user.username}"

class PendingRegistration(models.Model):
    STATUS_CHOICES = (
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    )
    TIPOS_PERFIL = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
        ('coordenacao', 'Coordenação'),
    )

    primeiro_nome = models.CharField(max_length=150)
    sobrenome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    
    # Campo Essencial
    senha = models.CharField(max_length=128, blank=True, null=True)
    
    telefone = models.CharField(max_length=15, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True)
    
    # Endereço
    cep = models.CharField(max_length=9, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=30, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=80, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    
    tipo_solicitado = models.CharField(max_length=20, choices=TIPOS_PERFIL)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    # Campos que o Admin acusou estarem faltando:
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    motivo_rejeicao = models.TextField(blank=True, null=True)
    aprovado_por = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='registros_processados'
    )
    
    class Meta:
        verbose_name = 'Registro Pendente'
        verbose_name_plural = 'Registros Pendentes'
        ordering = ['-data_solicitacao']
        db_table = 'usuarios_pending_registration'

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome}'
    
    def get_nome_completo(self):
        return f'{self.primeiro_nome} {self.sobrenome}'

    def get_endereco_completo(self):
        parts = [p for p in [self.logradouro, self.numero, self.bairro, self.cidade, self.estado] if p]
        return " - ".join(parts) if parts else "Endereço não informado"

    def aprovar(self, admin_user):
        from apps.academico.models import Aluno, Professor, Secretaria, Coordenacao
        
        if self.status != 'pendente':
            raise ValueError("Apenas registros pendentes podem ser aprovados.")
        
        with transaction.atomic():
            user, created = User.objects.get_or_create(username=self.username, defaults={
                'email': self.email,
                'first_name': self.primeiro_nome,
                'last_name': self.sobrenome,
                'is_active': True
            })
            
            if self.senha:
                user.set_password(self.senha)
                user.save()
            
            if self.tipo_solicitado in ['coordenacao', 'secretaria']:
                user.is_staff = True
                user.save()

            Profile.objects.update_or_create(user=user, defaults={
                'tipo': self.tipo_solicitado,
                'telefone': self.telefone or '',
                'cpf': self.cpf,
                'cep': self.cep, 'logradouro': self.logradouro,
                'numero': self.numero, 'bairro': self.bairro,
                'cidade': self.cidade, 'estado': self.estado,
                'endereco': self.get_endereco_completo()
            })
            
            if self.tipo_solicitado == 'aluno':
                Aluno.objects.get_or_create(user=user, defaults={'RA_aluno': self.username})
            elif self.tipo_solicitado == 'professor':
                Professor.objects.get_or_create(user=user)
            elif self.tipo_solicitado == 'secretaria':
                Secretaria.objects.get_or_create(user=user)
            elif self.tipo_solicitado == 'coordenacao':
                Coordenacao.objects.get_or_create(user=user)
            
            self.status = 'aprovado'
            self.data_aprovacao = models.functions.Now() # Usando Now() do DB para evitar import timezone
            self.aprovado_por = admin_user
            self.save()
            return user

    def rejeitar(self, admin_user, motivo=''):
        self.status = 'rejeitado'
        self.data_aprovacao = models.functions.Now()
        self.motivo_rejeicao = motivo
        self.aprovado_por = admin_user
        self.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass