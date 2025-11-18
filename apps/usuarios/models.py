# apps/usuarios/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """
    Modelo de perfil do usuário com informações adicionais
    """
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
    """
    Modelo para armazenar registros (cadastros) pendentes de aprovação do admin
    Inclui campos de endereço preenchidos via API ViaCEP
    """
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

    # ==================== INFORMAÇÕES PESSOAIS ====================
    primeiro_nome = models.CharField(max_length=150, verbose_name='Primeiro Nome')
    sobrenome = models.CharField(max_length=150, verbose_name='Sobrenome')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    username = models.CharField(max_length=150, unique=True, verbose_name='Nome de Usuário')
    telefone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefone')
    cpf = models.CharField(max_length=14, blank=True, null=True, unique=True, verbose_name='CPF')
    
    # ==================== ENDEREÇO (VIACEP) ====================
    cep = models.CharField(max_length=9, blank=True, null=True, verbose_name='CEP')
    logradouro = models.CharField(max_length=255, blank=True, null=True, verbose_name='Logradouro')
    numero = models.CharField(max_length=30, blank=True, null=True, verbose_name='Número')
    bairro = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bairro')
    cidade = models.CharField(max_length=80, blank=True, null=True, verbose_name='Cidade')
    estado = models.CharField(max_length=2, blank=True, null=True, verbose_name='Estado (UF)')
    
    # ==================== TIPO E STATUS ====================
    tipo_solicitado = models.CharField(
        max_length=20, 
        choices=TIPOS_PERFIL, 
        verbose_name='Tipo de Perfil Solicitado'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pendente',
        verbose_name='Status da Solicitação'
    )
    
    # ==================== TIMESTAMPS ====================
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Solicitação')
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name='Data de Aprovação/Rejeição')
    motivo_rejeicao = models.TextField(blank=True, null=True, verbose_name='Motivo da Rejeição')
    
    # ==================== ADMIN RESPONSÁVEL ====================
    aprovado_por = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        verbose_name='Aprovado/Rejeitado por',
        related_name='registros_processados'
    )
    
    class Meta:
        verbose_name = 'Registro Pendente'
        verbose_name_plural = 'Registros Pendentes'
        ordering = ['-data_solicitacao']
        db_table = 'usuarios_pending_registration'

    def __str__(self):
        return f'{self.primeiro_nome} {self.sobrenome} ({self.get_tipo_solicitado_display()}) - {self.get_status_display()}'
    
    def get_nome_completo(self):
        """Retorna o nome completo do solicitante"""
        return f'{self.primeiro_nome} {self.sobrenome}'
    
    def get_endereco_completo(self):
        """Retorna o endereço completo formatado"""
        if self.logradouro and self.numero:
            partes = [
                f'{self.logradouro}, {self.numero}',
                self.bairro,
                f'{self.cidade}/{self.estado}' if self.cidade and self.estado else None,
                f'CEP: {self.cep}' if self.cep else None
            ]
            return ' - '.join([p for p in partes if p])
        return 'Endereço não informado'

    def aprovar(self, admin_user):
        """
        Cria um User e Profile a partir do registro aprovado
        Inclui dados de endereço no Profile
        """
        from django.utils import timezone
        
        if self.status != 'pendente':
            raise ValueError(
                f"Apenas registros 'pendente' podem ser aprovados. "
                f"Status atual: {self.status}"
            )
        
        # Verifica se já existe um usuário com esse username ou email
        if User.objects.filter(username=self.username).exists():
            raise ValueError(f"Usuário '{self.username}' já existe.")
        
        if User.objects.filter(email=self.email).exists():
            raise ValueError(f"E-mail '{self.email}' já está cadastrado.")
        
        # Criar User
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            first_name=self.primeiro_nome,
            last_name=self.sobrenome,
            is_active=True  # Usuário ativo imediatamente
        )
        
        # Monta o endereço completo para o campo 'endereco' do Profile
        endereco_completo = self.get_endereco_completo()
        
        # Criar Profile
        Profile.objects.create(
            user=user,
            tipo=self.tipo_solicitado,
            telefone=self.telefone if self.telefone else '',
            cpf=self.cpf if self.cpf else None,
            endereco=endereco_completo
        )
        
        # Marcar como aprovado
        self.status = 'aprovado'
        self.data_aprovacao = timezone.now()
        self.aprovado_por = admin_user
        self.save()
        
        return user

    def rejeitar(self, admin_user, motivo=''):
        """
        Rejeita o registro com motivo
        """
        from django.utils import timezone
        
        if self.status != 'pendente':
            raise ValueError(
                f"Apenas registros 'pendente' podem ser rejeitados. "
                f"Status atual: {self.status}"
            )
        
        self.status = 'rejeitado'
        self.data_aprovacao = timezone.now()
        self.motivo_rejeicao = motivo
        self.aprovado_por = admin_user
        self.save()


# ==================== SIGNALS ====================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal para criar Profile automaticamente quando um User é criado
    (Desabilitado para evitar conflitos com admin inline)
    """
    if created:
        # Não criar automaticamente o Profile aqui quando o usuário é criado via admin
        # porque o admin já fornece um Inline para criar/editar o Profile e isso
        # causava UNIQUE constraint (dupla criação). Removido para evitar conflito.
        # Se for necessário garantir que todos os users tenham profile, use
        # lógica explícita em fluxos de criação (registro, scripts ou overrides do admin).
        return


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal para salvar o Profile quando o User é salvo
    """
    # Salva o profile existente, se houver. Se não existir, ignora.
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        pass
