/**
 * Responsive Layout Controller
 * Gerencia o comportamento do sidebar e interatividade em dispositivos móveis
 */

document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.layout-wrapper > div:last-child');
    
    // Função para fechar sidebar ao redimensionar
    function updateLayout() {
        const isMobile = window.innerWidth < 992;
        
        if (!isMobile && sidebar) {
            sidebar.classList.remove('show');
        }
    }
    
    // Listener para mudanças de tamanho de tela
    window.addEventListener('resize', updateLayout);
    
    // Toggle sidebar em dispositivos móveis
    function toggleSidebar() {
        if (sidebar) {
            sidebar.classList.toggle('show');
        }
    }
    
    // Botão hambúrguer (se existir)
    const hamburgerBtn = document.querySelector('[data-bs-toggle="sidebar"]');
    if (hamburgerBtn) {
        hamburgerBtn.addEventListener('click', toggleSidebar);
    }
    
    // Fechar sidebar ao clicar em um link
    const sidebarLinks = sidebar?.querySelectorAll('.btn');
    sidebarLinks?.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth < 992) {
                sidebar.classList.remove('show');
            }
        });
    });
    
    // Fechar sidebar ao clicar fora
    document.addEventListener('click', function(event) {
        if (window.innerWidth < 992 && sidebar?.classList.contains('show')) {
            if (!sidebar.contains(event.target) && !event.target.closest('[data-bs-toggle="sidebar"]')) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // Smooth scroll para links
    const smoothScrollLinks = document.querySelectorAll('a[href^="#"]');
    smoothScrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href !== '#' && document.querySelector(href)) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Animação de cards ao scroll
    if ('IntersectionObserver' in window) {
        const cards = document.querySelectorAll('.card');
        const cardObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.5s ease-out forwards';
                    cardObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        cards.forEach(card => cardObserver.observe(card));
    }
    
    // Tooltips (Bootstrap)
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Adicionar animação CSS dinamicamente
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @media (max-width: 992px) {
        #sidebar::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
            z-index: -1;
        }
        
        #sidebar.show::before {
            opacity: 1;
            pointer-events: all;
        }
    }
`;
document.head.appendChild(style);
