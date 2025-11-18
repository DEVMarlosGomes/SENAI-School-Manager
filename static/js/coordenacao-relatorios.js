/**
 * Página de Relatórios - Coordenação
 * Gerencia geração e exportação de relatórios
 */

document.addEventListener('DOMContentLoaded', function() {
    
    const relatorioContainer = document.getElementById('relatorioContainer');
    const relatorioContent = document.getElementById('relatorioContent');

    // Gerar relatório
    function gerarRelatorio() {
        const tipo = document.getElementById('tipoRelatorio').value;
        const periodo = document.getElementById('periodoRelatorio').value;
        const turma = document.getElementById('turmaRelatorio').value;

        if (!periodo) {
            alert('Selecione um período');
            return;
        }

        const relatorios = {
            desempenho: gerarRelatorioDesempenho(),
            frequencia: gerarRelatorioFrequencia(),
            evasao: gerarRelatorioEvasao(),
            turmas: gerarRelatorioPorTurma(),
            disciplinas: gerarRelatorioPorDisciplina(),
            professores: gerarRelatorioAvaliacaoProfessores(),
            geral: gerarRelatorioGeral()
        };

        document.getElementById('relatorioTitle').innerHTML = `
            <i class="fas fa-file-alt text-senai-red me-2"></i>Relatório: ${document.getElementById('tipoRelatorio').options[document.getElementById('tipoRelatorio').selectedIndex].text}
        `;

        relatorioContent.innerHTML = relatorios[tipo] || '<p>Relatório não disponível</p>';
        relatorioContainer.style.display = 'block';
    }

    // Conteúdo dos relatórios
    function gerarRelatorioDesempenho() {
        return `
            <h5 class="mb-3">Desempenho Acadêmico Geral</h5>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Média Geral</p>
                        <h3 class="fw-bold text-senai-red">7.8</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Alunos Aprovados</p>
                        <h3 class="fw-bold text-success">85%</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Em Recuperação</p>
                        <h3 class="fw-bold text-warning">12%</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Reprovados</p>
                        <h3 class="fw-bold text-danger">3%</h3>
                    </div>
                </div>
            </div>
            <table class="table table-sm">
                <thead class="table-light">
                    <tr>
                        <th>Turma</th>
                        <th>Média</th>
                        <th>Aprovados</th>
                        <th>Reprovados</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>TI-2023A</td>
                        <td>8.2</td>
                        <td>88%</td>
                        <td>2%</td>
                    </tr>
                    <tr>
                        <td>MEC-2023B</td>
                        <td>7.5</td>
                        <td>82%</td>
                        <td>4%</td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    function gerarRelatorioFrequencia() {
        return `
            <h5 class="mb-3">Frequência dos Alunos</h5>
            <div class="row mb-3">
                <div class="col-md-4">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Frequência Média</p>
                        <h3 class="fw-bold">92%</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Alunos com >75%</p>
                        <h3 class="fw-bold text-success">89</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Alunos com <75%</p>
                        <h3 class="fw-bold text-danger">11</h3>
                    </div>
                </div>
            </div>
            <div class="alert alert-warning">
                <strong>Atenção:</strong> 11 alunos possuem frequência abaixo de 75% e podem ser evadidos do programa.
            </div>
        `;
    }

    function gerarRelatorioEvasao() {
        return `
            <h5 class="mb-3">Análise de Risco de Evasão</h5>
            <div class="alert alert-danger">
                <strong>Total em Risco:</strong> 15 alunos (12%)
            </div>
            <table class="table table-sm">
                <thead class="table-light">
                    <tr>
                        <th>Aluno</th>
                        <th>Turma</th>
                        <th>Frequência</th>
                        <th>Média</th>
                        <th>Risco</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Pedro Oliveira</td>
                        <td>MEC-2023B</td>
                        <td>60%</td>
                        <td>4.5</td>
                        <td><span class="badge bg-danger">Alto</span></td>
                    </tr>
                    <tr>
                        <td>Ana Costa</td>
                        <td>ELE-2023B</td>
                        <td>65%</td>
                        <td>5.2</td>
                        <td><span class="badge bg-warning">Médio</span></td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    function gerarRelatorioPorTurma() {
        return `
            <h5 class="mb-3">Análise por Turma</h5>
            <table class="table table-sm">
                <thead class="table-light">
                    <tr>
                        <th>Turma</th>
                        <th>Total Alunos</th>
                        <th>Média</th>
                        <th>Frequência</th>
                        <th>Aprovação</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>TI-2023A</td>
                        <td>28</td>
                        <td>8.2</td>
                        <td>94%</td>
                        <td>88%</td>
                    </tr>
                    <tr>
                        <td>MEC-2023B</td>
                        <td>24</td>
                        <td>7.5</td>
                        <td>91%</td>
                        <td>82%</td>
                    </tr>
                    <tr>
                        <td>ELE-2023B</td>
                        <td>22</td>
                        <td>7.9</td>
                        <td>90%</td>
                        <td>85%</td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    function gerarRelatorioPorDisciplina() {
        return `
            <h5 class="mb-3">Análise por Disciplina</h5>
            <table class="table table-sm">
                <thead class="table-light">
                    <tr>
                        <th>Disciplina</th>
                        <th>Turmas</th>
                        <th>Alunos</th>
                        <th>Média</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Programação I</td>
                        <td>2</td>
                        <td>28</td>
                        <td>8.1</td>
                    </tr>
                    <tr>
                        <td>Banco de Dados</td>
                        <td>1</td>
                        <td>14</td>
                        <td>7.8</td>
                    </tr>
                    <tr>
                        <td>Mecânica Técnica</td>
                        <td>1</td>
                        <td>24</td>
                        <td>7.5</td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    function gerarRelatorioAvaliacaoProfessores() {
        return `
            <h5 class="mb-3">Avaliação de Desempenho de Professores</h5>
            <table class="table table-sm">
                <thead class="table-light">
                    <tr>
                        <th>Professor</th>
                        <th>Disciplinas</th>
                        <th>Média Turmas</th>
                        <th>Avaliação</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>João Silva</td>
                        <td>Programação, BD</td>
                        <td>8.0</td>
                        <td><span class="badge bg-success">Excelente</span></td>
                    </tr>
                    <tr>
                        <td>Maria Santos</td>
                        <td>Mecânica, Desenho</td>
                        <td>7.5</td>
                        <td><span class="badge bg-info">Bom</span></td>
                    </tr>
                </tbody>
            </table>
        `;
    }

    function gerarRelatorioGeral() {
        return `
            <h5 class="mb-3">Relatório Geral da Unidade Escolar</h5>
            <div class="row mb-3">
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Total de Alunos</p>
                        <h3 class="fw-bold">125</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Total de Turmas</p>
                        <h3 class="fw-bold">5</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Total de Professores</p>
                        <h3 class="fw-bold">12</h3>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card p-3 text-center">
                        <p class="small text-muted">Taxa de Aprovação</p>
                        <h3 class="fw-bold text-success">85%</h3>
                    </div>
                </div>
            </div>
            <h6 class="fw-bold mt-4 mb-2">Destaques</h6>
            <ul class="list-group list-group-flush">
                <li class="list-group-item"><i class="fas fa-check text-success me-2"></i> Média geral da unidade: 7.8</li>
                <li class="list-group-item"><i class="fas fa-check text-success me-2"></i> Frequência média: 92%</li>
                <li class="list-group-item"><i class="fas fa-exclamation text-warning me-2"></i> 15 alunos em risco de evasão</li>
                <li class="list-group-item"><i class="fas fa-check text-success me-2"></i> Taxa de aprovação acima da meta</li>
            </ul>
        `;
    }

    // Eventos
    document.getElementById('btnGerarRelatorio').addEventListener('click', gerarRelatorio);

    document.getElementById('btnExportarPDF').addEventListener('click', function() {
        const titulo = document.getElementById('relatorioTitle').textContent.trim();
        const elemento = document.getElementById('relatorioContent');
        
        if (elemento.innerHTML.trim() === '') {
            alert('Gere um relatório primeiro');
            return;
        }

        const opt = {
            margin: 10,
            filename: `relatorio_${new Date().getTime()}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
        };

        html2pdf().set(opt).from(elemento).save();
    });

    document.getElementById('btnExportarExcel').addEventListener('click', function() {
        const elemento = document.getElementById('relatorioContent');
        
        if (elemento.innerHTML.trim() === '') {
            alert('Gere um relatório primeiro');
            return;
        }

        // Extrair dados da tabela
        const tabelas = elemento.querySelectorAll('table');
        if (tabelas.length === 0) {
            alert('Este relatório não pode ser exportado para Excel');
            return;
        }

        const wb = XLSX.utils.book_new();
        
        tabelas.forEach((tabela, index) => {
            const dados = XLSX.utils.sheet_from_table(tabela);
            const nomeAba = `Tabela ${index + 1}`;
            XLSX.utils.book_append_sheet(wb, dados, nomeAba);
        });

        XLSX.writeFile(wb, `relatorio_${new Date().getTime()}.xlsx`);
    });

    document.getElementById('btnFecharRelatorio').addEventListener('click', function() {
        relatorioContainer.style.display = 'none';
    });

    // Relatórios rápidos
    document.querySelectorAll('[data-relatorio]').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const tipo = this.getAttribute('data-relatorio');
            document.getElementById('tipoRelatorio').value = tipo;
            document.getElementById('periodoRelatorio').value = 'semestre1';
            gerarRelatorio();
        });
    });
});
