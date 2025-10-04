# 🎨 SINASC Dashboard - Design System

**Versão:** 2.0  
**Data:** Outubro 2025  
**Status:** ✅ Implementado

---

## 📋 Visão Geral

Este documento descreve o sistema de design completo do SINASC Dashboard, garantindo consistência visual, acessibilidade e experiência profissional em toda a aplicação.

---

## 🎨 Paleta de Cores

### Cores Principais

```css
Primary (Azul)
├─ Main:       #2196f3  /* Cor principal da marca */
├─ Dark:       #1976d2  /* Ênfase, hover states */
├─ Light:      #64b5f6  /* Backgrounds, estados secundários */
└─ Lightest:   #e3f2fd  /* Backgrounds sutis */
```

### Cores Semânticas

```css
Success (Verde)
├─ Main:       #4caf50  /* Indicadores positivos */
└─ Light:      #81c784  /* Estados hover */

Warning (Laranja)
├─ Main:       #ff9800  /* Avisos, cesárea */
└─ Dark:       #f57c00  /* Ênfase em warnings */

Danger (Vermelho)
├─ Main:       #f44336  /* Alertas, indicadores críticos */
└─ Light:      #e57373  /* Estados hover */

Info (Ciano)
├─ Main:       #00bcd4  /* Informações neutras */
└─ Dark:       #0097a7  /* Ênfase */
```

### Escala de Cinza

```css
Gray Scale
├─ 50:  #fafafa  /* Backgrounds muito claros */
├─ 100: #f5f5f5  /* Backgrounds principais */
├─ 200: #eeeeee  /* Bordas sutis */
├─ 300: #e0e0e0  /* Bordas padrão */
├─ 400: #bdbdbd  /* Elementos desativados */
├─ 500: #9e9e9e  /* Texto secundário */
├─ 600: #757575  /* Texto terciário */
├─ 700: #616161  /* Texto principal muted */
├─ 800: #424242  /* Texto principal */
└─ 900: #212121  /* Texto enfático */
```

---

## 📝 Tipografia

### Família de Fontes

```css
Primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif
Monospace: 'SF Mono', 'Monaco', 'Inconsolata', 'Consolas', monospace
```

**Importação:**
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap">
```

### Escala Tipográfica

| Elemento | Tamanho | Peso | Altura Linha | Uso |
|----------|---------|------|--------------|-----|
| H1 | 2.5rem (40px) | 800 | 1.2 | Títulos principais |
| H2 | 2rem (32px) | 700 | 1.2 | Seções principais |
| H3 | 1.75rem (28px) | 700 | 1.2 | Subsections |
| H4 | 1.5rem (24px) | 600 | 1.2 | Títulos de cards |
| H5 | 1.25rem (20px) | 600 | 1.2 | Subtítulos |
| H6 | 1rem (16px) | 600 | 1.2 | Labels enfatizados |
| Body | 1rem (16px) | 400 | 1.6 | Texto padrão |
| Lead | 1.25rem (20px) | 400 | 1.6 | Texto introdutório |
| Small | 0.875rem (14px) | 400 | 1.4 | Texto secundário |

### Hierarquia de Peso

- **300** (Light): Uso mínimo
- **400** (Regular): Corpo de texto
- **500** (Medium): Labels, botões
- **600** (Semi-Bold): Subtítulos
- **700** (Bold): Títulos, ênfase
- **800** (Extra-Bold): H1, brand

---

## 📐 Espaçamento

### Sistema de Escala (8px base)

```css
xs:  0.25rem  /* 4px  - Spacing interno mínimo */
sm:  0.5rem   /* 8px  - Gaps pequenos */
md:  1rem     /* 16px - Espaçamento padrão */
lg:  1.5rem   /* 24px - Seções */
xl:  2rem     /* 32px - Entre componentes */
2xl: 3rem     /* 48px - Grandes seções */
3xl: 4rem     /* 64px - Separação máxima */
```

### Aplicação Prática

```
Padding interno de cards:     var(--spacing-lg)  /* 24px */
Margin entre cards:           var(--spacing-md)  /* 16px */
Gap entre seções:             var(--spacing-2xl) /* 48px */
Padding de containers:        var(--spacing-xl)  /* 32px */
```

---

## 🔲 Border Radius

```css
sm:  0.25rem  /* 4px  - Elementos pequenos */
md:  0.5rem   /* 8px  - Botões, inputs */
lg:  0.75rem  /* 12px - Cards principais */
xl:  1rem     /* 16px - Cards especiais, imagens */
```

---

## ✨ Sombras

### Níveis de Elevação

```css
Shadow SM (Elevação 1)
├─ Uso: Botões, inputs hover
└─ CSS: 0 1px 2px 0 rgba(0, 0, 0, 0.05)

Shadow MD (Elevação 2)
├─ Uso: Cards padrão
└─ CSS: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 
        0 2px 4px -1px rgba(0, 0, 0, 0.06)

Shadow LG (Elevação 3)
├─ Uso: Cards hover, dropdowns
└─ CSS: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
        0 4px 6px -2px rgba(0, 0, 0, 0.05)

Shadow XL (Elevação 4)
├─ Uso: Modais, popups
└─ CSS: 0 20px 25px -5px rgba(0, 0, 0, 0.1),
        0 10px 10px -5px rgba(0, 0, 0, 0.04)
```

---

## 🎭 Componentes

### Cards

**Variações:**

1. **Card Padrão**
```css
Background: white
Border: none
Border-radius: 12px (lg)
Shadow: md
Transition: all 250ms ease-in-out
```

2. **Card Hover**
```css
Shadow: lg
Transform: translateY(-2px)
```

3. **Card com Header**
```css
Header Background: linear-gradient(135deg, #f5f5f5, white)
Header Border-bottom: 2px solid #e0e0e0
Header Padding: 16px 24px
```

### Navbar

```css
Background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)
Border-bottom: 3px solid #2196f3
Box-shadow: var(--shadow-lg)
Padding: 16px 32px
```

**Links:**
```css
Color: rgba(255, 255, 255, 0.9)
Hover Background: rgba(255, 255, 255, 0.1)
Active Background: rgba(255, 255, 255, 0.2)
Border-radius: 8px
Transition: all 250ms ease-in-out
```

### Botões

```css
Primary Button
├─ Background: linear-gradient(135deg, #2196f3, #1976d2)
├─ Padding: 8px 24px
├─ Border-radius: 8px
├─ Font-weight: 600
└─ Hover: translateY(-2px) + shadow-md
```

---

## 📊 Gráficos (Plotly)

### Configuração de Layout

```python
COMMON_LAYOUT = {
    "template": "plotly_white",
    "font": {
        "family": "Inter, sans-serif",
        "size": 13,
        "color": "#424242"
    },
    "plot_bgcolor": "white",
    "paper_bgcolor": "white",
    "xaxis": {
        "showgrid": False,
        "showline": True,
        "linewidth": 2,
        "linecolor": "#e0e0e0"
    },
    "yaxis": {
        "showgrid": True,
        "gridwidth": 1,
        "gridcolor": "#f5f5f5"
    }
}
```

### Cores dos Indicadores

| Indicador | Cor | Código |
|-----------|-----|--------|
| Baixo Peso | Warning | #ff9800 |
| Adolescentes | Info | #00bcd4 |
| APGAR5 Baixo | Danger | #f44336 |
| Cesárea | Warning | #ff9800 |
| Prematuros | Danger | #f44336 |
| Hospitalar | Primary | #2196f3 |

### Legenda

```python
LEGEND_CONFIG = {
    "orientation": "h",
    "yanchor": "bottom",
    "y": -0.25,
    "xanchor": "center",
    "x": 0.5,
    "bgcolor": "rgba(255, 255, 255, 0.8)",
    "bordercolor": "#e0e0e0",
    "borderwidth": 1
}
```

---

## 🎯 Ícones

### Font Awesome - Mapeamento Semântico

| Conceito | Ícone | Classe | Cor |
|----------|-------|--------|-----|
| Nascimentos | 👶 | `fa-baby` | Primary (#2196f3) |
| Baixo Peso | ⚖️ | `fa-weight-hanging` | Warning Dark (#f57c00) |
| Adolescentes | 👥 | `fa-user-friends` | Info Dark (#0097a7) |
| APGAR5 | ❤️ | `fa-heartbeat` | Danger (#f44336) |
| Cesárea | 🏥 | `fa-procedures` | Warning (#ff9800) |
| Prematuros | ⚠️ | `fa-exclamation-triangle` | Danger (#f44336) |
| Hospital | 🏥 | `fa-hospital` | Primary (#2196f3) |

### Tamanhos

```css
Small:  14px  /* Inline com texto */
Base:   16px  /* Padrão */
Large:  24px  /* fa-lg */
2X:     32px  /* fa-2x - Destaque em cards */
3X:     48px  /* fa-3x - Headers */
```

---

## ♿ Acessibilidade

### Contraste de Cores

Todas as combinações de cores atendem **WCAG 2.1 Nível AA**:

- Texto normal: Contraste mínimo 4.5:1
- Texto grande: Contraste mínimo 3:1
- Elementos de UI: Contraste mínimo 3:1

### Foco de Teclado

```css
Focus Visible
├─ Outline: 3px solid #64b5f6 (primary-light)
├─ Outline-offset: 2px
└─ Todos os elementos interativos
```

### Movimento Reduzido

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

### Alto Contraste

```css
@media (prefers-contrast: high) {
    --primary-500: #1565c0;  /* Azul mais escuro */
    --danger: #c62828;       /* Vermelho mais escuro */
}
```

---

## 📱 Responsividade

### Breakpoints

```css
Mobile:       < 768px   (sm)
Tablet:       768-991px (md)
Desktop:      992-1199px (lg)
Large Desktop: ≥1200px  (xl)
```

### Comportamento por Dispositivo

**Mobile (<768px):**
- Cards em coluna única
- Navbar colapsável
- Fonte reduzida em 10%
- Padding reduzido

**Tablet (768-991px):**
- Cards em 2 colunas
- Gráficos em grid 2x2

**Desktop (≥992px):**
- Cards em até 3 colunas
- Layout completo
- Hover effects ativos

---

## 🎬 Animações

### Transições

```css
Fast:  150ms  /* Hover simples */
Base:  250ms  /* Padrão para a maioria */
Slow:  350ms  /* Modais, navegação */

Easing: ease-in-out (padrão)
```

### Animações Principais

**Fade In (Cards):**
```css
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
```

**Card Hover:**
```css
.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    transition: all 250ms ease-in-out;
}
```

---

## 📄 Páginas

### Estrutura Padrão

```html
<div class="container-fluid">
    <!-- Header com título e subtítulo -->
    <header style="background: gradient, border: accent">
        <h1>Título da Página</h1>
        <p class="lead">Descrição</p>
    </header>
    
    <!-- Seção 1 -->
    <section style="border-left: 4px solid primary">
        <h4>Título da Seção</h4>
        <p class="text-muted small">Descrição</p>
    </section>
    
    <!-- Cards Grid -->
    <div class="row">
        <!-- Cards aqui -->
    </div>
    
    <!-- Footer -->
    <footer class="text-center text-muted">
        Metadados e fonte
    </footer>
</div>
```

---

## 🎨 Gradientes

### Principais

```css
Primary Gradient (Navbar, Buttons)
├─ background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%)

Card Header Gradient
├─ background: linear-gradient(135deg, #f5f5f5 0%, white 100%)

Hero Gradient
├─ background: linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)
```

---

## 🎯 Melhores Práticas

### DO ✅

- Usar variáveis CSS para cores e espaçamento
- Manter consistência de border-radius em componentes similares
- Aplicar sombras progressivamente (sm → md → lg)
- Usar Inter font para todo o texto
- Aplicar hover states em elementos interativos
- Usar ícones Font Awesome semanticamente
- Manter contraste WCAG AA em textos
- Usar gradientes sutis em backgrounds

### DON'T ❌

- Misturar múltiplas famílias de fontes
- Usar cores fora da paleta definida
- Aplicar múltiplas sombras no mesmo elemento
- Ignorar estados de hover/focus
- Usar cores puras sem considerar contraste
- Abusar de animações (pode causar náusea)
- Ignorar comportamento mobile
- Usar font-sizes arbitrárias (seguir escala)

---

## 📦 Arquivos do Design System

```
dashboard/
├── assets/
│   └── custom.css           # Todas as regras CSS
├── config/
│   └── settings.py          # Paleta de cores, configurações
└── app.py                   # Navbar e estrutura global
```

---

## 🔄 Versionamento

**v2.0 (Atual):**
- ✅ Design system completo implementado
- ✅ Paleta de cores moderna
- ✅ Tipografia Inter
- ✅ Componentes padronizados
- ✅ Acessibilidade WCAG AA
- ✅ Responsividade mobile-first

**v1.0 (Anterior):**
- Bootstrap padrão
- Cores desorganizadas
- Sem design system

---

## 📚 Referências

- **Material Design 3:** https://m3.material.io/
- **Inter Font:** https://rsms.me/inter/
- **WCAG 2.1:** https://www.w3.org/WAI/WCAG21/quickref/
- **Plotly Themes:** https://plotly.com/python/templates/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.0/

---

**Mantido por:** Yannngn  
**Última atualização:** Outubro 2025  
**Status:** ✅ Produção
