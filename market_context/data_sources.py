"""Data collection from public market APIs."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class DataResult:
    data: Dict[str, Any]
    errors: List[str]


def _safe_call(label: str, func, fallback: Dict[str, Any]) -> DataResult:
    try:
        return DataResult(func(), [])
    except Exception as exc:  # pragma: no cover - defensive
        message = f"{label} failed: {exc}"
        logger.warning(message)
        return DataResult(fallback, [message])


def _get_ticker(ticker: str):
    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover - environment
        raise RuntimeError(
            "yfinance is not installed; install it or use another API provider."
        ) from exc
    return yf.Ticker(ticker)


def get_price_volume(ticker: str) -> DataResult:
    def _fetch():
        yf_ticker = _get_ticker(ticker)
        history = yf_ticker.history(period="90d")
        if history.empty:
            return {
                "current_price": None,
                "volume": None,
                "avg_volume_30d": None,
                "avg_volume_90d": None,
                "price_1d": None,
                "price_1w": None,
                "price_1m": None,
            }
        current_price = float(history["Close"].iloc[-1])
        volume = float(history["Volume"].iloc[-1])
        avg_volume_30d = float(history["Volume"].tail(30).mean())
        avg_volume_90d = float(history["Volume"].mean())
        price_1d = float(history["Close"].iloc[-2]) if len(history) > 1 else None
        price_1w = float(history["Close"].iloc[-6]) if len(history) > 5 else None
        price_1m = float(history["Close"].iloc[-21]) if len(history) > 20 else None
        return {
            "current_price": current_price,
            "volume": volume,
            "avg_volume_30d": avg_volume_30d,
            "avg_volume_90d": avg_volume_90d,
            "price_1d": price_1d,
            "price_1w": price_1w,
            "price_1m": price_1m,
        }

    return _safe_call(
        "get_price_volume",
        _fetch,
        {
            "current_price": None,
            "volume": None,
            "avg_volume_30d": None,
            "avg_volume_90d": None,
            "price_1d": None,
            "price_1w": None,
            "price_1m": None,
        },
    )


def get_volatility_beta(ticker: str) -> DataResult:
    def _fetch():
        yf_ticker = _get_ticker(ticker)
        history = yf_ticker.history(period="90d")
        returns = history["Close"].pct_change().dropna()
        if returns.empty:
            volatility_30d = None
            volatility_90d = None
        else:
            volatility_30d = float(returns.tail(30).std() * (252**0.5))
            volatility_90d = float(returns.std() * (252**0.5))
        info = yf_ticker.info or {}
        beta = info.get("beta")
        return {
            "volatility_30d": volatility_30d,
            "volatility_90d": volatility_90d,
            "beta": beta,
        }

    return _safe_call(
        "get_volatility_beta",
        _fetch,
        {"volatility_30d": None, "volatility_90d": None, "beta": None},
    )


def get_institutional_ownership(ticker: str) -> DataResult:
    def _fetch():
        yf_ticker = _get_ticker(ticker)
        info = yf_ticker.info or {}
        percent_institutional = info.get("heldPercentInstitutions")
        recent_change = None
        try:
            holders = yf_ticker.institutional_holders
        except Exception:
            holders = None
        if holders is not None and not holders.empty and len(holders) > 1:
            try:
                recent_change = float(holders["Shares"].iloc[0] - holders["Shares"].iloc[1])
            except Exception:
                recent_change = None
        return {
            "percent_institutional": percent_institutional,
            "recent_change": recent_change,
        }

    return _safe_call(
        "get_institutional_ownership",
        _fetch,
        {"percent_institutional": None, "recent_change": None},
    )


def get_short_interest(ticker: str) -> DataResult:
    def _fetch():
        yf_ticker = _get_ticker(ticker)
        info = yf_ticker.info or {}
        return {
            "short_float": info.get("shortPercentOfFloat"),
            "days_to_cover": info.get("shortRatio"),
        }

    return _safe_call(
        "get_short_interest",
        _fetch,
        {"short_float": None, "days_to_cover": None},
    )


def get_float_liquidity(ticker: str) -> DataResult:
    def _fetch():
        yf_ticker = _get_ticker(ticker)
        info = yf_ticker.info or {}
        float_shares = info.get("floatShares")
        shares_outstanding = info.get("sharesOutstanding")
        free_float_percent = None
        if float_shares and shares_outstanding:
            free_float_percent = float_shares / shares_outstanding
        return {
            "free_float_percent": free_float_percent,
            "float_shares": float_shares,
            "shares_outstanding": shares_outstanding,
            "avg_volume": info.get("averageVolume"),
        }

    return _safe_call(
        "get_float_liquidity",
        _fetch,
        {
            "free_float_percent": None,
            "float_shares": None,
            "shares_outstanding": None,
            "avg_volume": None,
        },
    )


def get_momentum(ticker: str) -> DataResult:
    def _fetch():
        yf_ticker = _get_ticker(ticker)
        history = yf_ticker.history(period="1y")
        if history.empty:
            return {
                "return_3m": None,
                "return_6m": None,
                "return_12m": None,
            }
        close = history["Close"]
        current = float(close.iloc[-1])

        def _calc_return(days: int) -> Optional[float]:
            if len(close) <= days:
                return None
            past = float(close.iloc[-days])
            if past == 0:
                return None
            return (current - past) / past
        return {
            "return_3m": _calc_return(63),
            "return_6m": _calc_return(126),
            "return_12m": _calc_return(252),
        }

    return _safe_call(
        "get_momentum",
        _fetch,
        {"return_3m": None, "return_6m": None, "return_12m": None},
    )


def collect_all(ticker: str) -> tuple[Dict[str, Any], List[str]]:
    results = [
        get_price_volume(ticker),
        get_volatility_beta(ticker),
        get_institutional_ownership(ticker),
        get_short_interest(ticker),
        get_float_liquidity(ticker),
        get_momentum(ticker),
    ]
    data: Dict[str, Any] = {}
    errors: List[str] = []
    for result in results:
        data.update(result.data)
        errors.extend(result.errors)
    return data, errors
