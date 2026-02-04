"""Console report builder."""

from __future__ import annotations

from typing import Dict, List, Optional


def _format_percent(value: Optional[float]) -> str:
    if value is None:
        return "N/D"
    return f"{value * 100:.2f}%"


def _format_number(value: Optional[float]) -> str:
    if value is None:
        return "N/D"
    return f"{value:,.2f}"


def build_report(
    ticker: str,
    data: Dict[str, Optional[float]],
    interpretations: Dict[str, str],
    score: Dict[str, object],
    alerts: List[Dict[str, str]],
    missing: List[str],
) -> str:
    lines = []
    lines.append(f"Informe de contexto de mercado: {ticker}")
    lines.append("=" * 60)
    lines.append("Resumen de mercado")
    lines.append(f"Precio actual: {_format_number(data.get('current_price'))}")
    lines.append(f"Volumen diario: {_format_number(data.get('volume'))}")
    lines.append(
        f"Volumen medio 30D: {_format_number(data.get('avg_volume_30d'))}"
    )
    lines.append(
        f"Volumen medio 90D: {_format_number(data.get('avg_volume_90d'))}"
    )
    lines.append(
        f"Volatilidad 90D: {_format_percent(data.get('volatility_90d'))}"
    )
    lines.append(f"Beta: {_format_number(data.get('beta'))}")
    lines.append(
        f"Institucionales: {_format_percent(data.get('percent_institutional'))}"
    )
    lines.append(f"Short float: {_format_percent(data.get('short_float'))}")
    lines.append(f"Days to cover: {_format_number(data.get('days_to_cover'))}")
    lines.append(
        f"Free float: {_format_percent(data.get('free_float_percent'))}"
    )
    lines.append(
        f"Rentabilidad 3M: {_format_percent(data.get('return_3m'))}"
    )
    lines.append(
        f"Rentabilidad 6M: {_format_percent(data.get('return_6m'))}"
    )
    lines.append(
        f"Rentabilidad 12M: {_format_percent(data.get('return_12m'))}"
    )

    lines.append("")
    lines.append("Riesgos detectados")
    lines.append(f"- {interpretations['short_interest']}")
    lines.append(f"- {interpretations['institutional']}")
    lines.append(f"- {interpretations['volatility']}")
    lines.append(f"- {interpretations['momentum']}")

    lines.append("")
    lines.append("Alertas activas")
    if alerts:
        for alert in alerts:
            lines.append(f"- {alert['type']}: {alert['detail']}")
    else:
        lines.append("- No se detectaron alertas tácticas relevantes.")

    lines.append("")
    lines.append("Score de riesgo")
    lines.append(f"Puntaje total (0-10): {score['total']} | Nivel: {score['label']}")

    lines.append("")
    lines.append("Conclusión de contexto")
    lines.append(
        "Este informe es descriptivo y orientado a contexto de riesgo. "
        "No constituye recomendación de inversión."
    )

    if missing:
        lines.append("")
        lines.append("Métricas no disponibles")
        for item in missing:
            lines.append(f"- {item}")

    return "\n".join(lines)
