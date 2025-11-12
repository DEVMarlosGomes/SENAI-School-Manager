"""
Testes para funcionalidade de logout do sistema SENAI School Manager.
Verifica presença do botão de logout no navbar e comportamento do endpoint /contas/logout/.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class LogoutTests(TestCase):
    """Testes relacionados ao logout de usuários."""
    
    def setUp(self):
        """Configuração inicial dos testes."""
        self.client = Client()
        # Criar um usuário de teste
        self.user = User.objects.create_user(
            username='aluno_test',
            password='senha123',
            first_name='Aluno',
            last_name='Teste'
        )

    def test_logout_link_presente_navbar(self):
        """Verifica se o link de logout está presente no navbar quando logado."""
        # Fazer login
        self.client.login(username='aluno_test', password='senha123')
        
        # Buscar página inicial (que tem o navbar)
        response = self.client.get(reverse('home'))
        
        # Verificar status 200 e presença do HTML do botão logout
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="#" data-bs-toggle="modal" data-bs-target="#logoutModal"')
        self.assertContains(response, 'Sair</a>')

    def test_logout_requer_post(self):
        """Verifica se o endpoint de logout requer método POST."""
        # Fazer login
        self.client.login(username='aluno_test', password='senha123')
        
        # Tentar logout via GET (deve falhar)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        
        # Confirmar que ainda está logado
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.first_name)

    def test_logout_post_sucesso(self):
        """Verifica se o POST para logout funciona e redireciona corretamente."""
        # Fazer login
        self.client.login(username='aluno_test', password='senha123')
        
        # Fazer logout via POST
        response = self.client.post(reverse('logout'))
        
        # Verificar redirecionamento para home
        self.assertRedirects(response, reverse('home'))
        
        # Confirmar que está deslogado
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        # Verifica se o nome completo do usuário não está presente
        self.assertNotContains(response, f"{self.user.first_name} {self.user.last_name}")

    def test_modal_logout_presente(self):
        """Verifica se o modal de confirmação de logout está presente quando logado."""
        # Fazer login
        self.client.login(username='aluno_test', password='senha123')
        
        # Buscar página inicial
        response = self.client.get(reverse('home'))
        
        # Verificar presença do modal e seus elementos
        self.assertContains(response, 'id="logoutModal"')
        self.assertContains(response, 'Confirmação de saída')
        self.assertContains(response, 'method="post"')
        self.assertContains(response, 'action="%s"' % reverse('logout'))