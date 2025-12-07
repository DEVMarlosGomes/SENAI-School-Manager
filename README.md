🎓 SENAI School Manager - Sistema de Gestão Escolar Avançado

💡 Descrição do Projeto
O SENAI School Manager é uma plataforma escolar web robusta e unificada, desenvolvida para centralizar e otimizar todas as operações administrativas, acadêmicas e financeiras da Escola SENAI. O sistema foi concebido para substituir múltiplos sistemas legados, eliminando retrabalho, inconsistência de dados e a experiência fragmentada do usuário.

A plataforma oferece dashboards específicos para cada perfil (Role), garantindo que alunos, professores, coordenação e secretaria tenham acesso seguro e direto às ferramentas e informações mais relevantes para suas funções.

🎯 Contexto e Objetivos
Problema a Resolver
Atualmente, a gestão escolar descentralizada gera ineficiência. O projeto visa solucionar a fragmentação de dados (matrículas, notas, frequência, pagamentos) em diferentes sistemas, que resultam em erros, lentidão na gestão e sobrecarga de trabalho.

Objetivos
Centralização: Unificar a gestão de todos os dados acadêmicos, administrativos e financeiros em uma única plataforma.

Eficiência: Fornecer dashboards e ferramentas otimizadas por perfil.

Relatórios: Implementar um sistema robusto de relatórios e exportações de dados acadêmicos.

Integração: Oferecer uma API REST segura e integrações com serviços externos (como Stripe).

⚙️ Arquitetura e Tecnologias
O sistema segue uma arquitetura de três camadas (Frontend, Backend, Banco de Dados).

Backend
Componente | Tecnologia | Descrição
--- | --- | ---
Framework | Django | Principal framework Python para desenvolvimento web.
API | Django REST Framework | Usado para construir a API RESTful.
Banco de Dados | PostgreSQL / SQLite | SGBD relacional (SQLite em dev, Postgres em prod).
Pagamentos | Stripe API | Processamento de pagamentos online e webhooks.
Drivers/Libs | psycopg2, reportlab, stripe | Conexão com banco, geração de PDFs e pagamentos.

Exportar para as Planilhas
Frontend
Componente | Tecnologia | Descrição
--- | --- | ---
Estrutura | HTML, CSS, JavaScript | Linguagens fundamentais para a construção da interface.
Design/Layout | Bootstrap / Tailwind CSS | Frameworks CSS para interface moderna e responsiva.

Exportar para as Planilhas
🧩 Módulos e Funcionalidades
O sistema é dividido nos seguintes módulos principais, acessíveis de acordo com a Role do usuário:

Gestão de Usuários e Perfis:
* Cadastros e autenticação de Alunos, Professores, Coordenação e Secretaria.
* Definição e gerenciamento de permissões (Secretaria é o nível máximo).

Cadastro Escolar:
* Gestão de Cursos, Disciplinas e Turmas (com validação da Coordenação).

Gestão Acadêmica:
* Lançamento de Notas, Faltas e Observações (Professores).
* Consulta de Histórico Escolar (Alunos).
* Finalização de Boletins (Coordenação).

Gestão Financeira (Novo):
* Geração de cobranças manuais pela Secretaria.
* Pagamento online integrado via Stripe (Checkout transparente).
* Atualização automática de status via Webhook (Pendente → Pago).
* Histórico de pagamentos para Alunos.

Dashboards Específicos:
* Visão consolidada de desempenho, frequência e financeiro para Alunos.
* Visão de turmas e relatórios para Professores.
* Visão de validações pendentes para Coordenação.

Relatórios e Exportações:
* Geração de relatórios acadêmicos e administrativos em formatos variados (PDF via ReportLab, CSV).

📊 Modelo de Dados (Visão Geral)
O sistema é baseado em um modelo relacional que garante a integridade dos dados, com destaque para a segregação de responsabilidades entre as entidades.

Entidade Principal | Relacionamento Chave | Responsabilidade
--- | --- | ---
Usuário / Perfil | 1:1 com Aluno, Professor, etc. | Define o nível de acesso e permissões (Role).
Turma | N:1 com Curso; 1:N com Aluno. | Estrutura operacional do ensino.
Histórico Escolar | N:1 com Aluno e Disciplina. | Armazena dados de nota, média e frequência.
Pagamento | N:1 com Aluno. | Controle de cobranças, valores e integração Stripe.
Boletim | N:1 com Turma. | Consolidação final de resultados.

Exportar para as Planilhas
🤝 Colaboradores

Isabella Oliveira

Leonardo Silva

Marlos Gomes

Matheus Rodrigues

Romulo Famiglietti

Este projeto está em desenvolvimento ativo. Para contribuir, clone o repositório e consulte a Documentação Técnica e Funcional completa.

https://bird-toothpaste-81f.notion.site/Documenta-o-Sistema-de-Gest-o-Escolar-Avan-ado-SENAI-School-Manager-2a595238c1de808c8d64d80f480810dc
