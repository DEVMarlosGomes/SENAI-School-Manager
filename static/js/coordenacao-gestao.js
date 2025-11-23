document.addEventListener('DOMContentLoaded', function() {
    
    // --- RECUPERAÇÃO DE DADOS DO DJANGO ---
    const schoolData = window.SCHOOL_DATA || {};
    let mockAlunos = schoolData.alunos || [];
    let mockTurmas = schoolData.turmas || [];
    let mockProfessores = schoolData.professores || [];
    let mockDisciplinas = schoolData.disciplinas || [];
    
    // --- CONFIGURAÇÃO TOKEN SEGURANÇA (CSRF) ---
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrftoken = csrfInput ? csrfInput.value : '';

    // =================================================================
    // 1. ABA ALUNOS (COM EDIÇÃO, EXCLUSÃO E FILTROS)
    // =================================================================

    function renderAlunosTable(alunos = mockAlunos) {
        const tbody = document.getElementById('alunosTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (alunos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted p-3">Nenhum aluno encontrado.</td></tr>';
            return;
        }

        alunos.forEach(aluno => {
            let badgeClass = 'bg-secondary';
            // Normaliza status para evitar erros de caixa (maiúscula/minúscula)
            const statusRaw = (aluno.status || '').toLowerCase(); 

            if (statusRaw === 'ativo') badgeClass = 'bg-success';
            else if (statusRaw === 'trancado') badgeClass = 'bg-secondary'; 
            else if (statusRaw === 'pendente') badgeClass = 'bg-warning text-dark';
            else if (statusRaw === 'inativo') badgeClass = 'bg-danger';

            // Formata texto para exibição (Primeira letra maiúscula)
            const statusDisplay = aluno.status ? aluno.status.charAt(0).toUpperCase() + aluno.status.slice(1) : 'Indefinido';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${aluno.nome}</td>
                <td><span class="badge bg-light text-dark border">${aluno.matricula}</span></td>
                <td>${aluno.turma}</td>
                <td><span class="badge ${badgeClass}">${statusDisplay}</span></td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary me-1 btn-editar" data-id="${aluno.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger btn-excluir" data-id="${aluno.id}"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        // Reconecta os eventos aos botões recém-criados
        attachActionListeners();
    }

    function attachActionListeners() {
        // Botões de Editar
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                const aluno = mockAlunos.find(a => a.id == id);
                if (aluno) {
                    abrirModalEditar(aluno);
                }
            });
        });

        // Botões de Excluir
        document.querySelectorAll('.btn-excluir').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.getAttribute('data-id');
                if (confirm('Tem certeza que deseja excluir este aluno? Essa ação apagará também o login do usuário.')) {
                    deletarAluno(id);
                }
            });
        });
    }

    // --- FILTROS DE ALUNOS ---
    const btnFiltrar = document.getElementById('btnFiltrarAlunos');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', () => {
            const nome = document.getElementById('filterAlunoNome').value.toLowerCase();
            const status = document.getElementById('filterAlunoStatus').value.toLowerCase();
            const turma = document.getElementById('filterAlunoTurma').value;

            const filtrados = mockAlunos.filter(a => {
                const aStatus = (a.status || '').toLowerCase();
                const matchNome = !nome || a.nome.toLowerCase().includes(nome) || a.matricula.includes(nome);
                // Compara status em minúsculo (ex: "trancado" == "trancado")
                const matchStatus = !status || aStatus === status;
                const matchTurma = !turma || a.turma === turma;
                return matchNome && matchStatus && matchTurma;
            });
            renderAlunosTable(filtrados);
        });
    }

    // =================================================================
    // 2. ABA TURMAS (Visualização Completa)
    // =================================================================

    function renderTurmas() {
        const container = document.getElementById('turmasContainer');
        if (!container) return;
        container.innerHTML = '';
        
        if (mockTurmas.length === 0) {
            container.innerHTML = '<div class="col-12 text-center text-muted p-3">Nenhuma turma cadastrada.</div>';
            return;
        }

        mockTurmas.forEach(turma => {
            const ocupacao = turma.vagas > 0 ? Math.round((turma.matriculados / turma.vagas) * 100) : 0;
            let barColor = 'bg-primary';
            if (ocupacao >= 100) barColor = 'bg-danger';
            else if (ocupacao >= 80) barColor = 'bg-warning';

            const div = document.createElement('div');
            div.className = 'col-lg-6 col-md-12 mb-3';
            div.innerHTML = `
                <div class="card shadow-sm border-0 h-100 p-3">
                    <div class="d-flex justify-content-between mb-2">
                        <h6 class="fw-bold mb-0">${turma.codigo}</h6>
                        <span class="badge bg-light text-dark border">${turma.matriculados}/${turma.vagas}</span>
                    </div>
                    <small class="text-muted d-block mb-2">${turma.nome}</small>
                    <small class="text-muted d-block mb-2"><i class="fas fa-chalkboard-user me-1"></i> ${turma.professor}</small>
                    <div class="progress" style="height: 6px;">
                        <div class="progress-bar ${barColor}" style="width: ${ocupacao}%"></div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
        
        // Atualiza também os filtros de turma (na aba Alunos e no Modal)
        updateTurmaSelects();
    }

    function updateTurmaSelects() {
        const selectFiltro = document.getElementById('filterAlunoTurma');
        const selectModal = document.getElementById('inputAlunoTurma');
        
        if (selectFiltro) selectFiltro.innerHTML = '<option value="">Todas as Turmas</option>';
        if (selectModal) selectModal.innerHTML = '<option value="">Selecione uma turma</option>';

        mockTurmas.forEach(t => {
            if (selectFiltro) {
                const opt = document.createElement('option');
                opt.value = t.codigo; 
                opt.textContent = t.codigo;
                selectFiltro.appendChild(opt);
            }
            if (selectModal) {
                const opt = document.createElement('option');
                opt.value = t.codigo; // Backend espera o código/nome para buscar
                opt.textContent = t.codigo + ' - ' + t.nome;
                selectModal.appendChild(opt);
            }
        });
    }

    // =================================================================
    // 3. ABA PROFESSORES
    // =================================================================

    function renderProfessores() {
        const tbody = document.getElementById('professoresTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (mockProfessores.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhum professor encontrado.</td></tr>';
            return;
        }

        mockProfessores.forEach(prof => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${prof.nome}</td>
                <td>${prof.email}</td>
                <td><small class="d-inline-block text-truncate" style="max-width: 250px;" title="${prof.disciplinas}">${prof.disciplinas}</small></td>
                <td><span class="badge bg-senai-dark">${prof.turmas}</span></td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // =================================================================
    // 4. ABA DISCIPLINAS
    // =================================================================

    function renderDisciplinas() {
        const tbody = document.getElementById('disciplinasTableBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        
        if (mockDisciplinas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Nenhuma disciplina encontrada.</td></tr>';
            return;
        }

        mockDisciplinas.forEach(disc => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="badge bg-light text-dark border">${disc.codigo}</span></td>
                <td>${disc.nome}</td>
                <td>${disc.cargaHoraria}h</td>
                <td><span class="badge bg-info text-dark">${disc.turmas}</span></td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary"><i class="fas fa-edit"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // =================================================================
    // 5. INTEGRAÇÃO API (SALVAR/DELETAR)
    // =================================================================

    async function salvarAlunoBackend(dados) {
        try {
            const response = await fetch('/dashboards/api/gestao/aluno/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(dados)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert(result.message);
                window.location.reload(); // Recarrega para atualizar dados reais
            } else {
                alert('Erro: ' + result.message);
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            alert('Erro ao conectar com o servidor.');
        }
    }

    async function deletarAluno(id) {
        try {
            const response = await fetch(`/dashboards/api/gestao/aluno/delete/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Aluno excluído.');
                window.location.reload();
            } else {
                alert('Erro ao excluir: ' + result.message);
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao tentar excluir.');
        }
    }

    // =================================================================
    // 6. CONTROLE DE MODALS
    // =================================================================

    const modalAlunoEl = document.getElementById('modalAluno');
    let modalAluno = null;
    if (modalAlunoEl) modalAluno = new bootstrap.Modal(modalAlunoEl);

    let alunoIdEmEdicao = null;

    // Botão Novo Aluno
    const btnNovo = document.getElementById('btnNovoAluno');
    if (btnNovo) {
        btnNovo.addEventListener('click', () => {
            alunoIdEmEdicao = null;
            const title = document.getElementById('modalAlunoTitle');
            if(title) title.textContent = 'Novo Aluno';
            
            const form = document.getElementById('formAluno');
            if(form) form.reset();
            
            if(modalAluno) modalAluno.show();
        });
    }

    // Abrir Edição
    function abrirModalEditar(aluno) {
        alunoIdEmEdicao = aluno.id;
        const title = document.getElementById('modalAlunoTitle');
        if(title) title.textContent = 'Editar Aluno';
        
        // Preenche formulário
        document.getElementById('inputAlunoNome').value = aluno.nome;
        document.getElementById('inputAlunoMatricula').value = aluno.matricula;
        document.getElementById('inputAlunoTurma').value = aluno.turma;
        
        // Normaliza status para o select (Primeira letra maiúscula)
        let st = aluno.status ? aluno.status.toLowerCase() : 'ativo';
        st = st.charAt(0).toUpperCase() + st.slice(1);
        // Tenta setar valor, se não existir no select, padrão é Ativo
        const statusSelect = document.getElementById('inputAlunoStatus');
        statusSelect.value = st; 
        if (!statusSelect.value) statusSelect.value = 'Ativo';

        if(modalAluno) modalAluno.show();
    }

    // Salvar Aluno (Click do botão no modal)
    const btnSalvar = document.getElementById('btnSalvarAluno');
    if (btnSalvar) {
        btnSalvar.addEventListener('click', () => {
            const dados = {
                id: alunoIdEmEdicao,
                nome: document.getElementById('inputAlunoNome').value,
                matricula: document.getElementById('inputAlunoMatricula').value,
                turma: document.getElementById('inputAlunoTurma').value,
                status: document.getElementById('inputAlunoStatus').value
            };
            salvarAlunoBackend(dados);
        });
    }

    // Outros Modals (Turma, Professor, Disciplina) - Placeholders para não quebrar UI
    const modalTurmaEl = document.getElementById('modalTurma');
    let modalTurma = modalTurmaEl ? new bootstrap.Modal(modalTurmaEl) : null;
    const btnNovoTurma = document.getElementById('btnNovaTurma');
    if(btnNovoTurma && modalTurma) {
        btnNovoTurma.addEventListener('click', () => {
             document.getElementById('formTurma').reset();
             modalTurma.show(); 
        });
    }

    const modalProfEl = document.getElementById('modalProfessor');
    let modalProfessor = modalProfEl ? new bootstrap.Modal(modalProfEl) : null;
    const btnNovoProf = document.getElementById('btnNovoProfessor');
    if(btnNovoProf && modalProfessor) {
        btnNovoProf.addEventListener('click', () => {
            document.getElementById('formProfessor').reset();
            modalProfessor.show();
        });
    }

    const modalDiscEl = document.getElementById('modalDisciplina');
    let modalDisciplina = modalDiscEl ? new bootstrap.Modal(modalDiscEl) : null;
    const btnNovoDisc = document.getElementById('btnNovaDisciplina');
    if(btnNovoDisc && modalDisciplina) {
        btnNovoDisc.addEventListener('click', () => {
            document.getElementById('formDisciplina').reset();
            modalDisciplina.show();
        });
    }

    // =================================================================
    // 7. INICIALIZAÇÃO DE KPIS
    // =================================================================
    
    function updateKPIs() {
        const totalAlunos = mockAlunos.length;
        const ativos = mockAlunos.filter(a => (a.status||'').toLowerCase() === 'ativo').length;
        const pendentes = mockAlunos.filter(a => (a.status||'').toLowerCase() === 'pendente').length;
        const inativos = totalAlunos - ativos - pendentes;

        const setTxt = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        };

        setTxt('kpiTotalAlunos', totalAlunos);
        setTxt('kpiAtivos', ativos);
        setTxt('kpiPendentes', pendentes);
        setTxt('kpiInativos', inativos);
    }

    updateKPIs();
    renderAlunosTable();
    renderTurmas();     
    renderProfessores();
    renderDisciplinas();
});