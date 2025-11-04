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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
