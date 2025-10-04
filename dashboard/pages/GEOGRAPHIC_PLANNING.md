# 🗺️ Planejamento: Página de Análise Geográfica

**Data:** Outubro 2025  
**Status:** 📋 Planejamento Inicial  
**Prioridade:** Alta

---

## 📋 Visão Geral

Criar uma página interativa para análise geográfica dos nascimentos no Brasil, permitindo visualizar distribuições espaciais, comparar regiões, e identificar padrões geográficos em indicadores de saúde perinatal.

---

## 🎯 Objetivos

### Principais
1. **Visualização espacial** dos nascimentos por estado/município
2. **Comparação geográfica** de indicadores de saúde
3. **Identificação de disparidades regionais**
4. **Análise de cobertura hospitalar** por região
5. **Hotspots** de prematuridade e gravidez na adolescência

### Secundários
- Facilitar decisões de políticas públicas regionalizadas
- Identificar áreas prioritárias para investimento
- Comparar desempenho entre estados/municípios

---

## 📊 Dados Disponíveis

### ⭐ Indicadores Prioritários

Os indicadores mais relevantes para análise de saúde pública são as **taxas** ao invés de médias:

**🎯 Indicadores Principais (Ordem de Importância):**
1. **Taxa de Baixo Peso ao Nascer** (`low_birth_weight_pct`) - <2.500g
2. **Taxa de Prematuridade** (`preterm_birth_pct`) - <37 semanas
3. **Taxa de APGAR5 Baixo** (`low_apgar5_pct`) - <7 no 5º minuto
4. **Taxa de Gravidez na Adolescência** (`adolescent_pregnancy_pct`) - <20 anos
5. **Taxa de Cesárea** (`cesarean_pct`) - Comparar com OMS (15%)
6. **Taxa de Nascimento Hospitalar** (`hospital_birth_pct`) - Cobertura

**📊 Indicadores Secundários (Médias - menor prioridade):**
- Idade Materna Média (`IDADEMAE_mean`) - Ainda relevante
- Peso Médio ao Nascer (`PESO_mean`) - Ainda relevante
- ~~Idade Gestacional Média~~ - Menos importante
- ~~APGAR 5min Médio~~ - Menos importante

> **Nota:** As taxas são melhores indicadores porque identificam populações em risco e permitem comparações com metas da OMS e Ministério da Saúde.

### Arquivos de Agregados Geográficos

#### **Por Estado (state_YYYY.parquet)**
```python
Colunas disponíveis:
- state_code: Código do estado (2 dígitos)
- total_births: Total de nascimentos
- PESO_mean, PESO_median, PESO_std: Peso ao nascer
- IDADEMAE_mean, IDADEMAE_median: Idade materna
- SEMAGESTAC_mean, SEMAGESTAC_median: Idade gestacional
- APGAR1_mean, APGAR5_mean: Scores APGAR
- cesarean_pct: Taxa de cesárea
- multiple_pregnancy_pct: Taxa de gestação múltipla
- hospital_birth_pct: Taxa de nascimento hospitalar
- preterm_birth_pct: Taxa de prematuridade
```

#### **Por Município (municipality_YYYY.parquet)**
```python
Top 500 municípios por volume de nascimentos:
- CODMUNNASC: Código do município (7 dígitos)
- total_births: Total de nascimentos
- PESO_mean, PESO_median: Peso ao nascer
- IDADEMAE_mean: Idade materna média
- APGAR5_mean: Score APGAR 5min
- cesarean_pct: Taxa de cesárea
```

### Dados Complementares

#### **IBGE (data/IBGE/)**
- `municipalities.json`: Nomes e códigos de municípios
- População por município (se disponível)
- Coordenadas geográficas

#### **GeoJSON do Brasil**
- Estados brasileiros com geometrias
- Necessário para mapas choropleth

---

## 🎨 Design da Interface

### Layout Proposto

```
┌─────────────────────────────────────────────────────────────┐
│  🗺️ ANÁLISE GEOGRÁFICA                                      │
│  Distribuição Espacial dos Nascimentos                      │
├─────────────────────────────────────────────────────────────┤
│  📅 Ano: [Dropdown: 2024 ▼]  📊 Indicador: [Dropdown ▼]    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🗺️ MAPA CHOROPLETH DO BRASIL                        │   │
│  │                                                      │   │
│  │  [Mapa interativo colorido por indicador selecionado]│   │
│  │                                                      │   │
│  │  Legenda: [Gradiente de cores]                      │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────┬───────────────────┬───────────────┐ │
│  │ 📊 Top 10 Estados │ 📉 Bottom 10      │ 📍 Destaques  │ │
│  │                   │                   │               │ │
│  │ [Tabela ordenada] │ [Tabela ordenada] │ [Info cards]  │ │
│  └───────────────────┴───────────────────┴───────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 📊 COMPARAÇÃO REGIONAL (Norte, Nordeste, etc.)      │   │
│  │                                                      │   │
│  │  [Gráfico de barras agrupadas por região]           │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │ 🏆 Ranking Municípios│ 📈 Dispersão Indicadores     │   │
│  │                      │                              │   │
│  │ [Top 20 municípios]  │ [Scatter: Taxa vs Volume]   │   │
│  └──────────────────────┴──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Componentes Principais

### 1. **Seletor de Ano e Indicador**

```python
# Dropdowns para controle
year_dropdown = dcc.Dropdown(
    id="geo-year-dropdown",
    options=[2019, 2020, 2021, 2022, 2023, 2024],
    value=2024
)

indicator_dropdown = dcc.Dropdown(
    id="geo-indicator-dropdown",
    options=[
        {"label": "Total de Nascimentos", "value": "total_births"},
        {"label": "Taxa de Cesárea (%)", "value": ""},
        {"label": "Taxa de Prematuridade (%)", "value": "preterm_birth_pct"},
        {"label": "Taxa de Baixo Peso ao Nascer (%)", "value": "low_birth_weight_pct"},
        {"label": "Taxa de APGAR5 Baixo (%)", "value": "low_apgar5_pct"},
        {"label": "Taxa de Gravidez na Adolescência (%)", "value": "adolescent_pregnancy_pct"},
        {"label": "Taxa de Nascimento Hospitalar (%)", "value": "hospital_birth_pct"},
        {"label": "Idade Materna Média (anos)", "value": "IDADEMAE_mean"},
        {"label": "Peso Médio ao Nascer (g)", "value": "PESO_mean"},
    ],
    value="total_births"
)
```

### 2. **Mapa Choropleth Interativo**

**Tecnologia:** `plotly.graph_objects.Choropleth`

**Características:**
- Coloração por indicador selecionado
- Hover com informações detalhadas
- Zoom e pan interativos
- Escala de cores adequada (divergente ou sequencial)
- Centralização no Brasil

**Paleta de Cores Sugerida:**
- **Volume (nascimentos):** Viridis (azul → amarelo → verde)
- **Taxas positivas (hospitalar):** Blues (azul claro → azul escuro)
- **Taxas negativas (cesárea, prematuros):** Reds (amarelo → laranja → vermelho)
- **Médias (idade, peso):** RdYlGn (vermelho → amarelo → verde)

### 3. **Rankings e Comparações**

#### **Top 10 Estados**
```python
# Tabela com os 10 melhores estados no indicador
dbc.Table(
    [
        html.Thead([
            html.Tr([
                html.Th("Ranking"),
                html.Th("Estado"),
                html.Th("Valor"),
                html.Th("% do Total"),
            ])
        ]),
        html.Tbody(id="geo-top-states-table")
    ],
    striped=True,
    bordered=True,
    hover=True
)
```

#### **Bottom 10 Estados**
- Mesma estrutura, ordenação inversa
- Útil para identificar áreas de atenção

#### **Cards de Destaques**
```python
# Maior, menor, média nacional
- 🏆 Estado com maior valor
- ⚠️ Estado com menor valor
- 📊 Média nacional
- 📈 Desvio padrão
```

### 4. **Comparação por Região**

**Regiões Brasileiras:**
- Norte (11, 12, 13, 14, 15, 16, 17)
- Nordeste (21, 22, 23, 24, 25, 26, 27, 28, 29)
- Sudeste (31, 32, 33, 35)
- Sul (41, 42, 43)
- Centro-Oeste (50, 51, 52, 53)

**Gráfico:** Barras agrupadas ou boxplot por região

### 5. **Análise Municipal**

#### **Ranking Top 20 Municípios**
- Tabela com os 20 principais municípios
- Nome do município, estado, valor do indicador

#### **Scatter Plot: Volume vs Indicador**
- Eixo X: Total de nascimentos
- Eixo Y: Indicador selecionado
- Permite identificar outliers
- Tamanho dos pontos proporcional à população (se disponível)

---

## 🔧 Implementação Técnica

### Estrutura de Arquivos

```
dashboard/pages/
├── geographic.py          # Página principal
└── geographic_utils.py    # Funções auxiliares

dashboard/assets/
└── brazil_states.json     # GeoJSON dos estados
```

### Funções Auxiliares Necessárias

```python
# geographic_utils.py

def load_brazil_geojson() -> dict:
    """Carrega GeoJSON dos estados brasileiros."""
    pass

def get_state_name_from_code(code: str) -> str:
    """Converte código UF em nome do estado."""
    STATE_NAMES = {
        "11": "Rondônia", "12": "Acre", "13": "Amazonas",
        "14": "Roraima", "15": "Pará", "16": "Amapá",
        "17": "Tocantins", "21": "Maranhão", "22": "Piauí",
        # ... todos os estados
    }
    return STATE_NAMES.get(code, "Desconhecido")

def get_region_from_state_code(code: str) -> str:
    """Retorna a região a partir do código do estado."""
    first_digit = code[0]
    regions = {
        "1": "Norte",
        "2": "Nordeste",
        "3": "Sudeste",
        "4": "Sul",
        "5": "Centro-Oeste"
    }
    return regions.get(first_digit, "Desconhecido")

def aggregate_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega dados por região geográfica."""
    df['region'] = df['state_code'].apply(get_region_from_state_code)
    return df.groupby('region').agg({...})

def format_indicator_value(value: float, indicator: str) -> str:
    """Formata valor do indicador para exibição (com unidade)."""
    if 'pct' in indicator:
        return f"{value:.1f}%".replace(".", ",")
    elif indicator == 'PESO_mean':
        return f"{value:.0f}g"
    elif indicator == 'IDADEMAE_mean':
        return f"{value:.1f}".replace(".", ",")
    else:
        return f"{value:,.0f}".replace(",", ".")

def get_color_scale(indicator: str) -> list:
    """Retorna escala de cores apropriada para o indicador."""
    if indicator in ['', 'preterm_birth_pct', 'low_birth_weight_pct', 'low_apgar5_pct', 'adolescent_pregnancy_pct']:
        return 'Reds'  # Valores altos = ruim (indicadores negativos)
    elif indicator in ['hospital_birth_pct']:
        return 'Blues'  # Valores altos = bom
    else:
        return 'Viridis'  # Neutro (médias)
```

### Callbacks Principais

```python
@app.callback(
    Output("geo-choropleth-map", "figure"),
    [Input("geo-year-dropdown", "value"),
     Input("geo-indicator-dropdown", "value")]
)
def update_choropleth_map(year: int, indicator: str):
    """Atualiza mapa choropleth baseado em ano e indicador."""
    pass

@app.callback(
    [Output("geo-top-states-table", "children"),
     Output("geo-bottom-states-table", "children")],
    [Input("geo-year-dropdown", "value"),
     Input("geo-indicator-dropdown", "value")]
)
def update_rankings(year: int, indicator: str):
    """Atualiza tabelas de ranking de estados."""
    pass

@app.callback(
    Output("geo-regional-comparison", "figure"),
    [Input("geo-year-dropdown", "value"),
     Input("geo-indicator-dropdown", "value")]
)
def update_regional_comparison(year: int, indicator: str):
    """Atualiza gráfico de comparação regional."""
    pass

@app.callback(
    Output("geo-municipal-ranking", "children"),
    [Input("geo-year-dropdown", "value"),
     Input("geo-indicator-dropdown", "value")]
)
def update_municipal_ranking(year: int, indicator: str):
    """Atualiza ranking de municípios."""
    pass

@app.callback(
    Output("geo-scatter-plot", "figure"),
    [Input("geo-year-dropdown", "value"),
     Input("geo-indicator-dropdown", "value")]
)
def update_scatter_plot(year: int, indicator: str):
    """Atualiza scatter plot de volume vs indicador."""
    pass
```

---

## 📦 Dependências Necessárias

### Já Disponíveis
- ✅ plotly
- ✅ pandas
- ✅ dash
- ✅ dash-bootstrap-components

### A Obter
- 🔍 **GeoJSON dos estados brasileiros**
  - Fonte sugerida: [Brasil.io](https://brasil.io/dataset/geo/)
  - Ou IBGE: [Malhas territoriais](https://www.ibge.gov.br/geociencias/downloads-geociencias.html)

### Estrutura do GeoJSON Esperada

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "id": "11",
        "name": "Rondônia",
        "sigla": "RO"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    },
    ...
  ]
}
```

---

## 🎯 Indicadores de Sucesso

### Métricas de Performance
- ⚡ Tempo de carregamento do mapa < 2s
- 🎨 Renderização suave (60 FPS)
- 📱 Responsivo em mobile

### Funcionalidades
- ✅ Visualização de todos os 27 estados
- ✅ Mudança fluida entre indicadores
- ✅ Hover com informações detalhadas
- ✅ Rankings atualizados dinamicamente
- ✅ Comparação regional clara

### UX/UI
- ✅ Paleta de cores intuitiva
- ✅ Legendas explicativas
- ✅ Tooltips informativos
- ✅ Layout limpo e organizado

---

## 📋 Roadmap de Implementação

### Fase 1: Estrutura Básica (2-3 horas)
- [x] Criar arquivo `geographic.py`
- [ ] Definir layout básico
- [ ] Implementar seletores (ano, indicador)
- [ ] Criar placeholders para gráficos

### Fase 2: Mapa Choropleth (3-4 horas)
- [ ] Obter GeoJSON dos estados
- [ ] Implementar função de carregamento
- [ ] Criar callback do mapa
- [ ] Adicionar hover interativo
- [ ] Configurar escalas de cores

### Fase 3: Rankings e Tabelas (2 horas)
- [ ] Implementar Top 10 estados
- [ ] Implementar Bottom 10 estados
- [ ] Criar cards de destaques
- [ ] Adicionar formatação brasileira

### Fase 4: Comparação Regional (2 horas)
- [ ] Implementar função de agregação por região
- [ ] Criar gráfico de barras regionais
- [ ] Adicionar estatísticas por região

### Fase 5: Análise Municipal (2-3 horas)
- [ ] Implementar ranking de municípios
- [ ] Criar scatter plot interativo
- [ ] Adicionar filtros adicionais

### Fase 6: Polimento e Testes (1-2 horas)
- [ ] Ajustar cores e layout
- [ ] Testar responsividade
- [ ] Otimizar performance
- [ ] Adicionar documentação

**Tempo Total Estimado:** 12-16 horas

---

## 🎨 Paleta de Cores Geográfica

### Por Tipo de Indicador

```python
COLOR_SCALES = {
    # Indicadores de volume (mais = melhor)
    "total_births": {
        "scale": "Viridis",
        "reversescale": False,
        "description": "Azul (baixo) → Amarelo → Verde (alto)"
    },
    
    # Indicadores negativos (mais = pior)
    "": {
        "scale": "YlOrRd",
        "reversescale": False,
        "description": "Amarelo (baixo) → Laranja → Vermelho (alto)"
    },
    "preterm_birth_pct": {
        "scale": "YlOrRd",
        "reversescale": False,
        "description": "Amarelo (baixo) → Laranja → Vermelho (alto)"
    },
    "low_birth_weight_pct": {
        "scale": "YlOrRd",
        "reversescale": False,
        "description": "Amarelo (baixo) → Laranja → Vermelho (alto)"
    },
    "low_apgar5_pct": {
        "scale": "Reds",
        "reversescale": False,
        "description": "Rosa (baixo) → Vermelho escuro (alto)"
    },
    "adolescent_pregnancy_pct": {
        "scale": "OrRd",
        "reversescale": False,
        "description": "Laranja claro (baixo) → Vermelho (alto)"
    },
    
    # Indicadores positivos (mais = melhor)
    "hospital_birth_pct": {
        "scale": "Blues",
        "reversescale": False,
        "description": "Azul claro (baixo) → Azul escuro (alto)"
    },
    
    # Indicadores neutros
    "IDADEMAE_mean": {
        "scale": "RdYlBu",
        "reversescale": True,
        "description": "Vermelho (jovem) → Amarelo → Azul (mais velha)"
    },
    "PESO_mean": {
        "scale": "RdYlGn",
        "reversescale": False,
        "description": "Vermelho (baixo) → Amarelo → Verde (alto)"
    },
}
```

---

## 📊 Exemplos de Insights Esperados

### Análise de Cesárea
- Identificar estados com taxas muito acima da recomendação OMS (15%)
- Comparar regiões (Sul/Sudeste vs Norte/Nordeste)
- Verificar correlação com nível de urbanização

### Análise de Prematuridade
- Identificar hotspots de prematuridade
- Comparar com cobertura hospitalar
- Analisar relação com idade materna

### Análise de Baixo Peso ao Nascer
- Identificar estados com maiores taxas de <2.500g
- Correlacionar com prematuridade
- Comparar com metas internacionais

### Análise de APGAR5 Baixo
- Mapear estados com maiores problemas de vitalidade neonatal
- Verificar relação com cobertura hospitalar
- Identificar necessidade de melhorias na assistência ao parto

### Análise de Gravidez na Adolescência
- Identificar estados com maiores taxas de gestação <20 anos
- Comparar regiões Norte/Nordeste vs Sul/Sudeste
- Relacionar com políticas de planejamento familiar

### Distribuição Geográfica
- Concentração de nascimentos no Sudeste
- Diferenças urbano/rural
- Disparidades regionais em indicadores de qualidade

---

## 💡 Por que Taxas são Melhores que Médias?

### Vantagens dos Indicadores de Taxa

**1. Identificação de Populações em Risco**
- Taxas mostram a **proporção** de casos problemáticos
- Médias podem mascarar problemas graves em subgrupos
- Exemplo: APGAR5 médio de 8.5 pode esconder 2% de bebês com APGAR <7

**2. Comparabilidade Internacional**
- OMS e Ministério da Saúde definem metas em **taxas**, não médias
- Exemplo: OMS recomenda cesárea <15% (taxa), não peso médio
- Facilita benchmarking com outros países

**3. Acionabilidade para Políticas Públicas**
- Taxas indicam **quantas pessoas** precisam de intervenção
- Médias são descritivas, taxas são prescritivas
- Exemplo: "8% de baixo peso" → intervenção nutricional para gestantes

**4. Detecção de Outliers e Extremos**
- Taxas capturam casos extremos (muito baixo peso, APGAR crítico)
- Médias são influenciadas pela maioria "normal"
- Exemplo: Taxa de prematuros extremos (<28 semanas) é crítica

**5. Monitoramento de Metas**
```
✅ Taxa de baixo peso: Meta <10% (OMS)
✅ Taxa de cesárea: Meta <15% (OMS)
✅ Taxa de prematuridade: Meta <10% (Brasil)
✅ Taxa de APGAR5 <7: Meta <1% (ideal)

❌ Peso médio ao nascer: Qual seria a meta?
❌ APGAR5 médio: Difícil definir threshold
```

### Quando Médias são Úteis

**Ainda relevantes para contexto:**
- **Idade Materna Média**: Tendências demográficas (envelhecimento/rejuvenescimento)
- **Peso Médio**: Tendências populacionais gerais

**Mas sempre combine com taxas:**
- Peso médio + taxa de baixo peso
- Idade média + taxa de adolescentes

---

## 🔄 Integrações Futuras

### Fase 2 (Futuro)
- [ ] Análise temporal geográfica (evolução ao longo dos anos)
- [ ] Comparação entre dois estados lado a lado
- [ ] Exportação de dados regionais
- [ ] Análise por mesorregiões
- [ ] Correlação com dados socioeconômicos (IDH, PIB per capita)

### Visualizações Avançadas
- [ ] Mapa de calor (heatmap) com densidade
- [ ] Animação temporal (evolução dos indicadores)
- [ ] Gráficos de rede (fluxo entre estados)
- [ ] Análise de clusters geográficos

---

## 📚 Referências

### Dados Geográficos
- **IBGE:** https://www.ibge.gov.br/geociencias/downloads-geociencias.html
- **Brasil.io:** https://brasil.io/dataset/geo/
- **Natural Earth:** https://www.naturalearthdata.com/

### Bibliotecas
- **Plotly Choropleth:** https://plotly.com/python/choropleth-maps/
- **Dash Bootstrap:** https://dash-bootstrap-components.opensource.faculty.ai/

### Inspiração de Design
- **Our World in Data:** https://ourworldindata.org/
- **Google COVID-19 Dashboard:** https://www.google.com/covid19/
- **John Hopkins Dashboard:** https://coronavirus.jhu.edu/map.html

---

## ✅ Próximos Passos

1. ✅ **Revisar e aprovar este planejamento**
2. ⏳ **Obter GeoJSON dos estados brasileiros**
3. ⏳ **Criar estrutura básica do arquivo `geographic.py`**
4. ⏳ **Implementar primeiro protótipo do mapa**
5. ⏳ **Testar com dados reais**
6. ⏳ **Iterar e refinar**

---

**Documento criado em:** Outubro 2025  
**Última atualização:** Outubro 2025  
**Responsável:** AI Assistant  
**Status:** 📋 Aguardando aprovação para implementação
