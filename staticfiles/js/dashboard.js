document.addEventListener('DOMContentLoaded', function() {
    // Inicialização de componentes
    initializeCharts();
    initializeTooltips();
});

function initializeCharts() {
    // Aqui você pode adicionar a lógica para inicializar gráficos
    // usando bibliotecas como Chart.js se necessário
}

function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
}