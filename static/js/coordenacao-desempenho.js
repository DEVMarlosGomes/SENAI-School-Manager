document.addEventListener('DOMContentLoaded', function() {
    
    // Recupera dados REAIS injetados pelo Django
    const dbData = window.DESEMPENHO_DATA || {
        alunos: [],
        turmas: [],
        grafico_notas: {},
        grafico_frequencia: { labels: [], data: [] }
    };

    const realAlunos = dbData.alunos;
    const realTurmas = dbData.turmas;

    // --- 1. PREENCHER FILTRO DE TURMAS ---
    const filterTurma = document.getElementById('filterTurma');
    if (filterTurma) {
        filterTurma.innerHTML = '<option value="">Todas as Turmas</option>';
        realTurmas.forEach(turma => {
            const option = document.createElement('option');
            option.value = turma.codigo;
            option.textContent = turma.codigo;
            filterTurma.appendChild(option);
        });
    }

    // --- 2. RENDERIZAR CARDS DE TURMAS ---
    const containerTurmas = document.getElementById('turmasContainer');
    if (containerTurmas) {
        containerTurmas.innerHTML = '';
        if (realTurmas.length === 0) {
            containerTurmas.innerHTML = '<div class="col-12 p-3 text-center text-muted">Nenhuma turma encontrada.</div>';
        } else {
            realTurmas.forEach(turma => {
                const div = document.createElement('div');
                div.className = 'col-lg-4 col-md-6 mb-3';
                
                let corMedia = 'text-dark';
                if (turma.media_geral >= 7) corMedia = 'text-success';
                else if (turma.media_geral < 5) corMedia = 'text-danger'; // Regra < 5
                else corMedia = 'text-warning';
    
                div.innerHTML = `
                    <div class="card shadow-sm border-0 p-3 h-100 card-hover">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div>
                                <h6 class="fw-bold text-dark mb-0">${turma.codigo}</h6>
                                <small class="text-muted" style="font-size:0.8em">${turma.nome}</small>
                            </div>
                            <i class="fas fa-chalkboard fa-2x text-senai-red opacity-25"></i>
                        </div>
                        <hr class="my-2">
                        <div class="row g-2 text-center">
                            <div class="col-6 border-end">
                                <small class="text-muted d-block">Alunos</small>
                                <span class="fw-bold">${turma.alunos}</span>
                            </div>
                            <div class="col-6">
                                <small class="text-muted d-block">Média Geral</small>
                                <span class="fw-bold ${corMedia}">${turma.media_geral}</span>
                            </div>
                        </div>
                    </div>
                `;
                containerTurmas.appendChild(div);
            });
        }
    }

    // --- 3. RENDERIZAR TABELA DE ALUNOS ---
    function renderAlunosTable(listaAlunos) {
        const tbody = document.getElementById('alunosTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        if (listaAlunos.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center p-3 text-muted">Nenhum aluno encontrado.</td></tr>';
            return;
        }
        
        listaAlunos.forEach(aluno => {
            const tr = document.createElement('tr');
            
            // Badges
            let badgeClass = 'bg-secondary';
            if (aluno.situacao === 'Aprovado') badgeClass = 'bg-success';
            else if (aluno.situacao === 'Recuperação') badgeClass = 'bg-warning text-dark';
            else if (aluno.situacao.includes('Reprovado')) badgeClass = 'bg-danger';

            // Cores Texto Média
            let mediaClass = 'text-dark';
            if (aluno.media >= 7) mediaClass = 'text-success fw-bold';
            else if (aluno.media < 5) mediaClass = 'text-danger fw-bold';

            // Cores Barra Frequência
            let freqColor = 'bg-success';
            if (aluno.frequencia < 75) freqColor = 'bg-danger';
            else if (aluno.frequencia < 85) freqColor = 'bg-warning';

            tr.innerHTML = `
                <td class="ps-3 fw-bold text-dark">${aluno.nome}</td>
                <td><span class="badge bg-light text-dark border">${aluno.matricula}</span></td>
                <td>${aluno.turma}</td>
                <td class="text-center ${mediaClass}">${aluno.media}</td>
                <td class="text-center" style="width: 150px;">
                    <div class="d-flex align-items-center">
                        <div class="progress flex-grow-1" style="height: 10px; background-color: #e9ecef;">
                            <div class="progress-bar ${freqColor}" style="width: ${aluno.frequencia}%"></div>
                        </div>
                        <span class="ms-2 small text-muted">${aluno.frequencia}%</span>
                    </div>
                </td>
                <td class="text-center">
                    <span class="badge ${badgeClass}">${aluno.situacao}</span>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    renderAlunosTable(realAlunos);

    // --- 4. GRÁFICO DE NOTAS (MODIFICADO: 3 BARRAS) ---
    const ctxNotas = document.getElementById('chartNotas');
    if (ctxNotas) {
        const dadosNotas = dbData.grafico_notas || {}; 
        
        new Chart(ctxNotas, {
            type: 'bar',
            data: {
                // Labels fixas para as 3 categorias
                labels: ['Aprovado (≥7)', 'Recuperação (5-6.9)', 'Reprovado (<5)'],
                datasets: [{
                    label: 'Qtd Alunos',
                    data: [
                        dadosNotas['Aprovado'] || 0,
                        dadosNotas['Recuperação'] || 0,
                        dadosNotas['Reprovado'] || 0
                    ],
                    backgroundColor: ['#198754', '#ffc107', '#dc3545'], // Verde, Amarelo, Vermelho
                    borderRadius: 4,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { 
                    y: { 
                        beginAtZero: true, 
                        ticks: { stepSize: 1 } 
                    } 
                }
            }
        });
    }

    // --- 5. GRÁFICO DE FREQUÊNCIA ---
    const ctxFreq = document.getElementById('chartFrequencia');
    if (ctxFreq) {
        const dadosFreq = dbData.grafico_frequencia || { labels: [], data: [] };
        
        new Chart(ctxFreq, {
            type: 'bar',
            data: {
                labels: dadosFreq.labels,
                datasets: [{
                    label: 'Frequência Média (%)',
                    data: dadosFreq.data,
                    backgroundColor: '#E30613',
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', 
                scales: {
                    x: { min: 0, max: 100 },
                    y: { grid: {display: false} }
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    // --- 6. EVENTO DE FILTRAR ---
    const btnFiltrar = document.getElementById('btnFiltrar');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', function() {
            const turmaSelecionada = document.getElementById('filterTurma').value;
            const nomeBusca = document.getElementById('filterAluno').value.toLowerCase();
            const situacaoSelecionada = document.getElementById('filterSituacao').value;

            const filtrados = realAlunos.filter(a => {
                const matchTurma = !turmaSelecionada || a.turma === turmaSelecionada;
                const matchNome = !nomeBusca || a.nome.toLowerCase().includes(nomeBusca) || a.matricula.includes(nomeBusca);
                
                let matchSituacao = true;
                if (situacaoSelecionada) {
                    if (situacaoSelecionada === 'Reprovado') {
                         matchSituacao = a.situacao.includes('Reprovado');
                    } else {
                         matchSituacao = a.situacao === situacaoSelecionada;
                    }
                }

                return matchTurma && matchNome && matchSituacao;
            });

            renderAlunosTable(filtrados);
        });
    }
});