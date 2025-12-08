# 🎓 SENAI School Manager - Sistema de Gestão Escolar Avançado

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-092E20.svg?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)


> Uma plataforma escolar web robusta e unificada, desenvolvida para centralizar e otimizar todas as operações administrativas, acadêmicas e financeiras da Escola SENAI.

---

## 💡 Sobre o Projeto

O **SENAI School Manager** foi concebido para substituir múltiplos sistemas legados, eliminando retrabalho, inconsistência de dados e a experiência fragmentada do usuário. A plataforma oferece dashboards específicos para cada perfil (Aluno, Professor, Coordenação e Secretaria), garantindo acesso seguro e direto às ferramentas mais relevantes.

### 🎯 Objetivos Principais

* **Centralização:** Unificar dados de matrículas, notas, frequência e pagamentos.
* **Eficiência:** Dashboards otimizados por perfil de usuário.
* **Relatórios:** Sistema robusto de exportação de dados acadêmicos (PDF/CSV).
* **Integração:** API REST segura e pagamentos via Stripe.

---

## 🌐 Deploy

Você pode acessar uma versão funcional do sistema através do link abaixo:

👉 **[SENAI School Manager](https://leomeriva.pythonanywhere.com/)**

<img width="347" height="433" alt="image" src="https://github.com/user-attachments/assets/ee26a771-2e18-4af3-9408-89a1f3ac5053" />

---

## ⚙️ Tecnologias Utilizadas

Este projeto utiliza uma arquitetura MVC (Model-View-Controller) adaptada pelo Django (MVT).

| Componente | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+ / Django 5.2+ | Core do sistema e lógica de negócios. |
| **API** | Django REST Framework | API RESTful para integrações externas. |
| **Banco de Dados** | SQLite / PostgreSQL | SQLite (Dev) e PostgreSQL/Supabase (Prod). |
| **Frontend** | HTML5, CSS3, JS | Bootstrap/Tailwind para responsividade. |
| **Pagamentos** | Stripe API | Processamento de pagamentos e Webhooks. |
| **Relatórios** | ReportLab | Geração dinâmica de PDFs acadêmicos. |

---

## 📂 Estrutura do Projeto

A lógica de negócio é segregada em aplicações específicas (`apps`) para facilitar a escalabilidade.

```bash
SENAI-SCHOOL-MANAGER
├── apps/
│   ├── academico/       # Gestão acadêmica (Notas, Cursos)
│   ├── dashboards/      # Lógica dos painéis visuais
│   ├── payments/        # Integração Stripe e lógica financeira
│   ├── relatorios/      # Geradores de PDF/CSV
│   └── usuarios/        # Gestão de usuários e autenticação
├── core/                # Funcionalidades base/globais
├── school_manager/      # Configurações do projeto (Settings, URLs)
├── static/
│   ├── css/             # Folhas de estilo
│   ├── img/             # Imagens e assets
│   └── js/              # Scripts JavaScript
├── templates/
│   ├── academico/       # Templates das views acadêmicas
│   ├── dashboards/      # Templates dos painéis
│   ├── includes/        # Fragmentos reutilizáveis (navbars, footers)
│   ├── pagamentos/      # Telas de pagamento e checkout
│   ├── registration/    # Telas de login/registro (Django Auth)
│   ├── relatorios/      # Templates de relatórios
│   ├── usuarios/        # Telas de perfil e gestão de usuários
│   ├── base.html        # Template base principal
│   ├── base_home.html   # Template da landing page
│   └── home.html        # Página inicial
├── manage.py            # Utilitário CLI do Django
└── requirements.txt     # Lista de dependências
```

---

## 🧩 Módulos e Funcionalidades

| Módulo | Acesso | Funcionalidades |
| :--- | :--- | :--- |
| **Usuários** | Todos | Login, Logout, Recuperação de senha, Gestão de Perfil. |
| **Acadêmico** | Prof/Coord/Aluno | Diário de classe, lançamento de notas, frequência, grade curricular. |
| **Dashboards** | Todos | Visão geral, gráficos de desempenho, alertas e notificações. |
| **Payments** | Secr/Aluno | Geração de cobranças, histórico financeiro, checkout transparente. |
| **Relatórios** | Coord/Secr | Boletins, Histórico Escolar, Lista de Presença, Relatórios Financeiros. |

---

## 🚀 Instalação e Configuração

Siga os passos abaixo para rodar o projeto localmente.

### Pré-requisitos

*   Python 3.11+
*   Git

### 1. Clonar o Repositório

```bash
git clone https://github.com/DEVMarlosGomes/SENAI-School-Manager.git
cd SENAI-School-Manager
```

### 2. Configurar o Ambiente Virtual

Recomendamos isolar as dependências do projeto.

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar Banco de Dados

Aplique as migrações para criar as tabelas no SQLite (padrão de desenvolvimento).

```bash
python manage.py migrate
```

### 5. Criar Superusuário (Admin)

Crie um acesso administrativo para gerenciar o sistema.

```bash
python manage.py createsuperuser
```

### 6. Popular o Banco (Opcional)

Utilize o script de seed para gerar dados de teste (alunos, cursos, notas).

```bash
python manage.py seed_database
```

### 7. Executar o Servidor

```bash
python manage.py runserver
```
O sistema estará acessível em: `http://127.0.0.1:8000/`

---

## 📄 Documentação Completa

Para detalhes técnicos sobre a modelagem de dados e regras de negócio:

📘 [Notion: Documentação Oficial SENAI School Manager](https://bird-toothpaste-81f.notion.site/Documenta-o-Sistema-de-Gest-o-Escolar-Avan-ado-SENAI-School-Manager-2a595238c1de808c8d64d80f480810dc?pvs=74)

---

## 🤝 Colaboradores

Equipe responsável pelo desenvolvimento e manutenção:

| Nome |
| :--- |
| **Isabella Oliveira** |
| **Leonardo Silva** |
| **Marlos Gomes** |
| **Matheus Rodrigues** |
| **Romulo Famiglietti** |
