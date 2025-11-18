// Arquivo: static/js/secretaria.js
document.addEventListener('DOMContentLoaded', function () {
    // Modal bootstrap helpers
    const modalAlunoEl = document.getElementById('modalAluno');
    const modalAluno = modalAlunoEl ? new bootstrap.Modal(modalAlunoEl) : null;

    // Novo Aluno
    const btnNovo = document.getElementById('btnNovoAluno');
    if (btnNovo) {
        btnNovo.addEventListener('click', () => {
            document.getElementById('modalAlunoTitle').innerText = 'Novo Aluno';
            document.getElementById('formAluno').reset();
            modalAluno.show();
        });
    }

    // helper: obter csrftoken do cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Salvar aluno -> envia para API e insere linha com retorno
    const btnSalvar = document.getElementById('salvarAluno');
    if (btnSalvar) {
        btnSalvar.addEventListener('click', async () => {
            const nome = document.getElementById('alunoNome').value.trim();
            const matricula = document.getElementById('alunoMatricula').value.trim();
            const turma = document.getElementById('alunoTurma').value.trim();
            const status = document.getElementById('alunoStatus').value;
            if (!nome) {
                alert('Preencha o nome.');
                return;
            }
            // Se modal tem editId, fazemos PUT
            const editId = modalAlunoEl ? modalAlunoEl.dataset.editId : '';
            if (editId) {
                const payload = {
                    first_name: nome.split(' ')[0] || nome,
                    last_name: nome.split(' ').slice(1).join(' ') || '',
                    email: '',
                    status: status,
                    turma: turma
                };
                try {
                    const res = await fetch(`/academico/api/alunos/${editId}/`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCookie('csrftoken')
                        },
                        body: JSON.stringify(payload)
                    });
                    if (!res.ok) {
                        alert('Erro ao atualizar aluno.');
                        return;
                    }
                    // Atualizar linha na tabela
                    const tr = document.querySelector(`#tableAlunos tbody tr[data-id="${editId}"]`);
                    if (tr) {
                        tr.dataset.nome = nome;
                        tr.dataset.matricula = matricula;
                        tr.dataset.turma = turma;
                        tr.dataset.status = status;
                        tr.querySelector('td:nth-child(1)').innerText = nome;
                        tr.querySelector('td:nth-child(2)').innerText = matricula;
                        tr.querySelector('td:nth-child(3)').innerText = turma;
                        const badge = status === 'ativa' ? '<span class="badge bg-success">Ativa</span>' : (status === 'pendente' ? '<span class="badge bg-warning text-dark">Pendente</span>' : '<span class="badge bg-secondary">Inativa</span>');
                        tr.querySelector('td:nth-child(4)').innerHTML = badge;
                    }
                    // limpar estado de edição
                    delete modalAlunoEl.dataset.editId;
                    modalAluno.hide();
                    updateTotals();
                } catch (err) {
                    console.error(err);
                    alert('Erro ao conectar com o servidor.');
                }
                return;
            }

            // Caso criação (POST)
            const payload = {
                username: matricula || nome.replace(/\s+/g, '').toLowerCase(),
                first_name: nome.split(' ')[0] || nome,
                last_name: nome.split(' ').slice(1).join(' ') || '',
                email: '',
                password: 'ChangeMe123!',
                cpf: '',
                telefone: '',
                data_nascimento: '',
                endereco: ''
            };

            try {
                const res = await fetch('/academico/api/alunos/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(payload)
                });
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}));
                    alert('Erro ao criar aluno: ' + (err && err.errors ? JSON.stringify(err.errors) : res.statusText));
                    return;
                }
                const data = await res.json();
                // inserir linha usando dados retornados
                const tbody = document.querySelector('#tableAlunos tbody');
                const tr = document.createElement('tr');
                tr.setAttribute('data-id', data.id || '');
                tr.setAttribute('data-nome', nome);
                tr.setAttribute('data-matricula', data.matricula || matricula);
                tr.setAttribute('data-turma', turma);
                tr.setAttribute('data-status', status);
                const badge = status === 'ativa' ? '<span class="badge bg-success">Ativa</span>' : (status === 'pendente' ? '<span class="badge bg-warning text-dark">Pendente</span>' : '<span class="badge bg-secondary">Inativa</span>');
                tr.innerHTML = `
                    <td>${nome}</td>
                    <td>${data.matricula || matricula}</td>
                    <td>${turma}</td>
                    <td>${badge}</td>
                    <td>—</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-primary btn-editar me-1">Editar</button>
                        <button class="btn btn-sm btn-outline-primary btn-detalhe me-1">Detalhar</button>
                        <button class="btn btn-sm btn-danger btn-excluir">Excluir</button>
                    </td>
                `;
                tbody.prepend(tr);
                modalAluno.hide();
                updateTotals();
            } catch (err) {
                alert('Erro ao conectar com o servidor.');
                console.error(err);
            }
        });
    }

    // Delegação de eventos na tabela (editar/excluir/detalhar)
    document.addEventListener('click', async function (e) {
        // Excluir
        if (e.target.matches('.btn-excluir')) {
            const tr = e.target.closest('tr');
            const alunoId = tr ? tr.dataset.id : null;
            if (!confirm('Remover este aluno?')) return;
            if (alunoId) {
                try {
                    const res = await fetch(`/academico/api/alunos/${alunoId}/`, {
                        method: 'DELETE',
                        headers: { 'X-CSRFToken': getCookie('csrftoken') }
                    });
                    if (res.ok) {
                        tr.remove();
                        updateTotals();
                    } else {
                        alert('Erro ao remover aluno.');
                    }
                } catch (err) {
                    console.error(err);
                    alert('Erro de conexão ao remover aluno.');
                }
            } else if (tr) {
                tr.remove();
                updateTotals();
            }
            return;
        }

        // Detalhar
        if (e.target.matches('.btn-detalhe')) {
            const tr = e.target.closest('tr');
            const nome = tr ? tr.dataset.nome : '';
            const matricula = tr ? tr.dataset.matricula : '';
            alert(`Detalhes de ${nome} (Matrícula: ${matricula})`);
            return;
        }

        // Editar -> abrir modal preenchido e marcar edição
        if (e.target.matches('.btn-editar')) {
            const tr = e.target.closest('tr');
            const alunoId = tr ? tr.dataset.id : '';
            document.getElementById('modalAlunoTitle').innerText = 'Editar Aluno';
            document.getElementById('alunoNome').value = tr ? (tr.dataset.nome || '') : '';
            document.getElementById('alunoMatricula').value = tr ? (tr.dataset.matricula || '') : '';
            document.getElementById('alunoTurma').value = tr ? (tr.dataset.turma || '') : '';
            document.getElementById('alunoStatus').value = tr ? (tr.dataset.status || 'ativa') : 'ativa';
            if (modalAlunoEl) modalAlunoEl.dataset.editId = alunoId || '';
            modalAluno.show();
            return;
        }
    });

    // Atualiza totais simples
    function updateTotals() {
        const total = document.querySelectorAll('#tableAlunos tbody tr').length;
        const ativos = document.querySelectorAll('#tableAlunos tbody tr[data-status="ativa"]').length;
        const elTotal = document.getElementById('totalAlunos');
        const elAtivos = document.getElementById('alunosAtivos');
        if (elTotal) elTotal.innerText = total;
        if (elAtivos) elAtivos.innerText = ativos;
    }

    // Filtro simples cliente
    const btnFiltrar = document.getElementById('btnFiltrar');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', () => {
            const nome = document.getElementById('f_nome').value.toLowerCase();
            const matricula = document.getElementById('f_matricula').value.toLowerCase();
            const turma = document.getElementById('f_turma').value.toLowerCase();
            const status = document.getElementById('f_status').value.toLowerCase();
            document.querySelectorAll('#tableAlunos tbody tr').forEach(tr => {
                const matchesNome = !nome || (tr.dataset.nome && tr.dataset.nome.toLowerCase().includes(nome));
                const matchesMat = !matricula || (tr.dataset.matricula && tr.dataset.matricula.toLowerCase().includes(matricula));
                const matchesTurma = !turma || (tr.dataset.turma && tr.dataset.turma.toLowerCase().includes(turma));
                const matchesStatus = !status || (tr.dataset.status && tr.dataset.status.toLowerCase() === status);
                tr.style.display = (matchesNome && matchesMat && matchesTurma && matchesStatus) ? '' : 'none';
            });
        });
    }

    // Financeiro: ações básicas
    document.addEventListener('click', function (e) {
        if (e.target.matches('.btn-registrar')) {
            alert('Registrar pagamento (simulado).');
        }
        if (e.target.id === 'btnExportarRelatorio' || e.target.matches('.btn-export')) {
            alert('Exportar relatório (simulado).');
        }
        if (e.target.id === 'btnRegistrarPagamento') {
            alert('Abrir formulário de registro de pagamento (simulado).');
        }
    });

    // Documentos: emitir/baixar (simulado)
    const btnEmitir = document.getElementById('btnEmitirDoc');
    if (btnEmitir) btnEmitir.addEventListener('click', () => alert('Emitir novo documento (simulado).'));

    // Mural de mensagens: nova mensagem
    const btnNovaMsg = document.getElementById('btnNovaMensagem');
    const modalMsgEl = document.getElementById('modalMensagem');
    const modalMsg = modalMsgEl ? new bootstrap.Modal(modalMsgEl) : null;
    if (btnNovaMsg) btnNovaMsg.addEventListener('click', () => modalMsg.show());
    const btnEnviarMsg = document.getElementById('enviarMensagem');
    if (btnEnviarMsg) btnEnviarMsg.addEventListener('click', () => {
        const assunto = document.getElementById('mensagemAssunto').value || '(Sem assunto)';
        const conteudo = document.getElementById('mensagemConteudo').value || '';
        // Adiciona à lista localmente
        const lista = document.getElementById('listaMensagens');
        const item = document.createElement('a');
        item.href = '#';
        item.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-start';
        item.innerHTML = `<div><div class="fw-bold">${assunto}</div><small class="text-muted">Enviado agora</small><div class="small">${conteudo}</div></div><div class="text-end"><span class="badge bg-danger">Não lida</span><div class="mt-2"><button class="btn btn-sm btn-outline-primary btn-responder">Responder</button> <button class="btn btn-sm btn-outline-secondary btn-arquivar">Arquivar</button></div></div>`;
        lista.prepend(item);
        modalMsg.hide();
        document.getElementById('formMensagem').reset();
    });

    // Marca mensagens como lidas/arquiva/responde (simulado)
    document.addEventListener('click', function (e) {
        if (e.target.matches('.btn-arquivar')) {
            const item = e.target.closest('.list-group-item');
            item.remove();
        }
        if (e.target.matches('.btn-responder')) {
            alert('Responder (simulado)');
        }
    });

    // Carregar lista inicial de alunos via API e inicializa totais
    (async function loadAlunos() {
        try {
            const res = await fetch('/academico/api/alunos/');
            if (!res.ok) return updateTotals();
            const data = await res.json();
            const tbody = document.querySelector('#tableAlunos tbody');
            if (!tbody) return;
            // Limpar linhas de exemplo (preservar se desejar)
            tbody.innerHTML = '';
            data.results.forEach(a => {
                const tr = document.createElement('tr');
                tr.setAttribute('data-nome', a.nome || '');
                tr.setAttribute('data-matricula', a.matricula || '');
                tr.setAttribute('data-turma', a.curso || '');
                tr.setAttribute('data-status', a.status || '');
                const badgeClass = a.status === 'ativa' ? '<span class="badge bg-success">Ativa</span>' : (a.status === 'pendente' ? '<span class="badge bg-warning text-dark">Pendente</span>' : '<span class="badge bg-secondary">'+(a.status||'')+'</span>');
                tr.innerHTML = `
                    <td>${a.nome}</td>
                    <td>${a.matricula}</td>
                    <td>${a.curso}</td>
                    <td>${badgeClass}</td>
                    <td>—</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-primary btn-editar me-1">Editar</button>
                        <button class="btn btn-sm btn-outline-primary btn-detalhe me-1">Detalhar</button>
                        <button class="btn btn-sm btn-danger btn-excluir">Excluir</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
            updateTotals();
        } catch (err) {
            console.warn('Não foi possível carregar alunos via API', err);
            updateTotals();
        }
    })();
});
