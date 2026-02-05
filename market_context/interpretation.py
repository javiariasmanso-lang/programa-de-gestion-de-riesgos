"""Interpretation rules and descriptive text for market context."""

from __future__ import annotations

from typing import Optional


SHORT_INTEREST_THRESHOLDS = [0.05, 0.10, 0.20]
INSTITUTIONAL_THRESHOLDS = [0.40, 0.70]
VOLATILITY_THRESHOLDS = [0.25, 0.45]
MOMENTUM_THRESHOLDS = [0.10, 0.25]


def interpret_short_interest(short_float: Optional[float]) -> str:
    if short_float is None:
        return "Short interest no disponible."
    if short_float < SHORT_INTEREST_THRESHOLDS[0]:
        return "Short interest bajo (<5%)."
    if short_float < SHORT_INTEREST_THRESHOLDS[1]:
        return "Short interest moderado (5–10%)."
    if short_float < SHORT_INTEREST_THRESHOLDS[2]:
        return "Short interest alto (≥10%)."
    return "Short interest muy alto (≥20%)."


def interpret_institutional(percent_institutional: Optional[float]) -> str:
    if percent_institutional is None:
        return "Participación institucional no disponible."
    if percent_institutional >= INSTITUTIONAL_THRESHOLDS[1]:
        return "Participación institucional alta (≥70%)."
    if percent_institutional >= INSTITUTIONAL_THRESHOLDS[0]:
        return "Participación institucional media (40–70%)."
    return "Participación institucional baja (<40%)."


def interpret_volatility(volatility_90d: Optional[float]) -> str:
    if volatility_90d is None:
        return "Volatilidad no disponible."
    if volatility_90d < VOLATILITY_THRESHOLDS[0]:
        return "Volatilidad baja (≤25% anualizada)."
    if volatility_90d < VOLATILITY_THRESHOLDS[1]:
        return "Volatilidad moderada (25–45% anualizada)."
    return "Volatilidad alta (≥45% anualizada)."


def interpret_momentum(return_6m: Optional[float]) -> str:
    if return_6m is None:
        return "Momentum no disponible."
    if return_6m >= MOMENTUM_THRESHOLDS[1]:
        return "Momentum fuerte positivo (≥25% en 6M)."
    if return_6m >= MOMENTUM_THRESHOLDS[0]:
        return "Momentum positivo moderado (10–25% en 6M)."
    if return_6m <= -MOMENTUM_THRESHOLDS[1]:
        return "Momentum fuerte negativo (≤-25% en 6M)."
    if return_6m <= -MOMENTUM_THRESHOLDS[0]:
        return "Momentum negativo moderado (≤-10% en 6M)."
    return "Momentum neutro (±10% en 6M)."
