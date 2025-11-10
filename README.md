🎓 SENAI School Manager - Sistema de Gestão Escolar Avançado

<a href="#-descrição-do-projeto">Descrição</a> •
<a href="#-contexto-e-objetivos">Objetivos</a> •
<a href="#-arquitetura-e-tecnologias">Tecnologias</a> •
<a href="#-módulos-e-funcionalidades">Módulos</a> •
<a href="#-modelo-de-dados-visão-geral">Modelo de Dados</a>


💡 Descrição do Projeto
O SENAI School Manager é uma plataforma escolar web robusta e unificada, desenvolvida para centralizar e otimizar todas as operações administrativas e acadêmicas da Escola SENAI. O sistema foi concebido para substituir múltiplos sistemas legados, eliminando retrabalho, inconsistência de dados e a experiência fragmentada do usuário.

A plataforma oferece dashboards específicos para cada perfil (Role), garantindo que alunos, professores, coordenação e secretaria tenham acesso seguro e direto às ferramentas e informações mais relevantes para suas funções.

🎯 Contexto e Objetivos
Problema a Resolver
Atualmente, a gestão escolar descentralizada gera ineficiência. O projeto visa solucionar a fragmentação de dados (matrículas, notas, frequência) em diferentes sistemas, que resultam em erros, lentidão na gestão e sobrecarga de trabalho.

Objetivos
Centralização: Unificar a gestão de todos os dados acadêmicos e administrativos em uma única plataforma.

Eficiência: Fornecer dashboards e ferramentas otimizadas por perfil.

Relatórios: Implementar um sistema robusto de relatórios e exportações de dados acadêmicos.

Integração: Oferecer uma API REST segura para futuras integrações com outros sistemas.

⚙️ Arquitetura e Tecnologias
O sistema segue uma arquitetura de três camadas (Frontend, Backend, Banco de Dados).

Backend
Componente	Tecnologia	Descrição
Framework	Django	Principal framework Python para desenvolvimento web.
API	Django REST Framework	Usado para construir a API RESTful para comunicação entre o frontend e o backend.
Banco de Dados	PostgreSQL	SGBD relacional robusto, escolhido pela sua confiabilidade e escalabilidade.
Drivers/Libs	psycopg2, django-filter, django-import-export	Bibliotecas essenciais para conexão, filtragem e manipulação de dados.

Exportar para as Planilhas
Frontend
Componente	Tecnologia	Descrição
Estrutura	HTML, CSS, JavaScript	Linguagens fundamentais para a construção da interface.
Design/Layout	Bootstrap / Tailwind CSS	Frameworks CSS utilizados para criar uma interface de usuário moderna e responsiva.

Exportar para as Planilhas
🧩 Módulos e Funcionalidades
O sistema é dividido nos seguintes módulos principais, acessíveis de acordo com a Role do usuário:

Gestão de Usuários e Perfis:

Cadastros e autenticação de Alunos, Professores, Coordenação e Secretaria.

Definição e gerenciamento de permissões (Secretaria é o nível máximo).

Cadastro Escolar:

Gestão de Cursos, Disciplinas e Turmas (com validação da Coordenação).

Gestão Acadêmica:

Lançamento de Notas, Faltas e Observações (Professores).

Consulta de Histórico Escolar (Alunos).

Finalização de Boletins (Coordenação).

Dashboards Específicos:

Visão consolidada de desempenho e frequência para Alunos.

Visão de turmas e relatórios para Professores.

Visão de validações pendentes para Coordenação.

Relatórios e Exportações:

Geração de relatórios acadêmicos e administrativos em formatos variados (ex: PDF, CSV).

API REST:

Interface para consumo de dados por sistemas externos.

📊 Modelo de Dados (Visão Geral)
O sistema é baseado em um modelo relacional que garante a integridade dos dados, com destaque para a segregação de responsabilidades entre as entidades.

Entidade Principal	Relacionamento Chave	Responsabilidade
Usuário / Perfil	1:1 com Aluno, Professor, Coordenação, etc.	Define o nível de acesso e permissões (Role).
Turma	N:1 com Curso; 1:N com Aluno (max. 40).	Estrutura operacional do ensino.
Histórico Escolar	N:1 com Aluno e Disciplina.	Armazena dados de nota, média, frequência e período.
Boletim	N:1 com Turma; Finalizado por Coordenação.	Consolidação final de resultados.

Exportar para as Planilhas
🤝 Colaboradores

Isabella Oliveira

Leonardo Santos

Marlos Gomes

Matheus Rodrigues

https://bird-toothpaste-81f.notion.site/Documenta-o-Sistema-de-Gest-o-Escolar-Avan-ado-SENAI-School-Manager-2a595238c1de808c8d64d80f480810dc

Romulo Famiglietti

Este projeto está em desenvolvimento ativo. Para contribuir, clone o repositório e consulte a Documentação Técnica e Funcional completa.
