"""Tactical alert rules."""

from __future__ import annotations

from typing import Dict, List, Optional


ALERT_VOLATILITY_EXTREME = 0.60
ALERT_VOLUME_MULTIPLIER = 1.5
ALERT_DROP_1D = -0.08
ALERT_DROP_1W = -0.15


def _pct_change(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if current is None or previous is None or previous == 0:
        return None
    return (current - previous) / previous


def generate_alerts(data: Dict[str, Optional[float]]) -> List[Dict[str, str]]:
    alerts: List[Dict[str, str]] = []

    short_float = data.get("short_float")
    if short_float is not None and short_float > 0.15:
        alerts.append(
            {
                "type": "Short float elevado",
                "detail": "Short float > 15% sugiere presión de cobertura potencial.",
            }
        )

    volatility_90d = data.get("volatility_90d")
    if volatility_90d is not None and volatility_90d >= ALERT_VOLATILITY_EXTREME:
        alerts.append(
            {
                "type": "Volatilidad extrema",
                "detail": "Volatilidad anualizada supera umbral extremo.",
            }
        )

    volume = data.get("volume")
    avg_volume_30d = data.get("avg_volume_30d")
    if volume is not None and avg_volume_30d:
        if volume > ALERT_VOLUME_MULTIPLIER * avg_volume_30d:
            alerts.append(
                {
                    "type": "Volumen anormal",
                    "detail": "Volumen actual > 150% de la media 30D.",
                }
            )

    return_1d = data.get("return_1d")
    return_1w = data.get("return_1w")
    if return_1d is not None and return_1d <= ALERT_DROP_1D:
        alerts.append(
            {
                "type": "Caída fuerte 1D",
                "detail": "Caída diaria relevante con presión de ventas.",
            }
        )
    if return_1w is not None and return_1w <= ALERT_DROP_1W:
        alerts.append(
            {
                "type": "Caída fuerte 1W",
                "detail": "Caída semanal relevante con presión de ventas.",
            }
        )

    conditions_met = 0
    if short_float is not None and short_float > 0.15:
        conditions_met += 1
    days_to_cover = data.get("days_to_cover")
    if days_to_cover is not None and days_to_cover > 5:
        conditions_met += 1
    free_float_percent = data.get("free_float_percent")
    if free_float_percent is not None and free_float_percent < 0.30:
        conditions_met += 1
    if volume is not None and avg_volume_30d and volume > ALERT_VOLUME_MULTIPLIER * avg_volume_30d:
        conditions_met += 1
    return_1m = data.get("return_1m")
    if return_1m is not None and return_1m > 0:
        conditions_met += 1

    if conditions_met >= 3:
        alerts.append(
            {
                "type": "Posible short squeeze",
                "detail": (
                    "Se cumplen ≥3 condiciones (short float, days to cover, free float reducido, "
                    "volumen elevado, momentum positivo). NO es recomendación; es advertencia de "
                    "volatilidad potencial."
                ),
            }
        )

    return alerts


def compute_short_term_returns(data: Dict[str, Optional[float]]) -> Dict[str, Optional[float]]:
    current = data.get("current_price")
    prev_1d = data.get("price_1d")
    prev_1w = data.get("price_1w")
    prev_1m = data.get("price_1m")
    return {
        "return_1d": _pct_change(current, prev_1d),
        "return_1w": _pct_change(current, prev_1w),
        "return_1m": _pct_change(current, prev_1m),
    }
