const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null;
const inputInitHeight = chatInput.scrollHeight;

// Cria o elemento HTML da mensagem (li)
const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    // Se for mensagem recebida (bot), ícone opcional poderia ir aqui
    let chatContent = className === "outgoing" ? `<p></p>` : `<p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi;
}

// Função para gerar resposta via Backend Django
const generateResponse = (chatElement) => {
    const messageElement = chatElement.querySelector("p");

    // Faz a requisição para sua view Django
    fetch("/dashboards/api/chat-gemini/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            // Pega o CSRF Token do cookie (padrão Django) se necessário,
            // mas aqui estamos usando @csrf_exempt na view para simplificar o exemplo.
            // Se remover o @csrf_exempt, precisa passar o token aqui.
        },
        body: JSON.stringify({ message: userMessage })
    }).then(res => res.json()).then(data => {
        if (data.response) {
            messageElement.textContent = data.response;
        } else {
            messageElement.textContent = "Ops! Não entendi. Tente novamente.";
        }
    }).catch(() => {
        messageElement.textContent = "Erro de conexão com o servidor. Tente mais tarde.";
    }).finally(() => {
        chatbox.scrollTo(0, chatbox.scrollHeight);
    });
}

const handleChat = () => {
    userMessage = chatInput.value.trim();
    if(!userMessage) return;

    // Limpa e reseta altura do input
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Adiciona mensagem do usuário na tela
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    // Adiciona mensagem de "Pensando..." do bot
    setTimeout(() => {
        const incomingChatLi = createChatLi("Pensando...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

// Eventos
chatInput.addEventListener("input", () => {
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));