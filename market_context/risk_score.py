"""Compute market risk score based on subcomponents."""

from __future__ import annotations

from typing import Dict, Optional


SCORE_LABELS = {
    "low": "bajo",
    "medium": "medio",
    "high": "alto",
}


def _score_short_interest(short_float: Optional[float]) -> int:
    if short_float is None:
        return 1
    if short_float < 0.05:
        return 0
    if short_float < 0.10:
        return 1
    if short_float < 0.20:
        return 2
    return 3


def _score_volatility(volatility_90d: Optional[float]) -> int:
    if volatility_90d is None:
        return 1
    if volatility_90d < 0.25:
        return 0
    if volatility_90d < 0.45:
        return 2
    return 3


def _score_liquidity(avg_volume: Optional[float], free_float_percent: Optional[float]) -> int:
    if avg_volume is None or free_float_percent is None:
        return 1
    if avg_volume > 1_000_000 and free_float_percent > 0.50:
        return 0
    if avg_volume > 500_000 and free_float_percent > 0.30:
        return 1
    return 2


def _score_institutional(percent_institutional: Optional[float]) -> int:
    if percent_institutional is None:
        return 1
    if percent_institutional >= 0.70:
        return 2
    if percent_institutional >= 0.40:
        return 1
    return 0


def _score_momentum(return_6m: Optional[float]) -> int:
    if return_6m is None:
        return 1
    if return_6m >= 0.25 or return_6m <= -0.25:
        return 2
    if return_6m >= 0.10 or return_6m <= -0.10:
        return 1
    return 0


def compute_market_risk_score(data: Dict[str, Optional[float]]) -> Dict[str, object]:
    scores = {
        "short_interest": _score_short_interest(data.get("short_float")),
        "volatility": _score_volatility(data.get("volatility_90d")),
        "liquidity": _score_liquidity(
            data.get("avg_volume"), data.get("free_float_percent")
        ),
        "institutional": _score_institutional(data.get("percent_institutional")),
        "momentum": _score_momentum(data.get("return_6m")),
    }
    total = sum(scores.values())
    if total <= 3:
        label = SCORE_LABELS["low"]
    elif total <= 6:
        label = SCORE_LABELS["medium"]
    else:
        label = SCORE_LABELS["high"]
    return {"total": total, "label": label, "components": scores}
