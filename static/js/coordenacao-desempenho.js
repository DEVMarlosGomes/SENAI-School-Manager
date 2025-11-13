/**
 * Página de Desempenho - Coordenação
 * Gerencia filtros, gráficos e tabelas de desempenho acadêmico
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Mock data
    const mockTurmas = [
        { id: 1, codigo: 'TI-2023A', nome: 'Técnico em TI - 2023A' },
        { id: 2, codigo: 'MEC-2023B', nome: 'Técnico em Mecânica - 2023B' },
        { id: 3, codigo: 'ELE-2023B', nome: 'Técnico em Eletrônica - 2023B' },
    ];

    const mockAlunos = [
        { id: 1, nome: 'João Silva', matricula: '2023001', turma: 'TI-2023A', media: 8.5, frequencia: 95, situacao: 'Aprovado' },
        { id: 2, nome: 'Maria Santos', matricula: '2023002', turma: 'TI-2023A', media: 7.2, frequencia: 88, situacao: 'Recuperação' },
        { id: 3, nome: 'Pedro Oliveira', matricula: '2023003', turma: 'MEC-2023B', media: 6.0, frequencia: 70, situacao: 'Recuperação' },
        { id: 4, nome: 'Ana Costa', matricula: '2023004', turma: 'ELE-2023B', media: 9.0, frequencia: 98, situacao: 'Aprovado' },
    ];

    // Preencher filtro de turmas
    const filterTurma = document.getElementById('filterTurma');
    mockTurmas.forEach(turma => {
        const option = document.createElement('option');
        option.value = turma.id;
        option.textContent = turma.nome;
        filterTurma.appendChild(option);
    });

    // Preencher cards de turmas
    function renderTurmas() {
        const container = document.getElementById('turmasContainer');
        container.innerHTML = '';
        mockTurmas.forEach(turma => {
            const alunosTurma = mockAlunos.filter(a => a.turma === turma.codigo).length;
            const div = document.createElement('div');
            div.className = 'col-lg-4 col-md-6 mb-3';
            div.innerHTML = `
                <a href="#" class="card shadow-sm border-0 p-4 text-decoration-none h-100 card-hover" style="cursor: pointer;">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h6 class="fw-bold text-dark">${turma.codigo}</h6>
                            <small class="text-muted">${turma.nome}</small>
                        </div>
                        <i class="fas fa-chalkboard fa-2x text-senai-red opacity-50"></i>
                    </div>
                    <hr>
                    <div class="row g-2">
                        <div class="col-6">
                            <p class="small text-muted mb-1">Alunos</p>
                            <p class="fw-bold">${alunosTurma}</p>
                        </div>
                        <div class="col-6">
                            <p class="small text-muted mb-1">Média Geral</p>
                            <p class="fw-bold text-success">7.9</p>
                        </div>
                    </div>
                </a>
            `;
            container.appendChild(div);
        });
    }

    // Renderizar tabela de alunos
    function renderAlunosTable(alunos = mockAlunos) {
        const tbody = document.getElementById('alunosTableBody');
        tbody.innerHTML = '';
        
        alunos.forEach(aluno => {
            const tr = document.createElement('tr');
            const situacaoClass = aluno.situacao === 'Aprovado' ? 'bg-success' : (aluno.situacao === 'Recuperação' ? 'bg-warning' : 'bg-danger');
            const situacaoBadge = aluno.situacao === 'Aprovado' ? 'success' : (aluno.situacao === 'Recuperação' ? 'warning' : 'danger');
            
            tr.innerHTML = `
                <td>${aluno.nome}</td>
                <td><span class="badge bg-light text-dark">${aluno.matricula}</span></td>
                <td>${aluno.turma}</td>
                <td class="text-center">
                    <span class="fw-bold ${aluno.media >= 7 ? 'text-success' : 'text-danger'}">${aluno.media.toFixed(1)}</span>
                </td>
                <td class="text-center">
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar ${aluno.frequencia >= 75 ? 'bg-success' : 'bg-warning'}" style="width: ${aluno.frequencia}%;">
                            <small>${aluno.frequencia}%</small>
                        </div>
                    </div>
                </td>
                <td class="text-center">
                    <span class="badge bg-${situacaoBadge}">${aluno.situacao}</span>
                </td>
                <td class="text-end">
                    <button class="btn btn-xs btn-outline-primary me-1" onclick="abrirDetalhesAluno(${aluno.id})">
                        <i class="fas fa-eye me-1"></i>Detalhes
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Abrir modal de detalhes
    window.abrirDetalhesAluno = function(id) {
        const aluno = mockAlunos.find(a => a.id === id);
        if (aluno) {
            document.getElementById('detailsNome').textContent = aluno.nome;
            document.getElementById('detailsMatricula').textContent = aluno.matricula;
            document.getElementById('detailsTurma').textContent = aluno.turma;
            document.getElementById('detailsStatus').innerHTML = `<span class="badge bg-success">${aluno.situacao}</span>`;
            document.getElementById('detailsFrequencia').textContent = aluno.frequencia + '%';
            document.getElementById('detailsAulasPresentes').textContent = Math.floor(aluno.frequencia / 5) + ' de 20 aulas';
            
            // Mock de notas por disciplina
            const notasHtml = `
                <div class="row">
                    <div class="col-md-6 mb-2">
                        <p class="small text-muted mb-1">Português</p>
                        <p class="fw-bold">8.5</p>
                    </div>
                    <div class="col-md-6 mb-2">
                        <p class="small text-muted mb-1">Matemática</p>
                        <p class="fw-bold">7.2</p>
                    </div>
                </div>
            `;
            document.getElementById('detailsNotas').innerHTML = notasHtml;
            
            const modal = new bootstrap.Modal(document.getElementById('alunoDetailsModal'));
            modal.show();
        }
    };

    // Gráfico de distribuição de notas
    if (document.getElementById('chartNotas')) {
        const ctx = document.getElementById('chartNotas').getContext('2d');
        const notasDistribuicao = {
            '9-10': 5,
            '8-8.9': 12,
            '7-7.9': 18,
            '6-6.9': 8,
            '<6': 3
        };
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(notasDistribuicao),
                datasets: [{
                    label: 'Quantidade de Alunos',
                    data: Object.values(notasDistribuicao),
                    backgroundColor: ['#198754', '#20c997', '#ffc107', '#ff9800', '#dc3545'],
                    borderRadius: 6,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { stepSize: 5 }
                    }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // Gráfico de frequência
    if (document.getElementById('chartFrequencia')) {
        const ctx = document.getElementById('chartFrequencia').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Semana 1', 'Semana 2', 'Semana 3', 'Semana 4', 'Semana 5', 'Semana 6'],
                datasets: [{
                    label: 'Frequência Média (%)',
                    data: [95, 93, 92, 91, 89, 88],
                    borderColor: '#FF0000',
                    backgroundColor: 'rgba(255, 0, 0, 0.1)',
                    borderWidth: 3,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: '#FF0000',
                    pointRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 10 }
                    }
                }
            }
        });
    }

    // Eventos de filtro
    document.getElementById('btnFiltrar').addEventListener('click', function() {
        const turmaId = document.getElementById('filterTurma').value;
        const alunoNome = document.getElementById('filterAluno').value.toLowerCase();
        
        let alunosFiltrados = mockAlunos;
        
        if (turmaId) {
            const turma = mockTurmas.find(t => t.id == turmaId);
            alunosFiltrados = alunosFiltrados.filter(a => a.turma === turma.codigo);
        }
        
        if (alunoNome) {
            alunosFiltrados = alunosFiltrados.filter(a => 
                a.nome.toLowerCase().includes(alunoNome) ||
                a.matricula.includes(alunoNome)
            );
        }
        
        renderAlunosTable(alunosFiltrados);
    });

    // Inicializar
    renderTurmas();
    renderAlunosTable();
});
