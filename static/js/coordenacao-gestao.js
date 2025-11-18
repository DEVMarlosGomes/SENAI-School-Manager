/**
 * Página de Gestão - Coordenação
 * Gerencia Alunos, Turmas, Professores e Disciplinas
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Mock data
    const mockTurmas = [
        { id: 1, codigo: 'TI-2023A', nome: 'Técnico em Informática', professor: 'João Silva', vagas: 30, matriculados: 28 },
        { id: 2, codigo: 'MEC-2023B', nome: 'Técnico em Mecânica', professor: 'Maria Santos', vagas: 25, matriculados: 24 },
    ];

    const mockAlunos = [
        { id: 1, nome: 'João Silva', matricula: '2023001', turma: 'TI-2023A', status: 'ativo' },
        { id: 2, nome: 'Maria Santos', matricula: '2023002', turma: 'TI-2023A', status: 'ativo' },
        { id: 3, nome: 'Pedro Oliveira', matricula: '2023003', turma: 'MEC-2023B', status: 'pendente' },
    ];

    const mockProfessores = [
        { id: 1, nome: 'João Silva', email: 'joao@senai.br', disciplinas: 'Programação, Banco de Dados', turmas: 2 },
        { id: 2, nome: 'Maria Santos', email: 'maria@senai.br', disciplinas: 'Mecânica, Desenho Técnico', turmas: 2 },
    ];

    const mockDisciplinas = [
        { id: 1, codigo: 'PROG001', nome: 'Programação I', cargaHoraria: 80, turmas: 2 },
        { id: 2, codigo: 'BD001', nome: 'Banco de Dados', cargaHoraria: 60, turmas: 1 },
    ];

    // Preencher filtro de turmas
    const filterAlunoTurma = document.getElementById('filterAlunoTurma');
    mockTurmas.forEach(turma => {
        const option = document.createElement('option');
        option.value = turma.codigo;
        option.textContent = turma.codigo;
        filterAlunoTurma.appendChild(option);
    });

    // Preencher KPIs
    function updateKPIs() {
        const totalAlunos = mockAlunos.length;
        const ativos = mockAlunos.filter(a => a.status === 'ativo').length;
        const pendentes = mockAlunos.filter(a => a.status === 'pendente').length;
        const inativos = totalAlunos - ativos - pendentes;

        document.getElementById('kpiTotalAlunos').textContent = totalAlunos;
        document.getElementById('kpiAtivos').textContent = ativos;
        document.getElementById('kpiPendentes').textContent = pendentes;
        document.getElementById('kpiInativos').textContent = inativos;
    }

    // Renderizar tabela de alunos
    function renderAlunosTable(alunos = mockAlunos) {
        const tbody = document.getElementById('alunosTableBody');
        tbody.innerHTML = '';
        
        alunos.forEach(aluno => {
            const badgeClass = aluno.status === 'ativo' ? 'bg-success' : (aluno.status === 'pendente' ? 'bg-warning' : 'bg-danger');
            const statusText = aluno.status === 'ativo' ? 'Ativo' : (aluno.status === 'pendente' ? 'Pendente' : 'Inativo');
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${aluno.nome}</td>
                <td><span class="badge bg-light text-dark">${aluno.matricula}</span></td>
                <td>${aluno.turma}</td>
                <td><span class="badge ${badgeClass}">${statusText}</span></td>
                <td class="text-end">
                    <button class="btn btn-xs btn-outline-primary me-1"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-xs btn-outline-danger"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Renderizar cards de turmas
    function renderTurmas() {
        const container = document.getElementById('turmasContainer');
        container.innerHTML = '';
        
        mockTurmas.forEach(turma => {
            const percentualOcupacao = Math.round((turma.matriculados / turma.vagas) * 100);
            const div = document.createElement('div');
            div.className = 'col-lg-6 col-md-12 mb-3';
            div.innerHTML = `
                <div class="card shadow-sm border-0 p-4">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <h6 class="fw-bold">${turma.codigo}</h6>
                            <small class="text-muted">${turma.nome}</small>
                        </div>
                        <button class="btn btn-xs btn-outline-primary"><i class="fas fa-edit"></i></button>
                    </div>
                    <div class="row g-3">
                        <div class="col-6">
                            <p class="small text-muted mb-1">Professor</p>
                            <p class="small fw-bold">${turma.professor}</p>
                        </div>
                        <div class="col-6">
                            <p class="small text-muted mb-1">Ocupação</p>
                            <p class="small fw-bold">${turma.matriculados}/${turma.vagas}</p>
                        </div>
                    </div>
                    <div class="progress mt-2" style="height: 8px;">
                        <div class="progress-bar" style="width: ${percentualOcupacao}%;"></div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    // Renderizar tabela de professores
    function renderProfessores() {
        const tbody = document.getElementById('professoresTableBody');
        tbody.innerHTML = '';
        
        mockProfessores.forEach(prof => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${prof.nome}</td>
                <td><a href="mailto:${prof.email}">${prof.email}</a></td>
                <td>${prof.disciplinas}</td>
                <td><span class="badge bg-primary">${prof.turmas}</span></td>
                <td class="text-end">
                    <button class="btn btn-xs btn-outline-primary me-1"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-xs btn-outline-danger"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Renderizar tabela de disciplinas
    function renderDisciplinas() {
        const tbody = document.getElementById('disciplinasTableBody');
        tbody.innerHTML = '';
        
        mockDisciplinas.forEach(disc => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="badge bg-light text-dark">${disc.codigo}</span></td>
                <td>${disc.nome}</td>
                <td>${disc.cargaHoraria}h</td>
                <td><span class="badge bg-info">${disc.turmas}</span></td>
                <td class="text-end">
                    <button class="btn btn-xs btn-outline-primary me-1"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-xs btn-outline-danger"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Filtrar alunos
    document.getElementById('btnFiltrarAlunos').addEventListener('click', function() {
        const nome = document.getElementById('filterAlunoNome').value.toLowerCase();
        const status = document.getElementById('filterAlunoStatus').value;
        const turma = document.getElementById('filterAlunoTurma').value;
        
        let alunosFiltrados = mockAlunos;
        
        if (nome) {
            alunosFiltrados = alunosFiltrados.filter(a => 
                a.nome.toLowerCase().includes(nome) || a.matricula.includes(nome)
            );
        }
        if (status) {
            alunosFiltrados = alunosFiltrados.filter(a => a.status === status);
        }
        if (turma) {
            alunosFiltrados = alunosFiltrados.filter(a => a.turma === turma);
        }
        
        renderAlunosTable(alunosFiltrados);
    });

    // Modals
    let modalAluno, modalTurma, modalProfessor, modalDisciplina;
    let alunoAtual = null, turmaAtual = null, professorAtual = null, disciplinaAtual = null;

    // Inicializar modals
    if (document.getElementById('modalAluno')) {
        modalAluno = new bootstrap.Modal(document.getElementById('modalAluno'));
        modalTurma = new bootstrap.Modal(document.getElementById('modalTurma'));
        modalProfessor = new bootstrap.Modal(document.getElementById('modalProfessor'));
        modalDisciplina = new bootstrap.Modal(document.getElementById('modalDisciplina'));

        // Preencher dropdowns de turmas e professores nos modals
        const inputAlunoTurma = document.getElementById('inputAlunoTurma');
        mockTurmas.forEach(turma => {
            const option = document.createElement('option');
            option.value = turma.codigo;
            option.textContent = turma.codigo + ' - ' + turma.nome;
            inputAlunoTurma.appendChild(option);
        });

        const inputTurmaProfessor = document.getElementById('inputTurmaProfessor');
        mockProfessores.forEach(prof => {
            const option = document.createElement('option');
            option.value = prof.id;
            option.textContent = prof.nome;
            inputTurmaProfessor.appendChild(option);
        });

        // Novo Aluno
        document.getElementById('btnNovoAluno').addEventListener('click', function() {
            alunoAtual = null;
            document.getElementById('modalAlunoTitle').textContent = 'Novo Aluno';
            document.getElementById('formAluno').reset();
            modalAluno.show();
        });

        // Salvar Aluno
        document.getElementById('btnSalvarAluno').addEventListener('click', function() {
            const nome = document.getElementById('inputAlunoNome').value.trim();
            const matricula = document.getElementById('inputAlunoMatricula').value.trim();
            const turma = document.getElementById('inputAlunoTurma').value;
            const status = document.getElementById('inputAlunoStatus').value;

            if (!nome || !matricula || !turma) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }

            if (alunoAtual) {
                // Editar
                alunoAtual.nome = nome;
                alunoAtual.matricula = matricula;
                alunoAtual.turma = turma;
                alunoAtual.status = status;
            } else {
                // Novo
                const novoAluno = {
                    id: Math.max(...mockAlunos.map(a => a.id), 0) + 1,
                    nome: nome,
                    matricula: matricula,
                    turma: turma,
                    status: status
                };
                mockAlunos.push(novoAluno);
            }

            updateKPIs();
            renderAlunosTable();
            modalAluno.hide();
        });

        // Novo Turma
        document.getElementById('btnNovaTurma').addEventListener('click', function() {
            turmaAtual = null;
            document.getElementById('modalTurmaTitle').textContent = 'Nova Turma';
            document.getElementById('formTurma').reset();
            modalTurma.show();
        });

        // Salvar Turma
        document.getElementById('btnSalvarTurma').addEventListener('click', function() {
            const codigo = document.getElementById('inputTurmaCodigo').value.trim();
            const nome = document.getElementById('inputTurmaNome').value.trim();
            const professorId = document.getElementById('inputTurmaProfessor').value;
            const vagas = parseInt(document.getElementById('inputTurmaVagas').value);

            if (!codigo || !nome || !professorId || !vagas) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }

            const professor = mockProfessores.find(p => p.id == professorId);

            if (turmaAtual) {
                // Editar
                turmaAtual.codigo = codigo;
                turmaAtual.nome = nome;
                turmaAtual.professor = professor.nome;
                turmaAtual.vagas = vagas;
            } else {
                // Novo
                const novaTurma = {
                    id: Math.max(...mockTurmas.map(t => t.id), 0) + 1,
                    codigo: codigo,
                    nome: nome,
                    professor: professor.nome,
                    vagas: vagas,
                    matriculados: 0
                };
                mockTurmas.push(novaTurma);

                // Atualizar opção no filtro de alunos
                const filterAlunoTurma = document.getElementById('filterAlunoTurma');
                const option = document.createElement('option');
                option.value = novaTurma.codigo;
                option.textContent = novaTurma.codigo;
                filterAlunoTurma.appendChild(option);
            }

            renderTurmas();
            modalTurma.hide();
        });

        // Novo Professor
        document.getElementById('btnNovoProfessor').addEventListener('click', function() {
            professorAtual = null;
            document.getElementById('modalProfessorTitle').textContent = 'Novo Professor';
            document.getElementById('formProfessor').reset();
            modalProfessor.show();
        });

        // Salvar Professor
        document.getElementById('btnSalvarProfessor').addEventListener('click', function() {
            const nome = document.getElementById('inputProfessorNome').value.trim();
            const email = document.getElementById('inputProfessorEmail').value.trim();
            const disciplinas = document.getElementById('inputProfessorDisciplinas').value.trim();

            if (!nome || !email || !disciplinas) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }

            if (professorAtual) {
                // Editar
                professorAtual.nome = nome;
                professorAtual.email = email;
                professorAtual.disciplinas = disciplinas;
            } else {
                // Novo
                const novoProfessor = {
                    id: Math.max(...mockProfessores.map(p => p.id), 0) + 1,
                    nome: nome,
                    email: email,
                    disciplinas: disciplinas,
                    turmas: 0
                };
                mockProfessores.push(novoProfessor);

                // Atualizar dropdown no modal de turma
                const inputTurmaProfessor = document.getElementById('inputTurmaProfessor');
                const option = document.createElement('option');
                option.value = novoProfessor.id;
                option.textContent = novoProfessor.nome;
                inputTurmaProfessor.appendChild(option);
            }

            renderProfessores();
            modalProfessor.hide();
        });

        // Nova Disciplina
        document.getElementById('btnNovaDisciplina').addEventListener('click', function() {
            disciplinaAtual = null;
            document.getElementById('modalDisciplinaTitle').textContent = 'Nova Disciplina';
            document.getElementById('formDisciplina').reset();
            modalDisciplina.show();
        });

        // Salvar Disciplina
        document.getElementById('btnSalvarDisciplina').addEventListener('click', function() {
            const codigo = document.getElementById('inputDisciplinaCodigo').value.trim();
            const nome = document.getElementById('inputDisciplinaNome').value.trim();
            const cargaHoraria = parseInt(document.getElementById('inputDisciplinaCargaHoraria').value);

            if (!codigo || !nome || !cargaHoraria) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }

            if (disciplinaAtual) {
                // Editar
                disciplinaAtual.codigo = codigo;
                disciplinaAtual.nome = nome;
                disciplinaAtual.cargaHoraria = cargaHoraria;
            } else {
                // Novo
                const novaDisciplina = {
                    id: Math.max(...mockDisciplinas.map(d => d.id), 0) + 1,
                    codigo: codigo,
                    nome: nome,
                    cargaHoraria: cargaHoraria,
                    turmas: 0
                };
                mockDisciplinas.push(novaDisciplina);
            }

            renderDisciplinas();
            modalDisciplina.hide();
        });
    }

    // Inicializar
    updateKPIs();
    renderAlunosTable();
    renderTurmas();
    renderProfessores();
    renderDisciplinas();
});
