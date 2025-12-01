/**
 * Página de Comunicação - Coordenação
 * Integra com as APIs: /dashboards/api/avisos-eventos/, /dashboards/api/avisos/criar/, /dashboards/api/eventos/criar/
 */

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

document.addEventListener('DOMContentLoaded', function() {
    const modalAvisoEl = document.getElementById('modalAviso');
    const modalEventoEl = document.getElementById('modalEvento');
    let modalAviso = modalAvisoEl ? new bootstrap.Modal(modalAvisoEl) : null;
    let modalEvento = modalEventoEl ? new bootstrap.Modal(modalEventoEl) : null;

    const csrftoken = getCookie('csrftoken');

    async function fetchAvisosEventos() {
        try {
            const res = await fetch('/dashboards/api/avisos-eventos/');
            if (!res.ok) throw new Error('Falha ao buscar avisos/eventos');
            const data = await res.json();
            renderAvisos(data.avisos || []);
            renderEventos(data.eventos || []);
        } catch (err) {
            console.error(err);
        }
    }

    function renderAvisos(avisos) {
        const container = document.getElementById('avisosContainer');
        if (!container) return;
        container.innerHTML = '';
        avisos.forEach(a => {
            const tipo = a.tipo || 'Geral';
            const tipoClass = tipo === 'Urgente' ? 'border-danger' : (tipo === 'Importante' ? 'border-warning' : 'border-success');
            const badgeClass = tipo === 'Urgente' ? 'bg-danger' : (tipo === 'Importante' ? 'bg-warning text-dark' : 'bg-success');

            const div = document.createElement('div');
            div.className = 'col-lg-4';
            div.innerHTML = `
                <div class="card shadow-sm border-0 border-top border-4 ${tipoClass}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="fw-bold mb-0">${a.titulo}</h6>
                            <span class="badge ${badgeClass}">${tipo}</span>
                        </div>
                        <p class="small text-muted mb-2">${a.conteudo}</p>
                        <small class="text-muted">${a.data} • ${a.criador}</small>
                        <div class="mt-3 text-end">
                            <button class="btn btn-xs btn-outline-primary me-1" onclick="window.editarAvisoClient(${a.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn btn-xs btn-outline-danger" onclick="window.deletarAvisoClient(${a.id})"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    function renderEventos(eventos) {
        const tbody = document.getElementById('eventosTBody');
        if (!tbody) return;
        tbody.innerHTML = '';
        eventos.forEach(e => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${e.titulo}</td>
                <td>${e.data}</td>
                <td>${e.descricao || ''}</td>
                <td>${e.local || ''}</td>
                <td class="text-end">
                    <button class="btn btn-xs btn-outline-primary me-1" onclick="window.editarEventoClient(${e.id})"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-xs btn-outline-danger" onclick="window.deletarEventoClient(${e.id})"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // abrir modais
    const btnNovoAviso = document.getElementById('btnNovoAviso');
    if (btnNovoAviso && modalAviso) btnNovoAviso.addEventListener('click', () => { document.getElementById('formAviso').reset(); modalAviso.show(); });
    const btnNovoEvento = document.getElementById('btnNovoEvento');
    if (btnNovoEvento && modalEvento) btnNovoEvento.addEventListener('click', () => { document.getElementById('formEvento').reset(); modalEvento.show(); });

    // salvar aviso
    window.salvarAviso = async function() {
        const titulo = document.getElementById('inputAvisoTitulo').value.trim();
        const tipo = document.getElementById('inputAvisoTipo').value;
        const conteudo = document.getElementById('inputAvisoConteudo').value.trim();
        if (!titulo || !tipo || !conteudo) { alert('Preencha título, tipo e conteúdo'); return; }

        try {
            const res = await fetch('/dashboards/api/avisos/criar/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                body: JSON.stringify({ titulo, tipo, conteudo })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Erro ao criar aviso');
            if (modalAviso) modalAviso.hide();
            fetchAvisosEventos();
        } catch (err) {
            alert(err.message || 'Erro de rede');
        }
    };

    // salvar evento
    window.salvarEvento = async function() {
        const titulo = document.getElementById('inputEventoTitulo').value.trim();
        const dataParte = document.getElementById('inputEventoDataEvento').value;
        const horaParte = document.getElementById('inputEventoHoraEvento').value || '00:00';
        const local = document.getElementById('inputEventoLocal').value.trim();
        const descricao = document.getElementById('inputEventoDescricao').value.trim();

        if (!titulo || !dataParte) { alert('Preencha título e data do evento'); return; }
        const iso = `${dataParte}T${horaParte}`;

        try {
            const res = await fetch('/dashboards/api/eventos/criar/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
                body: JSON.stringify({ titulo, descricao, data_evento: iso, local })
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Erro ao criar evento');
            if (modalEvento) modalEvento.hide();
            fetchAvisosEventos();
        } catch (err) {
            alert(err.message || 'Erro de rede');
        }
    };

    // client helpers for edit/delete (placeholders: re-fetch after action)
    window.editarAvisoClient = function(id) { alert('Edição disponível via backend posteriormente.'); };
    window.deletarAvisoClient = function(id) { alert('Remoção disponível via backend posteriormente.'); };
    window.editarEventoClient = function(id) { alert('Edição disponível via backend posteriormente.'); };
    window.deletarEventoClient = function(id) { alert('Remoção disponível via backend posteriormente.'); };

    // inicial fetch
    fetchAvisosEventos();
});
