from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    TIPOS_PERFIL = (
        ('aluno', 'Aluno'),
        ('professor', 'Professor'),
        ('secretaria', 'Secretaria'),
        ('coordenacao', 'Coordenação'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPOS_PERFIL)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_nascimento = models.DateField(null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, null=True)
    endereco = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

    def __str__(self):
        return f'{self.user.username} - {self.get_tipo_display()}'
    
    @property
    def is_aluno(self):
        return self.tipo == 'aluno'
    
    @property
    def is_professor(self):
        return self.tipo == 'professor'
    
    @property
    def is_secretaria(self):
        return self.tipo == 'secretaria'
    
    @property
    def is_coordenacao(self):
        return self.tipo == 'coordenacao'


class PendingRegistration(models.Model):
    """Modelo para armazenar registros (cadastros) pendentes de aprovação do admin"""
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

    # Informações de registro
    primeiro_nome = models.CharField(max_length=150)
    sobrenome = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    telefone = models.CharField(max_length=15, blank=True)
    cpf = models.CharField(max_length=14, blank=True, unique=True, null=True)
    
    # Tipo de usuário solicitado
    tipo_solicitado = models.CharField(max_length=20, choices=TIPOS_PERFIL)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    
    # Timestamps
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    motivo_rejeicao = models.TextField(blank=True, null=True)
    
    # Admin que aprovou/rejeitou
    aprovado_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        verbose_name = 'Registro Pendente'
        verbose_name_plural = 'Registros Pendentes'
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome} ({self.get_tipo_solicitado_display()}) - {self.get_status_display()}'

    def aprovar(self, admin_user):
        """Cria um User e Profile a partir do registro aprovado"""
        from django.utils import timezone
        
        if self.status != 'pendente':
            raise ValueError(f"Apenas registros 'pendente' podem ser aprovados. Status atual: {self.status}")
        
        # Criar User
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            first_name=self.primeiro_nome,
            last_name=self.sobrenome,
            is_active=True  # Usuário ativo imediatamente
        )
        
        # Criar Profile
        Profile.objects.create(
            user=user,
            tipo=self.tipo_solicitado,
            telefone=self.telefone,
            cpf=self.cpf
        )
        
        # Marcar como aprovado
        self.status = 'aprovado'
        self.data_aprovacao = timezone.now()
        self.aprovado_por = admin_user
        self.save()
        
        return user

    def rejeitar(self, admin_user, motivo=''):
        """Rejeita o registro"""
        from django.utils import timezone
        
        if self.status != 'pendente':
            raise ValueError(f"Apenas registros 'pendente' podem ser rejeitados. Status atual: {self.status}")
        
        self.status = 'rejeitado'
        self.data_aprovacao = timezone.now()
        self.motivo_rejeicao = motivo
        self.aprovado_por = admin_user
        self.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Não criar automaticamente o Profile aqui quando o usuário é criado via admin
        # porque o admin já fornece um Inline para criar/editar o Profile e isso
        # causava UNIQUE constraint (dupla criação). Removido para evitar conflito.
        # Se for necessário garantir que todos os users tenham profile, use
        # lógica explícita em fluxos de criação (registro, scripts ou overrides do admin).
        return

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Salva o profile existente, se houver. Se não existir, ignora.
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass
