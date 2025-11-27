document.addEventListener('DOMContentLoaded', function() {
    
    // 1. RECUPERAÇÃO SEGURA DOS DADOS
    // Se o Django não enviou nada, usa um objeto vazio para não travar a tela com erro
    const dbData = window.DASHBOARD_DATA || {
        scatter_data: { bom: [], atencao: [], risco: [] },
        grafico_comparativo: { labels: [], aprovados: [], recuperacao: [], reprovados: [] }
    };

    // Configuração padrão de fontes e cores para todos os gráficos
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, sans-serif";
    Chart.defaults.color = '#6c757d';

    // =========================================================
    // 2. GRÁFICO DE DISPERSÃO (SCATTER PLOT)
    // =========================================================
    const ctxDispersao = document.getElementById('chartDispersao');
    
    if (ctxDispersao) {
        // Extrai os arrays de pontos
        const dadosBom = dbData.scatter_data?.bom || [];
        const dadosAtencao = dbData.scatter_data?.atencao || [];
        const dadosRisco = dbData.scatter_data?.risco || [];

        new Chart(ctxDispersao, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: 'Bom Desempenho',
                        data: dadosBom,
                        backgroundColor: '#198754', // Verde Sucesso
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Atenção',
                        data: dadosAtencao,
                        backgroundColor: '#ffc107', // Amarelo Alerta
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Risco (Nota/Freq Baixa)',
                        data: dadosRisco,
                        backgroundColor: '#dc3545', // Vermelho Erro
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    // LINHAS DE REFERÊNCIA (Fake Datasets para desenhar linhas)
                    {
                        type: 'line',
                        label: 'Nota de Corte (6.0)',
                        data: [{x: 0, y: 6}, {x: 100, y: 6}],
                        borderColor: 'rgba(0,0,0,0.2)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false,
                        showLine: true
                    },
                    {
                        type: 'line',
                        label: 'Freq. Mínima (75%)',
                        data: [{x: 75, y: 0}, {x: 75, y: 10}],
                        borderColor: 'rgba(0,0,0,0.2)',
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        fill: false,
                        showLine: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom',
                        title: { display: true, text: 'Frequência (%)' },
                        min: 40, // Foca na área relevante (40% a 100%)
                        max: 100,
                        grid: { color: '#f0f0f0' }
                    },
                    y: {
                        title: { display: true, text: 'Média Geral' },
                        min: 0,
                        max: 10,
                        grid: { color: '#f0f0f0' }
                    }
                },
                plugins: {
                    legend: { display: false }, // Oculta legenda padrão (temos a HTML)
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const p = context.raw;
                                // Se o ponto tiver nome do aluno, mostra no tooltip
                                if(p.aluno) {
                                    return `${p.aluno}: Nota ${p.y} | Freq ${p.x}%`;
                                }
                                return context.dataset.label;
                            }
                        }
                    }
                }
            }
        });
    }

    // =========================================================
    // 3. GRÁFICO DE EFICIÊNCIA POR CURSO (BARRAS EMPILHADAS)
    // =========================================================
    const ctxComparativo = document.getElementById('chartComparativo');
    
    if (ctxComparativo) {
        const compData = dbData.grafico_comparativo || {};
        
        // Verifica se existem dados para plotar
        const hasLabels = compData.labels && compData.labels.length > 0;

        // Dados ou Placeholder se vazio
        const labels = hasLabels ? compData.labels : ['Sem dados'];
        const dadosAprov = hasLabels ? compData.aprovados : [0];
        const dadosRecup = hasLabels ? compData.recuperacao : [0];
        const dadosReprov = hasLabels ? compData.reprovados : [0];

        new Chart(ctxComparativo, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Aprovados',
                        data: dadosAprov,
                        backgroundColor: '#198754',
                        barThickness: 25
                    },
                    {
                        label: 'Recuperação',
                        data: dadosRecup,
                        backgroundColor: '#ffc107',
                        barThickness: 25
                    },
                    {
                        label: 'Reprovados',
                        data: dadosReprov,
                        backgroundColor: '#dc3545',
                        barThickness: 25
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y', // IMPORTANTE: Torna o gráfico horizontal
                scales: {
                    x: {
                        stacked: true, // Empilha as barras no eixo X
                        grid: { display: false }
                    },
                    y: {
                        stacked: true, // Empilha as barras no eixo Y
                        grid: { display: false }
                    }
                },
                plugins: {
                    legend: { display: false }, // Oculta legenda padrão
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                }
            }
        });
    }
});