"""
Constants and data mappings for SINASC Dashboard.
"""

from dataclasses import dataclass


@dataclass
class CardMetricConfig:
    """Configuration for a single metric in the dashboard."""

    path: list[str]  # Path to extract value from summary dict
    format_type: str  # "number", "percentage", "years"
    unit: str  # Unit suffix (e.g., "anos", "%", "")
    card_title: str
    card_icon: str
    card_color: str

    def extract_value(self, data: dict, default: float = 0) -> float:
        """
        Extract a value from nested dictionary using the configured path.

        Args:
            data: Dictionary to extract from
            default: Default value if path not found

        Returns:
            Extracted value or default
        """
        current = data
        try:
            for key in self.path:
                current = current.get(key, {})
            return current if isinstance(current, (int, float)) else default
        except (AttributeError, TypeError):
            return default

    def format_value(self, value: float) -> str:
        """
        Format a number using Brazilian conventions based on the configured format_type and unit.

        Args:
            value: The numeric value to format

        Returns:
            Formatted string
        """
        if self.format_type == "number":
            # Format large numbers with dots as thousands separator
            formatted = f"{int(value):_}".replace("_", ".")
        elif self.format_type == "percentage":
            # Format percentages with comma as decimal separator
            formatted = f"{value:.1f}%".replace(".", ",")
        elif self.format_type == "years":
            # Format years with comma as decimal separator
            formatted = f"{value:.1f} {self.unit}".replace(".", ",")
        else:
            formatted = str(value)

        return formatted

    @staticmethod
    def calculate_yoy_change(current_value: float, prev_value: float | None) -> float | None:
        """
        Calculate year-over-year percentage change.

        Args:
            current_value: Current year's value
            prev_value: Previous year's value

        Returns:
            Percentage change or None if invalid
        """
        if prev_value is None or prev_value == 0:
            return None
        return ((current_value - prev_value) / prev_value) * 100


# Configuration for metrics displayed in year summary cards
YEAR_SUMMARY_METRICS = {
    "total_births": CardMetricConfig(
        path=["total_births"],
        format_type="number",
        unit="",
        card_title="Nascimentos Totais",
        card_icon="fas fa-baby",
        card_color="primary",
    ),
    "adolescent_pregnancy_pct": CardMetricConfig(
        path=["pregnancy", "adolescent_pregnancy_pct"],
        format_type="percentage",
        unit="anos",
        card_title="Taxa de Gestações Abaixo de 20 anos",
        card_icon="fas fa-female",
        card_color="info",
    ),
    "very_young_pregnancy_pct": CardMetricConfig(
        path=["pregnancy", "very_young_pregnancy_pct"],
        format_type="percentage",
        unit="",
        card_title="Taxa de Gestações Abaixo de 15 anos",
        card_icon="fas fa-child",
        card_color="success",
    ),
    "cesarean_pct": CardMetricConfig(
        path=["delivery_type", "cesarean_pct"],
        format_type="percentage",
        unit="",
        card_title="Taxa de Cesáreas",
        card_icon="fas fa-procedures",
        card_color="warning",
    ),
    "low_birth_weight_pct": CardMetricConfig(
        path=["health_indicators", "low_birth_weight_pct"],
        format_type="percentage",
        unit="",
        card_title="Taxa de Baixo Peso ao Nascer",
        card_icon="fas fa-weight-hanging",
        card_color="warning",
    ),
    "preterm_pct": CardMetricConfig(
        path=["pregnancy", "preterm_pct"],
        format_type="percentage",
        unit="",
        card_title="Taxa de Prematuridade",
        card_icon="fas fa-baby-carriage",
        card_color="danger",
    ),
    "hospital_birth_pct": CardMetricConfig(
        path=["location", "hospital_birth_pct"],
        format_type="percentage",
        unit="",
        card_title="Taxa de Nascimentos em Hospital",
        card_icon="fas fa-hospital",
        card_color="primary",
    ),
    "low_apgar5_pct": CardMetricConfig(
        path=["health_indicators", "low_apgar5_pct"],
        format_type="percentage",
        unit="",
        card_title="Taxa de APGAR5 Baixo",
        card_icon="fas fa-heartbeat",
        card_color="danger",
    ),
}


@dataclass
class IndicatorConfig:
    absolute: str | list[str]
    relative: str | list[str]
    absolute_title: str
    relative_title: str
    labels: str | list[str]
    colors: str | list[str]
    recommended_relative_limit: float | None
    recommended_name: str | None

    def get_absolute_columns(self) -> list[str]:
        """Get absolute columns as a list."""
        return [self.absolute] if isinstance(self.absolute, str) else self.absolute

    def get_relative_columns(self) -> list[str]:
        """Get relative columns as a list."""
        return [self.relative] if isinstance(self.relative, str) else self.relative

    def get_labels(self) -> list[str]:
        """Get labels as a list."""
        return [self.labels] if isinstance(self.labels, str) else self.labels

    def get_colors(self) -> list[str]:
        """Get colors as a list."""
        return [self.colors] if isinstance(self.colors, str) else self.colors

    def get_reference_line(self) -> dict | None:
        """Get reference line configuration if available."""
        if self.recommended_relative_limit is not None:
            return {
                "y": self.recommended_relative_limit,
                "text": self.recommended_name,
                "color": "neutral",  # Could be made configurable
            }
        return None


# TODO: add unit
INDICATOR_MAPPINGS = {
    "birth": IndicatorConfig(
        absolute="total_births",
        relative="births_per_1k",
        absolute_title="Nascimentos",
        relative_title="Nascimentos por 1.000 Habitantes",
        labels="Nascimentos",
        colors="primary",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "cesarean": IndicatorConfig(
        absolute="cesarean_count",
        relative="cesarean_pct",
        absolute_title="Cesáreas",
        relative_title="Taxa de Cesáreas (%)",
        labels="Cesáreas",
        colors="warning",
        recommended_relative_limit=15.0,
        recommended_name="Referência OMS",
    ),
    "preterm": IndicatorConfig(
        absolute=["preterm_count", "extreme_preterm_count"],
        relative=["preterm_pct", "extreme_preterm_pct"],
        absolute_title="Nascimentos Prematuros",
        relative_title="Taxa de Prematuridade (%)",
        labels=["Prematuros (<37 sem)", "Prematuros Extremos (<32 sem)"],
        colors=["warning", "danger"],
        recommended_relative_limit=10.0,
        recommended_name="Referência OMS",
    ),
    "adolescent": IndicatorConfig(
        absolute=["adolescent_pregnancy_count", "very_young_pregnancy_count"],
        relative=["adolescent_pregnancy_pct", "very_young_pregnancy_pct"],
        absolute_title="Gestações em Adolescentes",
        relative_title="Taxa de Gravidez na Adolescência (%)",
        labels=["Adolescentes (<20 anos)", "Menores de 15 anos"],
        colors=["info", "danger"],
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "low_weight": IndicatorConfig(
        absolute="low_birth_weight_count",
        relative="low_birth_weight_pct",
        absolute_title="Nascimentos com Baixo Peso",
        relative_title="Taxa de Baixo Peso ao Nascer (%)",
        labels="Baixo Peso ao Nascer",
        colors="info",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "low_apgar": IndicatorConfig(
        absolute="low_apgar5_count",
        relative="low_apgar5_pct",
        absolute_title="APGAR5 Baixo",
        relative_title="Taxa de APGAR5 Baixo (%)",
        labels="APGAR5 Baixo",
        colors="danger",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
}


BRAZILIAN_STATES = {
    "11": {"name": "Rondônia", "abbr": "RO", "region": "Norte"},
    "12": {"name": "Acre", "abbr": "AC", "region": "Norte"},
    "13": {"name": "Amazonas", "abbr": "AM", "region": "Norte"},
    "14": {"name": "Roraima", "abbr": "RR", "region": "Norte"},
    "15": {"name": "Pará", "abbr": "PA", "region": "Norte"},
    "16": {"name": "Amapá", "abbr": "AP", "region": "Norte"},
    "17": {"name": "Tocantins", "abbr": "TO", "region": "Norte"},
    "21": {"name": "Maranhão", "abbr": "MA", "region": "Nordeste"},
    "22": {"name": "Piauí", "abbr": "PI", "region": "Nordeste"},
    "23": {"name": "Ceará", "abbr": "CE", "region": "Nordeste"},
    "24": {"name": "Rio Grande do Norte", "abbr": "RN", "region": "Nordeste"},
    "25": {"name": "Paraíba", "abbr": "PB", "region": "Nordeste"},
    "26": {"name": "Pernambuco", "abbr": "PE", "region": "Nordeste"},
    "27": {"name": "Alagoas", "abbr": "AL", "region": "Nordeste"},
    "28": {"name": "Sergipe", "abbr": "SE", "region": "Nordeste"},
    "29": {"name": "Bahia", "abbr": "BA", "region": "Nordeste"},
    "31": {"name": "Minas Gerais", "abbr": "MG", "region": "Sudeste"},
    "32": {"name": "Espírito Santo", "abbr": "ES", "region": "Sudeste"},
    "33": {"name": "Rio de Janeiro", "abbr": "RJ", "region": "Sudeste"},
    "35": {"name": "São Paulo", "abbr": "SP", "region": "Sudeste"},
    "41": {"name": "Paraná", "abbr": "PR", "region": "Sul"},
    "42": {"name": "Santa Catarina", "abbr": "SC", "region": "Sul"},
    "43": {"name": "Rio Grande do Sul", "abbr": "RS", "region": "Sul"},
    "50": {"name": "Mato Grosso do Sul", "abbr": "MS", "region": "Centro-Oeste"},
    "51": {"name": "Mato Grosso", "abbr": "MT", "region": "Centro-Oeste"},
    "52": {"name": "Goiás", "abbr": "GO", "region": "Centro-Oeste"},
    "53": {"name": "Distrito Federal", "abbr": "DF", "region": "Centro-Oeste"},
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

# Geographic indicator configurations for state and municipal level pages
GEOGRAPHIC_INDICATORS = {
    "birth": IndicatorConfig(
        absolute="total_births",
        relative="births_per_1k",
        absolute_title="Nascimentos",
        relative_title="Nascimentos por 1.000 Habitantes",
        labels="Nascimentos",
        colors="primary",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "cesarean": IndicatorConfig(
        absolute="cesarean_count",
        relative="cesarean_pct",
        absolute_title="Número de Cesáreas",
        relative_title="Taxa de Cesárea (%)",
        labels="Cesáreas",
        colors="warning",
        recommended_relative_limit=15.0,
        recommended_name="Referência OMS (15%)",
    ),
    "preterm": IndicatorConfig(
        absolute="preterm_count",
        relative="preterm_pct",
        absolute_title="Número de Prematuros",
        relative_title="Taxa de Prematuridade (%)",
        labels="Prematuros",
        colors="warning",
        recommended_relative_limit=10.0,
        recommended_name="Referência OMS (10%)",
    ),
    "extreme_preterm": IndicatorConfig(
        absolute="extreme_preterm_count",
        relative="extreme_preterm_pct",
        absolute_title="Número de Prematuros Extremos",
        relative_title="Taxa de Prematuridade Extrema (%)",
        labels="Prematuros Extremos",
        colors="danger",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "adolescent_pregnancy": IndicatorConfig(
        absolute="adolescent_pregnancy_count",
        relative="adolescent_pregnancy_pct",
        absolute_title="Número de Gestações Adolescentes",
        relative_title="Taxa de Gravidez na Adolescência (%)",
        labels="Gestações Adolescentes",
        colors="info",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "low_birth_weight": IndicatorConfig(
        absolute="low_birth_weight_count",
        relative="low_birth_weight_pct",
        absolute_title="Número de Baixo Peso ao Nascer",
        relative_title="Taxa de Baixo Peso ao Nascer (%)",
        labels="Baixo Peso ao Nascer",
        colors="warning",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "low_apgar5": IndicatorConfig(
        absolute="low_apgar5_count",
        relative="low_apgar5_pct",
        absolute_title="Número de APGAR5 Baixo",
        relative_title="Taxa de APGAR5 Baixo (%)",
        labels="APGAR5 Baixo",
        colors="danger",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
    "hospital_birth": IndicatorConfig(
        absolute="hospital_birth_count",
        relative="hospital_birth_pct",
        absolute_title="Número de Nascimentos Hospitalares",
        relative_title="Taxa de Nascimentos Hospitalares (%)",
        labels="Nascimentos Hospitalares",
        colors="primary",
        recommended_relative_limit=None,
        recommended_name=None,
    ),
}
