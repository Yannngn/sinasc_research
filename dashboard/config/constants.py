"""
Constants and data mappings for SINASC Dashboard.
"""

# Brazilian States by Code
BRAZILIAN_STATES = {
    # North Region
    "11": {"name": "Rondônia", "abbr": "RO", "region": "North"},
    "12": {"name": "Acre", "abbr": "AC", "region": "North"},
    "13": {"name": "Amazonas", "abbr": "AM", "region": "North"},
    "14": {"name": "Roraima", "abbr": "RR", "region": "North"},
    "15": {"name": "Pará", "abbr": "PA", "region": "North"},
    "16": {"name": "Amapá", "abbr": "AP", "region": "North"},
    "17": {"name": "Tocantins", "abbr": "TO", "region": "North"},
    # Northeast Region
    "21": {"name": "Maranhão", "abbr": "MA", "region": "Northeast"},
    "22": {"name": "Piauí", "abbr": "PI", "region": "Northeast"},
    "23": {"name": "Ceará", "abbr": "CE", "region": "Northeast"},
    "24": {"name": "Rio Grande do Norte", "abbr": "RN", "region": "Northeast"},
    "25": {"name": "Paraíba", "abbr": "PB", "region": "Northeast"},
    "26": {"name": "Pernambuco", "abbr": "PE", "region": "Northeast"},
    "27": {"name": "Alagoas", "abbr": "AL", "region": "Northeast"},
    "28": {"name": "Sergipe", "abbr": "SE", "region": "Northeast"},
    "29": {"name": "Bahia", "abbr": "BA", "region": "Northeast"},
    # Southeast Region
    "31": {"name": "Minas Gerais", "abbr": "MG", "region": "Southeast"},
    "32": {"name": "Espírito Santo", "abbr": "ES", "region": "Southeast"},
    "33": {"name": "Rio de Janeiro", "abbr": "RJ", "region": "Southeast"},
    "35": {"name": "São Paulo", "abbr": "SP", "region": "Southeast"},
    # South Region
    "41": {"name": "Paraná", "abbr": "PR", "region": "South"},
    "42": {"name": "Santa Catarina", "abbr": "SC", "region": "South"},
    "43": {"name": "Rio Grande do Sul", "abbr": "RS", "region": "South"},
    # Center-West Region
    "50": {"name": "Mato Grosso do Sul", "abbr": "MS", "region": "Center-West"},
    "51": {"name": "Mato Grosso", "abbr": "MT", "region": "Center-West"},
    "52": {"name": "Goiás", "abbr": "GO", "region": "Center-West"},
    "53": {"name": "Distrito Federal", "abbr": "DF", "region": "Center-West"},
}

# Category labels (Portuguese)
CATEGORY_LABELS = {
    "LOCNASC": {
        1: "Hospital",
        2: "Outros estabelecimentos",
        3: "Domicílio",
        4: "Outros",
        5: "Aldeia Indígena",
        9: "Ignorado",
    },
    "PARTO": {
        1: "Vaginal",
        2: "Cesário",
        9: "Ignorado",
    },
    "GRAVIDEZ": {
        1: "Única",
        2: "Dupla",
        3: "Tripla ou mais",
        9: "Ignorado",
    },
    "SEXO": {
        "M": "Masculino",
        "F": "Feminino",
        "I": "Ignorado",
    },
    "ESTCIVMAE": {
        1: "Solteira",
        2: "Casada",
        3: "Viúva",
        4: "Separada/Divorciada",
        5: "União estável",
        9: "Ignorado",
    },
    "ESCMAE": {
        1: "Nenhuma",
        2: "1 a 3 anos",
        3: "4 a 7 anos",
        4: "8 a 11 anos",
        5: "12 anos ou mais",
        9: "Ignorado",
    },
}

# Metric display names
METRIC_NAMES = {
    "total_births": "Total de Nascimentos",
    "cesarean_pct": "Taxa de Cesárea (%)",
    "hospital_birth_pct": "Nascimentos em Hospital (%)",
    "multiple_pregnancy_pct": "Gravidez Múltipla (%)",
    "preterm_rate_pct": "Taxa de Prematuridade (%)",
    "PESO_mean": "Peso Médio (g)",
    "IDADEMAE_mean": "Idade Materna Média",
    "APGAR5_mean": "APGAR 5min Médio",
}

# Chart titles
CHART_TITLES = {
    "births_timeline": "Nascimentos ao Longo do Tempo",
    "cesarean_rate": "Taxa de Cesárea",
    "maternal_age": "Distribuição de Idade Materna",
    "birth_weight": "Distribuição de Peso ao Nascer",
    "apgar_scores": "Distribuição de Escores APGAR",
    "delivery_type": "Tipo de Parto",
    "births_by_state": "Nascimentos por Estado",
}

MONTH_NAMES = [
    "Jan",
    "Fev",
    "Mar",
    "Abr",
    "Mai",
    "Jun",
    "Jul",
    "Ago",
    "Set",
    "Out",
    "Nov",
    "Dez",
]
