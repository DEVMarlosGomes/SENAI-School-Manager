# 🛠️ Guia de Customização - UI/UX Responsiva

## Introdução

Este arquivo contém dicas e exemplos de como customizar e estender o CSS responsivo implementado.

---

## 📐 Variáveis CSS Disponíveis

Todas as variáveis estão definidas em `:root` no arquivo `static/css/home.css`:

```css
:root {
    /* Cores */
    --senai-red: #c41e3a;
    --senai-dark: #1a1a1a;
    --senai-light: #f8f9fa;
    
    /* Gradientes */
    --gradient-primary: linear-gradient(135deg, #c41e3a 0%, #e74c3c 100%);
    --gradient-secondary: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    
    /* Transição padrão */
    --transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    
    /* Espaçamento responsivo */
    --spacing-xs: clamp(0.5rem, 2vw, 1rem);
    --spacing-sm: clamp(1rem, 2.5vw, 1.5rem);
    --spacing-md: clamp(1.5rem, 3vw, 2rem);
    --spacing-lg: clamp(2rem, 4vw, 3rem);
    --spacing-xl: clamp(3rem, 5vw, 4rem);
    
    /* Tipografia responsiva */
    --font-size-h1: clamp(1.8rem, 6vw, 3.5rem);
    --font-size-h2: clamp(1.4rem, 4vw, 2.5rem);
    --font-size-h5: clamp(1rem, 2.5vw, 1.3rem);
    --font-size-body: clamp(0.85rem, 1.5vw, 1rem);
}
```

---

## 🎨 Customizações Comuns

### 1. Mudar Cores Primárias

**Aumentar intensidade do vermelho:**
```css
:root {
    --senai-red: #D32F2F;  /* Mais vibrante */
}
```

**Adicionar nova cor secundária:**
```css
:root {
    --senai-blue: #1976D2;
    --gradient-secondary: linear-gradient(135deg, #1976D2 0%, #1565C0 100%);
}
```

Depois use em elementos:
```css
.novo-elemento {
    background: var(--senai-blue);
}
```

### 2. Aumentar Espaçamento Global

Para um design mais arejado:
```css
:root {
    --spacing-xs: clamp(0.75rem, 2.5vw, 1.25rem);  /* Aumentado */
    --spacing-sm: clamp(1.25rem, 3vw, 1.75rem);    /* Aumentado */
    --spacing-md: clamp(2rem, 3.5vw, 2.5rem);      /* Aumentado */
    --spacing-lg: clamp(2.5rem, 4.5vw, 3.5rem);    /* Aumentado */
    --spacing-xl: clamp(3.5rem, 5.5vw, 4.5rem);    /* Aumentado */
}
```

### 3. Fazer Tipografia Maior

Para melhor legibilidade em mobile:
```css
:root {
    --font-size-h1: clamp(2rem, 7vw, 4rem);       /* Maior mínimo */
    --font-size-h2: clamp(1.6rem, 4.5vw, 2.8rem); /* Maior mínimo */
    --font-size-body: clamp(0.95rem, 1.8vw, 1.1rem); /* Maior */
}
```

### 4. Aumentar Velocidade de Transições

Para interface mais responsiva:
```css
:root {
    --transition: all 0.15s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}
```

### 5. Mudar Easing de Animações

Para efeito mais suave:
```css
:root {
    --transition: all 0.3s ease-in-out;
}
```

---

## 📱 Adicionar Novos Breakpoints

Se precisar de um breakpoint adicional:

```css
/* Extra large tablets */
@media (max-width: 1400px) {
    .container-fluid {
        padding-left: var(--spacing-lg);
        padding-right: var(--spacing-lg);
    }
    
    .hero-banner {
        min-height: 70vh;
    }
}

/* Ultra-wide screens */
@media (min-width: 2560px) {
    :root {
        --spacing-lg: clamp(3rem, 3vw, 4rem);
        --font-size-h1: clamp(3rem, 3vw, 4.5rem);
    }
}
```

---

## 🎭 Criar Novas Variantes de Componentes

### Exemplo: Botão com tamanho responsivo

```css
.btn-responsive {
    padding: clamp(10px, 1.5vw, 16px) clamp(20px, 2.5vw, 32px);
    font-size: clamp(0.8rem, 1.2vw, 1rem);
    border-radius: clamp(6px, 1.5vw, 10px);
    transition: var(--transition);
}

.btn-responsive:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(196, 30, 58, 0.3);
}
```

### Exemplo: Card customizado

```css
.custom-card {
    background: white;
    border-radius: clamp(8px, 2vw, 16px);
    padding: clamp(15px, 3vw, 30px);
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
    transition: var(--transition);
}

.custom-card:hover {
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    transform: translateY(-5px);
}
```

### Exemplo: Container responsivo

```css
.responsive-container {
    max-width: clamp(320px, 90vw, 1200px);
    margin-left: auto;
    margin-right: auto;
    padding-left: var(--spacing-md);
    padding-right: var(--spacing-md);
}
```

---

## 🔍 Debugging e Testes

### Ver tamanho viewport atual

```css
body::before {
    content: attr(data-viewport);
    position: fixed;
    bottom: 10px;
    right: 10px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    padding: 10px 15px;
    border-radius: 5px;
    z-index: 9999;
    font-size: 12px;
}
```

### Adicionar grid de debug

```css
body.debug {
    background-image: 
        linear-gradient(rgba(0, 0, 255, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 0, 255, 0.05) 1px, transparent 1px);
    background-size: 10px 10px;
}
```

### Adicionar em HTML (durante debug):
```html
<body class="debug">
```

---

## 📊 Exemplos Práticos

### 1. Criar Seção Customizada

```html
<section class="custom-section">
    <div class="container-fluid">
        <h2>Minha Seção</h2>
        <div class="custom-grid">
            <div class="custom-item">Item 1</div>
            <div class="custom-item">Item 2</div>
            <div class="custom-item">Item 3</div>
        </div>
    </div>
</section>
```

```css
.custom-section {
    padding: var(--spacing-xl) var(--spacing-lg);
    background: linear-gradient(135deg, var(--senai-light) 0%, white 100%);
}

.custom-section h2 {
    font-size: var(--font-size-h2);
    margin-bottom: var(--spacing-lg);
    text-align: center;
    color: var(--senai-dark);
}

.custom-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(clamp(200px, 25vw, 300px), 1fr));
    gap: var(--spacing-md);
}

.custom-item {
    background: white;
    padding: var(--spacing-md);
    border-radius: clamp(8px, 2vw, 12px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    transition: var(--transition);
}

.custom-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(196, 30, 58, 0.1);
}
```

### 2. Implementar Dark Mode

```css
@media (prefers-color-scheme: dark) {
    :root {
        --senai-light: #2a2a2a;
        --senai-dark: #ffffff;
    }
    
    body {
        background: #1a1a1a;
        color: #ffffff;
    }
    
    .custom-item {
        background: #2a2a2a;
        color: #ffffff;
    }
}
```

### 3. Adicionar Versão de Impressão

```css
@media print {
    :root {
        --spacing-lg: 1rem;
        --font-size-h1: 2rem;
    }
    
    .no-print {
        display: none !important;
    }
    
    .container-fluid {
        width: 100%;
    }
}
```

---

## ⚡ Performance Tips

### 1. Usar `will-change` com moderação

```css
.card {
    will-change: transform;  /* Ativa GPU acceleration */
    transition: var(--transition);
}

.card:hover {
    transform: translateY(-5px);
}
```

### 2. Otimizar animações para mobile

```css
@media (prefers-reduced-motion: reduce) {
    .card {
        will-change: auto;
        transition: none;
    }
}
```

### 3. Usar `contain` para elementos complexos

```css
.card {
    contain: layout style paint;  /* Isola elemento para performance */
}
```

---

## 🔗 Links Úteis

- [MDN: clamp()](https://developer.mozilla.org/en-US/docs/Web/CSS/clamp)
- [MDN: CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [MDN: Flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)
- [CSS Tricks: Responsive Typography](https://css-tricks.com/snippets/css/fluid-typography/)

---

## 📝 Checklist de Customização

Ao customizar, não esqueça de:

- [ ] Testar em celular (375px)
- [ ] Testar em tablet (768px)
- [ ] Testar em desktop (1920px)
- [ ] Verificar com DevTools
- [ ] Testar sem JavaScript ativado
- [ ] Verificar com leitor de tela
- [ ] Verificar em navegadores antigos
- [ ] Medir performance (Lighthouse)
- [ ] Testar em conexão lenta
- [ ] Verificar com cores invertidas (accessibility)

---

## 🆘 Troubleshooting

### Problema: Layout quebrado em tablet

**Solução**: Verifique se os valores do `clamp()` estão corretos:
```css
/* Min ≤ Valor Preferido ≤ Max */
padding: clamp(1rem, 3vw, 2rem);  /* ✅ Correto */
padding: clamp(2rem, 3vw, 1rem);  /* ❌ Incorreto */
```

### Problema: Texto muito pequeno/grande em mobile

**Solução**: Ajuste o valor mínimo do `clamp()`:
```css
/* Aumentar mínimo */
font-size: clamp(1rem, 1.5vw, 1.3rem);  /* Antes: 0.85rem */
```

### Problema: Espaçamento inconsistente

**Solução**: Use as variáveis ao invés de valores hardcoded:
```css
/* ❌ Evite */
padding: 20px;
margin: 30px;

/* ✅ Use variáveis */
padding: var(--spacing-sm);
margin: var(--spacing-md);
```

### Problema: Animações travando em mobile

**Solução**: Reduza complexidade das transições:
```css
/* ❌ Complexo */
transition: all 0.3s;

/* ✅ Específico */
transition: transform 0.3s, opacity 0.3s;
```

---

## 🎓 Aprendizado Contínuo

Para se manter atualizado:

1. **Acompanhe blogueiros CSS**
   - CSS Tricks
   - Smashing Magazine
   - Web.dev

2. **Participe de comunidades**
   - Stack Overflow
   - CSS-in-Depth
   - Dev.to

3. **Teste novas funcionalidades**
   - Container Queries
   - Aspect Ratio
   - Grid Layout Avançado

---

**Última atualização**: 11 de Novembro de 2025
**Versão**: 1.0
**Autor**: GitHub Copilot
