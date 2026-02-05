"""Streamlit app for descriptive market context analysis."""

from __future__ import annotations

from typing import Dict, List, Optional

import streamlit as st

from market_context import alerts, data_sources, interpretation, risk_score


LEVEL_COLORS = {
    "bajo": "#2e7d32",
    "medio": "#ef6c00",
    "alto": "#c62828",
}


def _format_currency(value: Optional[float]) -> str:
    if value is None:
        return "N/D"
    return f"${value:,.2f}"


def _format_number(value: Optional[float]) -> str:
    if value is None:
        return "N/D"
    return f"{value:,.2f}"


def _format_percent(value: Optional[float]) -> str:
    if value is None:
        return "N/D"
    return f"{value * 100:.2f}%"


def _collect_missing(data: Dict[str, Optional[float]]) -> List[str]:
    return [key for key, value in data.items() if value is None]


def _render_score_badge(score: Dict[str, object]) -> None:
    label = str(score["label"])
    color = LEVEL_COLORS.get(label, "#455a64")
    st.markdown(
        (
            "<div style='padding:14px;border-radius:10px;color:white;"
            f"background:{color};font-weight:600;font-size:20px;'>"
            f"Score de riesgo: {score['total']}/10 · Nivel: {label.upper()}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def _render_interpretations(interpretations: Dict[str, str]) -> None:
    st.subheader("Interpretaciones")
    for key, value in interpretations.items():
        title = key.replace("_", " ").capitalize()
        st.markdown(f"**{title}:** {value}")


def _render_alerts(alerts_list: List[Dict[str, str]]) -> None:
    st.subheader("Alertas activas")
    if not alerts_list:
        st.info("No se detectaron alertas tácticas relevantes.")
        return
    for alert in alerts_list:
        st.warning(f"**{alert['type']}** — {alert['detail']}")


def _render_missing(missing: List[str], errors: List[str]) -> None:
    if missing:
        st.subheader("Métricas no disponibles")
        st.caption("Las siguientes métricas no pudieron recuperarse:")
        st.write(", ".join(missing))

    if errors:
        st.subheader("Errores de fuente de datos")
        for err in errors:
            st.error(err)


def main() -> None:
    st.set_page_config(page_title="Contexto de Mercado", page_icon="📊", layout="wide")

    st.title("Contexto de Mercado")
    st.caption(
        "Aplicación descriptiva de riesgo y contexto de mercado. "
        "No constituye recomendación de inversión."
    )

    ticker = st.text_input("Ticker", placeholder="Ejemplo: AAPL").strip().upper()

    if st.button("Analizar mercado", type="primary"):
        if not ticker:
            st.error("Introduce un ticker válido para analizar.")
            return

        with st.spinner(f"Analizando {ticker}..."):
            try:
                data, errors = data_sources.collect_all(ticker)
                data.update(alerts.compute_short_term_returns(data))

                interpretations = {
                    "short_interest": interpretation.interpret_short_interest(
                        data.get("short_float")
                    ),
                    "institutional": interpretation.interpret_institutional(
                        data.get("percent_institutional")
                    ),
                    "volatility": interpretation.interpret_volatility(
                        data.get("volatility_90d")
                    ),
                    "momentum": interpretation.interpret_momentum(data.get("return_6m")),
                }

                score = risk_score.compute_market_risk_score(data)
                active_alerts = alerts.generate_alerts(data)
                missing = _collect_missing(data)
            except Exception as exc:  # pragma: no cover - UI guard
                st.exception(exc)
                st.error(
                    "No fue posible completar el análisis por un error inesperado. "
                    "No se emiten recomendaciones de inversión."
                )
                return

        st.subheader("Resumen de mercado")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Precio actual", _format_currency(data.get("current_price")))
        col2.metric("Volumen diario", _format_number(data.get("volume")))
        col3.metric("Volumen medio 30D", _format_number(data.get("avg_volume_30d")))
        col4.metric("Volatilidad 90D", _format_percent(data.get("volatility_90d")))

        col5, col6, col7, col8 = st.columns(4)
        col5.metric("Short float", _format_percent(data.get("short_float")))
        col6.metric("Days to cover", _format_number(data.get("days_to_cover")))
        col7.metric("Institucional", _format_percent(data.get("percent_institutional")))
        col8.metric("Rentabilidad 6M", _format_percent(data.get("return_6m")))

        st.subheader("Score de riesgo")
        _render_score_badge(score)

        _render_alerts(active_alerts)
        _render_interpretations(interpretations)
        _render_missing(missing, errors)

        st.divider()
        st.caption(
            "Este análisis es exclusivamente descriptivo y orientado a contexto/riesgo. "
            "NO es una recomendación de inversión."
        )


if __name__ == "__main__":
    main()
