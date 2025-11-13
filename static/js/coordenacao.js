// static/js/coordenacao.js
// Mocks de dados (fallback) - mantidos como fallback se a API não responder
const mock_kpiData = {
    total_turmas: 24,
    turmasTrend: '+3',
    professores_ativos: 42,
    professoresTrend: '+2',
    total_alunos: 1247,
    alunosTrend: '-15',
    alunos_risco_pct: '9%'
};

const mock_desempenhoTurmaData = {
    results: [
        { codigo: 'TI-0023A', valor: 8.8 },
        { codigo: 'MEC-2023B', valor: 7.2 },
        { codigo: 'ELE-2023B', valor: 6.0 },
        { codigo: 'ADM-2023A', valor: 7.8 },
        { codigo: 'LOG-2023B', valor: 7.9 }
    ]
};

const mock_indiceAprovacaoData = {
    total: 1247,
    aprovados_pct: 70,
    recuperacao_pct: 10,
    reprovados_pct: 20
};

const mock_atividadesRecentesData = {
    results: [
        { tipo: 'aprovado', titulo: 'Comunicado aprovado para Turma TI-2023A', detalhe: 'Prof. João Santos • há 2 horas', badge: 'Aprovado' },
        { tipo: 'novo', titulo: 'Nova turma criada: Mecânica Industrial 2024A', detalhe: 'Sistema • há 4 horas', badge: 'Novo' },
        { tipo: 'atencao', titulo: 'Frequência baixa detectada na Turma ELE-2023B', detalhe: 'Sistema • há 6 horas', badge: 'Atenção' }
    ]
};

async function fetchJSON(url) {
    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return await res.json();
    } catch (err) {
        console.warn('fetchJSON failed', url, err);
        return null;
    }
}

function formatNumber(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

function colorForValue(v) {
    // thresholds: >=7.8 green (Excelente); 7.0-7.79 orange (Atenção); <7.0 red (Crítico)
    if (v === null || v === undefined) return '#999999';
    if (v >= 7.8) return '#198754'; // green
    if (v >= 7.0) return '#ffc107'; // orange/yellow
    return '#dc3545'; // red
}

document.addEventListener('DOMContentLoaded', function () {
    // Buscar dados reais da API (com fallback para mocks)
    (async function loadAndRender() {
        // ========== KPIs ==========
        const kpis = await fetchJSON('/dashboards/api/coordenacao/kpis/') || mock_kpiData;
        
        document.getElementById('kpiTurmas').innerText = kpis.total_turmas ?? mock_kpiData.total_turmas;
        document.getElementById('kpiTurmasTrend').innerHTML = `<span class="text-success small">${kpis.turmasTrend ?? mock_kpiData.turmasTrend}</span>`;

        document.getElementById('kpiProfessores').innerText = kpis.professores_ativos ?? mock_kpiData.professores_ativos;
        document.getElementById('kpiProfessoresTrend').innerHTML = `<span class="text-success small">${kpis.professoresTrend ?? mock_kpiData.professoresTrend}</span>`;

        const alunosVal = kpis.total_alunos ?? mock_kpiData.total_alunos;
        document.getElementById('kpiAlunos').innerText = formatNumber(alunosVal);
        const alunosTrendEl = document.getElementById('kpiAlunosTrend');
        alunosTrendEl.innerHTML = `<span class="text-danger small">${kpis.alunosTrend ?? mock_kpiData.alunosTrend}</span>`;

        document.getElementById('kpiRisco').innerText = kpis.alunos_risco_pct ?? mock_kpiData.alunos_risco_pct;
        document.getElementById('kpiRiscoTrend').innerHTML = `<span class="text-warning small">↑1%</span>`;

        // ========== Gráfico de Desempenho por Turma ==========
        const desempenhoResp = await fetchJSON('/dashboards/api/coordenacao/desempenho/');
        const desempenho = desempenhoResp || mock_desempenhoTurmaData;
        
        const ctxBar = document.getElementById('chartDesempenho').getContext('2d');
        const labels = desempenho.results.map(r => r.codigo);
        const values = desempenho.results.map(r => r.valor ?? 0);
        const backgroundColors = values.map(v => colorForValue(v));

        const barChart = new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Desempenho (0-10)',
                    data: values,
                    backgroundColor: backgroundColors,
                    borderRadius: 8,
                    maxBarThickness: 50,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        suggestedMin: 0,
                        suggestedMax: 10,
                        ticks: {
                            stepSize: 1,
                            font: { size: 11 }
                        },
                        grid: { drawBorder: false }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 11 } }
                    }
                },
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return `Média: ${context.parsed.y.toFixed(1)}`;
                            }
                        },
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        padding: 10,
                        borderRadius: 4
                    },
                    legend: { display: false }
                }
            }
        });

        // ========== Gráfico de Aprovação ==========
        const aprovResp = await fetchJSON('/dashboards/api/coordenacao/aprovacao/') || mock_indiceAprovacaoData;
        const donutData = [
            aprovResp.aprovados_pct ?? mock_indiceAprovacaoData.aprovados_pct,
            aprovResp.recuperacao_pct ?? mock_indiceAprovacaoData.recuperacao_pct,
            aprovResp.reprovados_pct ?? mock_indiceAprovacaoData.reprovados_pct
        ];
        const donutColors = ['#198754', '#ffc107', '#dc3545'];
        
        const ctxDonut = document.getElementById('chartAprovacao').getContext('2d');
        const donutChart = new Chart(ctxDonut, {
            type: 'doughnut',
            data: {
                labels: ['Aprovados', 'Em Recuperação', 'Reprovados'],
                datasets: [{
                    data: donutData,
                    backgroundColor: donutColors,
                    hoverOffset: 10,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        padding: 10,
                        borderRadius: 4,
                        callbacks: {
                            label: function(context) {
                                return `${context.label}: ${context.parsed}%`;
                            }
                        }
                    }
                }
            }
        });

        // ========== Legenda de Aprovação ==========
        const legendEl = document.getElementById('legendAprovacao');
        legendEl.innerHTML = `
            <li class="mb-2 d-flex align-items-center">
                <i class="fas fa-circle text-success me-2 small"></i>
                <span class="flex-grow-1">Aprovados</span>
                <span class="badge bg-success ms-2">${aprovResp.aprovados_pct ?? mock_indiceAprovacaoData.aprovados_pct}%</span>
            </li>
            <li class="mb-2 d-flex align-items-center">
                <i class="fas fa-circle text-warning me-2 small"></i>
                <span class="flex-grow-1">Em Recuperação</span>
                <span class="badge bg-warning text-dark ms-2">${aprovResp.recuperacao_pct ?? mock_indiceAprovacaoData.recuperacao_pct}%</span>
            </li>
            <li class="d-flex align-items-center">
                <i class="fas fa-circle text-danger me-2 small"></i>
                <span class="flex-grow-1">Reprovados</span>
                <span class="badge bg-danger ms-2">${aprovResp.reprovados_pct ?? mock_indiceAprovacaoData.reprovados_pct}%</span>
            </li>
        `;
        document.getElementById('totalAlunosDonut').innerText = formatNumber(aprovResp.total ?? mock_indiceAprovacaoData.total);

        // ========== Atividades Recentes ==========
        const ativsResp = await fetchJSON('/dashboards/api/coordenacao/atividades/') || mock_atividadesRecentesData;
        const atividadesEl = document.getElementById('atividadesRecentes');
        
        if (!ativsResp.results || ativsResp.results.length === 0) {
            atividadesEl.innerHTML = '<div class="list-group-item text-center text-muted py-4"><i class="fas fa-inbox fa-2x mb-2 d-block opacity-50"></i>Nenhuma atividade recente</div>';
        } else {
            ativsResp.results.forEach(item => {
                const div = document.createElement('div');
                div.className = 'list-group-item d-flex align-items-start gap-3 px-4 py-3';
                
                let iconHtml = '';
                let iconClass = '';
                let badgeClass = 'bg-secondary';
                
                if (item.tipo === 'aprovado') {
                    iconHtml = '<i class="fas fa-check-circle fa-xl text-success"></i>';
                    badgeClass = 'bg-success';
                } else if (item.tipo === 'novo') {
                    iconHtml = '<i class="fas fa-plus-circle fa-xl text-danger"></i>';
                    badgeClass = 'bg-danger';
                } else if (item.tipo === 'atencao') {
                    iconHtml = '<i class="fas fa-exclamation-triangle fa-xl text-warning"></i>';
                    badgeClass = 'bg-warning text-dark';
                } else {
                    iconHtml = '<i class="fas fa-circle fa-xl text-muted opacity-50"></i>';
                }
                
                div.innerHTML = `
                    <div class="mt-1">${iconHtml}</div>
                    <div class="flex-grow-1 min-w-0">
                        <h6 class="mb-1 fw-bold small">${item.titulo}</h6>
                        <small class="text-muted d-block">${item.detalhe}</small>
                    </div>
                    <span class="badge ${badgeClass} ms-2 text-nowrap">${item.badge}</span>
                `;
                atividadesEl.appendChild(div);
            });
        }
    })();
});
