/**
 * Página de Comunicação - Coordenação
 * Gerencia Mensagens, Avisos, Eventos e Notificações
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Mock data
    const mockAvisos = [
        { id: 1, titulo: 'Reunião Importante', urgencia: 'Urgente', descricao: 'Reunião com coordenadores está marcada para...', data: '11/11/2025 • 10:00', publico: 'todos' },
        { id: 2, titulo: 'Atualização de Calendário', urgencia: 'Aviso', descricao: 'O calendário acadêmico foi alterado...', data: '10/11/2025 • 15:30', publico: 'todos' },
        { id: 3, titulo: 'Resultado de Processos', urgencia: 'Info', descricao: 'Os resultados de seleção foram publicados...', data: '09/11/2025 • 09:00', publico: 'alunos' },
    ];

    const mockEventos = [
        { id: 1, nome: 'Reunião Pedagógica', data: '15/11/2025', hora: '14:00', local: 'Sala de Reuniões', participantes: 12, descricao: '' },
        { id: 2, nome: 'Apresentação de Projetos', data: '20/11/2025', hora: '16:30', local: 'Auditório', participantes: 45, descricao: '' },
    ];

    // Modals
    let modalAviso, modalEvento;
    let avisoAtual = null, eventoAtual = null;

    // Inicializar modals
    if (document.getElementById('modalAviso')) {
        modalAviso = new bootstrap.Modal(document.getElementById('modalAviso'));
        modalEvento = new bootstrap.Modal(document.getElementById('modalEvento'));

        // Novo Aviso
        document.getElementById('btnNovoAviso').addEventListener('click', function() {
            avisoAtual = null;
            document.getElementById('modalAvisoTitle').textContent = 'Novo Aviso';
            document.getElementById('formAviso').reset();
            // Pré-preencer com data/hora atual
            const agora = new Date().toISOString().slice(0, 16);
            document.getElementById('inputAvisoData').value = agora;
            modalAviso.show();
        });

        // Salvar Aviso
        document.getElementById('btnSalvarAviso').addEventListener('click', function() {
            const titulo = document.getElementById('inputAvisoTitulo').value.trim();
            const urgencia = document.getElementById('inputAvisoUrgencia').value;
            const descricao = document.getElementById('inputAvisoDescricao').value.trim();
            const data = document.getElementById('inputAvisoData').value;
            const publico = document.getElementById('inputAvisoPublico').value;

            if (!titulo || !urgencia || !descricao || !data) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }

            const dataFormatada = new Date(data).toLocaleDateString('pt-BR') + ' • ' + new Date(data).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

            if (avisoAtual) {
                // Editar
                avisoAtual.titulo = titulo;
                avisoAtual.urgencia = urgencia;
                avisoAtual.descricao = descricao;
                avisoAtual.data = dataFormatada;
                avisoAtual.publico = publico;
            } else {
                // Novo
                const novoAviso = {
                    id: Math.max(...mockAvisos.map(a => a.id), 0) + 1,
                    titulo: titulo,
                    urgencia: urgencia,
                    descricao: descricao,
                    data: dataFormatada,
                    publico: publico
                };
                mockAvisos.push(novoAviso);
            }

            renderAvisos();
            modalAviso.hide();
        });

        // Novo Evento
        document.getElementById('btnNovoEvento').addEventListener('click', function() {
            eventoAtual = null;
            document.getElementById('modalEventoTitle').textContent = 'Novo Evento';
            document.getElementById('formEvento').reset();
            modalEvento.show();
        });

        // Salvar Evento
        document.getElementById('btnSalvarEvento').addEventListener('click', function() {
            const nome = document.getElementById('inputEventoNome').value.trim();
            const data = document.getElementById('inputEventoData').value;
            const hora = document.getElementById('inputEventoHora').value;
            const local = document.getElementById('inputEventoLocal').value.trim();
            const participantes = parseInt(document.getElementById('inputEventoParticipantes').value);
            const descricao = document.getElementById('inputEventoDescricao').value.trim();

            if (!nome || !data || !hora || !local || !participantes) {
                alert('Preencha todos os campos obrigatórios');
                return;
            }

            if (eventoAtual) {
                // Editar
                eventoAtual.nome = nome;
                eventoAtual.data = data;
                eventoAtual.hora = hora;
                eventoAtual.local = local;
                eventoAtual.participantes = participantes;
                eventoAtual.descricao = descricao;
            } else {
                // Novo
                const novoEvento = {
                    id: Math.max(...mockEventos.map(e => e.id), 0) + 1,
                    nome: nome,
                    data: data,
                    hora: hora,
                    local: local,
                    participantes: participantes,
                    descricao: descricao
                };
                mockEventos.push(novoEvento);
            }

            renderEventos();
            modalEvento.hide();
        });
    }

    // Renderizar avisos
    function renderAvisos() {
        const container = document.getElementById('avisosContainer');
        container.innerHTML = '';
        
        mockAvisos.forEach(aviso => {
            const urgenciaClass = aviso.urgencia === 'Urgente' ? 'border-danger' : (aviso.urgencia === 'Aviso' ? 'border-warning' : 'border-success');
            const urgenciaBg = aviso.urgencia === 'Urgente' ? 'bg-danger' : (aviso.urgencia === 'Aviso' ? 'bg-warning text-dark' : 'bg-success');

            const div = document.createElement('div');
            div.className = 'col-lg-4';
            div.innerHTML = `
                <div class="card shadow-sm border-0 border-top border-4 ${urgenciaClass}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="fw-bold mb-0">${aviso.titulo}</h6>
                            <span class="badge ${urgenciaBg}">${aviso.urgencia}</span>
                        </div>
                        <p class="small text-muted mb-2">${aviso.descricao}</p>
                        <small class="text-muted">${aviso.data}</small>
                        <div class="mt-3">
                            <button class="btn btn-xs btn-outline-primary me-1" onclick="editarAviso(${aviso.id})"><i class="fas fa-edit"></i></button>
                            <button class="btn btn-xs btn-outline-danger" onclick="deletarAviso(${aviso.id})"><i class="fas fa-trash"></i></button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(div);
        });
    }

    // Renderizar eventos
    function renderEventos() {
        const tbody = document.querySelector('#content-eventos tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        mockEventos.forEach(evento => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${evento.nome}</td>
                <td>${evento.data}</td>
                <td>${evento.hora}</td>
                <td>${evento.local}</td>
                <td><span class="badge bg-primary">${evento.participantes}</span></td>
                <td class="text-end">
                    <button class="btn btn-xs btn-outline-primary me-1" onclick="editarEvento(${evento.id})"><i class="fas fa-edit"></i></button>
                    <button class="btn btn-xs btn-outline-danger" onclick="deletarEvento(${evento.id})"><i class="fas fa-trash"></i></button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Selecionar conversas
    const conversas = document.querySelectorAll('#messagemList .list-group-item-action');
    conversas.forEach(conversa => {
        conversa.addEventListener('click', function() {
            conversas.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Enviar mensagem
    const messageForm = document.querySelector('.card-footer .input-group');
    if (messageForm) {
        messageForm.querySelector('button').addEventListener('click', function() {
            const input = messageForm.querySelector('input');
            if (input.value.trim()) {
                console.log('Mensagem enviada:', input.value);
                input.value = '';
            }
        });
    }

    // Funções globais
    window.editarAviso = function(id) {
        const aviso = mockAvisos.find(a => a.id === id);
        if (aviso) {
            avisoAtual = aviso;
            document.getElementById('modalAvisoTitle').textContent = 'Editar Aviso';
            document.getElementById('inputAvisoTitulo').value = aviso.titulo;
            document.getElementById('inputAvisoUrgencia').value = aviso.urgencia;
            document.getElementById('inputAvisoDescricao').value = aviso.descricao;
            document.getElementById('inputAvisoPublico').value = aviso.publico;
            modalAviso.show();
        }
    };

    window.deletarAviso = function(id) {
        if (confirm('Tem certeza que deseja deletar este aviso?')) {
            const index = mockAvisos.findIndex(a => a.id === id);
            if (index !== -1) {
                mockAvisos.splice(index, 1);
                renderAvisos();
            }
        }
    };

    window.editarEvento = function(id) {
        const evento = mockEventos.find(e => e.id === id);
        if (evento) {
            eventoAtual = evento;
            document.getElementById('modalEventoTitle').textContent = 'Editar Evento';
            document.getElementById('inputEventoNome').value = evento.nome;
            document.getElementById('inputEventoData').value = evento.data;
            document.getElementById('inputEventoHora').value = evento.hora;
            document.getElementById('inputEventoLocal').value = evento.local;
            document.getElementById('inputEventoParticipantes').value = evento.participantes;
            document.getElementById('inputEventoDescricao').value = evento.descricao;
            modalEvento.show();
        }
    };

    window.deletarEvento = function(id) {
        if (confirm('Tem certeza que deseja deletar este evento?')) {
            const index = mockEventos.findIndex(e => e.id === id);
            if (index !== -1) {
                mockEventos.splice(index, 1);
                renderEventos();
            }
        }
    };

    // Inicializar
    renderAvisos();
    renderEventos();
});
