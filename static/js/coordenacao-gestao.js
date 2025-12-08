document.addEventListener('DOMContentLoaded', function() {
    
    // --- RECUPERAÇÃO DE DADOS ---
    const schoolData = window.SCHOOL_DATA || {};
    let mockAlunos = schoolData.alunos || [];
    let mockTurmas = schoolData.turmas || [];
    let mockProfessores = schoolData.professores || [];
    let mockDisciplinas = schoolData.disciplinas || [];
    let cursosList = schoolData.cursos || [];
    
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    const csrftoken = csrfInput ? csrfInput.value : '';

    // ================= GENERIC CRUD FUNCTIONS =================
    
    async function genericSave(url, data) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                window.location.reload(); 
            } else {
                alert('Erro: ' + result.message);
            }
        } catch (error) { console.error(error); alert('Erro de conexão.'); }
    }

    async function genericDelete(url) {
        if (!confirm('Tem certeza que deseja excluir?')) return;
        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: { 'X-CSRFToken': csrftoken }
            });
            const result = await response.json();
            if (result.success) window.location.reload();
            else alert('Erro ao excluir: ' + result.message);
        } catch (error) { console.error(error); alert('Erro ao tentar excluir.'); }
    }

    // ================= 1. ALUNOS =================
    const modalAluno = new bootstrap.Modal(document.getElementById('modalAluno'));
    let alunoId = null;

    function renderAlunos() {
        const tbody = document.getElementById('alunosTableBody');
        tbody.innerHTML = mockAlunos.map(a => `
            <tr>
                <td>${a.nome}</td>
                <td><span class="badge bg-light text-dark border">${a.matricula}</span></td>
                <td>${a.turma_nome}</td>
                <td>${a.status}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary btn-edit-aluno" data-id="${a.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger btn-del-aluno" data-id="${a.id}"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
        
        document.querySelectorAll('.btn-edit-aluno').forEach(b => b.addEventListener('click', () => openAlunoModal(b.dataset.id)));
        document.querySelectorAll('.btn-del-aluno').forEach(b => b.addEventListener('click', () => genericDelete(`/dashboards/api/gestao/aluno/delete/${b.dataset.id}/`)));
    }

    function openAlunoModal(id = null) {
        alunoId = id;
        document.getElementById('formAluno').reset();
        document.getElementById('modalAlunoTitle').textContent = id ? 'Editar Aluno' : 'Novo Aluno';
        
        // Popula Select Turmas
        const sel = document.getElementById('inputAlunoTurma');
        sel.innerHTML = '<option value="">Selecione...</option>' + 
            mockTurmas.map(t => `<option value="${t.id}">${t.codigo}</option>`).join('');

        if (id) {
            const a = mockAlunos.find(x => x.id == id);
            document.getElementById('inputAlunoNome').value = a.nome;
            document.getElementById('inputAlunoEmail').value = a.email;
            document.getElementById('inputAlunoMatricula').value = a.matricula;
            document.getElementById('inputAlunoStatus').value = a.status;
            sel.value = a.turma_id;
        }
        modalAluno.show();
    }

    document.getElementById('btnNovoAluno').addEventListener('click', () => openAlunoModal());
    document.getElementById('btnSalvarAluno').addEventListener('click', () => {
        genericSave('/dashboards/api/gestao/aluno/save/', {
            id: alunoId,
            nome: document.getElementById('inputAlunoNome').value,
            email: document.getElementById('inputAlunoEmail').value,
            matricula: document.getElementById('inputAlunoMatricula').value,
            turma: document.getElementById('inputAlunoTurma').value,
            status: document.getElementById('inputAlunoStatus').value
        });
    });

    // ================= 2. TURMAS =================
    const modalTurma = new bootstrap.Modal(document.getElementById('modalTurma'));
    let turmaId = null;

    function renderTurmas() {
        const container = document.getElementById('turmasContainer');
        if (mockTurmas.length === 0) {
            container.innerHTML = '<div class="text-muted p-3">Nenhuma turma.</div>';
            return;
        }
        container.innerHTML = mockTurmas.map(t => `
            <div class="col-lg-6">
                <div class="card shadow-sm border-0 h-100 p-3">
                    <div class="d-flex justify-content-between mb-2">
                        <h6 class="fw-bold mb-0">${t.codigo}</h6>
                        <div>
                             <button class="btn btn-sm btn-link p-0 me-2 btn-edit-turma" data-id="${t.id}"><i class="fas fa-edit"></i></button>
                             <button class="btn btn-sm btn-link p-0 text-danger btn-del-turma" data-id="${t.id}"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                    <small class="text-muted d-block">${t.curso_nome}</small>
                    <small class="text-muted">Início: ${t.data_inicio} | Vagas: ${t.vagas}</small>
                </div>
            </div>
        `).join('');

        document.querySelectorAll('.btn-edit-turma').forEach(b => b.addEventListener('click', () => openTurmaModal(b.dataset.id)));
        document.querySelectorAll('.btn-del-turma').forEach(b => b.addEventListener('click', () => genericDelete(`/dashboards/api/gestao/turma/delete/${b.dataset.id}/`)));
    }

    function openTurmaModal(id = null) {
        turmaId = id;
        document.getElementById('formTurma').reset();
        document.getElementById('modalTurmaTitle').textContent = id ? 'Editar Turma' : 'Nova Turma';
        
        const sel = document.getElementById('inputTurmaCurso');
        sel.innerHTML = '<option value="">Selecione...</option>' + 
            cursosList.map(c => `<option value="${c.id}">${c.nome_curso}</option>`).join('');

        if(id) {
            const t = mockTurmas.find(x => x.id == id);
            document.getElementById('inputTurmaCodigo').value = t.codigo;
            sel.value = t.curso_id;
            document.getElementById('inputTurmaInicio').value = t.data_inicio;
            document.getElementById('inputTurmaFim').value = t.data_fim;
            document.getElementById('inputTurmaVagas').value = t.vagas;
        }
        modalTurma.show();
    }

    document.getElementById('btnNovaTurma').addEventListener('click', () => openTurmaModal());
    document.getElementById('btnSalvarTurma').addEventListener('click', () => {
        genericSave('/dashboards/api/gestao/turma/save/', {
            id: turmaId,
            codigo: document.getElementById('inputTurmaCodigo').value,
            curso: document.getElementById('inputTurmaCurso').value,
            data_inicio: document.getElementById('inputTurmaInicio').value,
            data_fim: document.getElementById('inputTurmaFim').value,
            vagas: document.getElementById('inputTurmaVagas').value
        });
    });

    // ================= 3. PROFESSORES =================
    const modalProfessor = new bootstrap.Modal(document.getElementById('modalProfessor'));
    let profId = null;

    function renderProfessores() {
        document.getElementById('professoresTableBody').innerHTML = mockProfessores.map(p => `
            <tr>
                <td>${p.nome}</td>
                <td>${p.email}</td>
                <td>${p.registro}</td>
                <td>${p.turmas}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary btn-edit-prof" data-id="${p.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger btn-del-prof" data-id="${p.id}"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
        document.querySelectorAll('.btn-edit-prof').forEach(b => b.addEventListener('click', () => openProfModal(b.dataset.id)));
        document.querySelectorAll('.btn-del-prof').forEach(b => b.addEventListener('click', () => genericDelete(`/dashboards/api/gestao/professor/delete/${b.dataset.id}/`)));
    }

    function openProfModal(id = null) {
        profId = id;
        document.getElementById('formProfessor').reset();
        document.getElementById('modalProfessorTitle').textContent = id ? 'Editar Professor' : 'Novo Professor';
        if(id) {
            const p = mockProfessores.find(x => x.id == id);
            document.getElementById('inputProfNome').value = p.nome;
            document.getElementById('inputProfEmail').value = p.email;
            document.getElementById('inputProfRegistro').value = p.registro;
        }
        modalProfessor.show();
    }
    
    document.getElementById('btnNovoProfessor').addEventListener('click', () => openProfModal());
    document.getElementById('btnSalvarProfessor').addEventListener('click', () => {
        genericSave('/dashboards/api/gestao/professor/save/', {
            id: profId,
            nome: document.getElementById('inputProfNome').value,
            email: document.getElementById('inputProfEmail').value,
            registro: document.getElementById('inputProfRegistro').value
        });
    });

    // ================= 4. DISCIPLINAS =================
    const modalDisciplina = new bootstrap.Modal(document.getElementById('modalDisciplina'));
    let discId = null;

    function renderDisciplinas() {
        document.getElementById('disciplinasTableBody').innerHTML = mockDisciplinas.map(d => `
            <tr>
                <td>${d.codigo}</td>
                <td>${d.nome}</td>
                <td>${d.carga_horaria}h</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary btn-edit-disc" data-id="${d.id}"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-sm btn-outline-danger btn-del-disc" data-id="${d.id}"><i class="fas fa-trash"></i></button>
                </td>
            </tr>
        `).join('');
        document.querySelectorAll('.btn-edit-disc').forEach(b => b.addEventListener('click', () => openDiscModal(b.dataset.id)));
        document.querySelectorAll('.btn-del-disc').forEach(b => b.addEventListener('click', () => genericDelete(`/dashboards/api/gestao/disciplina/delete/${b.dataset.id}/`)));
    }

    function openDiscModal(id = null) {
        discId = id;
        document.getElementById('formDisciplina').reset();
        document.getElementById('modalDisciplinaTitle').textContent = id ? 'Editar Disciplina' : 'Nova Disciplina';
        if(id) {
            const d = mockDisciplinas.find(x => x.id == id);
            document.getElementById('inputDiscCodigo').value = d.codigo;
            document.getElementById('inputDiscNome').value = d.nome;
            document.getElementById('inputDiscCH').value = d.carga_horaria;
        }
        modalDisciplina.show();
    }

    document.getElementById('btnNovaDisciplina').addEventListener('click', () => openDiscModal());
    document.getElementById('btnSalvarDisciplina').addEventListener('click', () => {
        genericSave('/dashboards/api/gestao/disciplina/save/', {
            id: discId,
            codigo: document.getElementById('inputDiscCodigo').value,
            nome: document.getElementById('inputDiscNome').value,
            carga_horaria: document.getElementById('inputDiscCH').value
        });
    });

    // Inicialização
    renderAlunos();
    renderTurmas();
    renderProfessores();
    renderDisciplinas();
});