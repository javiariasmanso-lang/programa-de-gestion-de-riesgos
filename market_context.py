"""CLI entrypoint for market context analysis."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional

from market_context import alerts, data_sources, export, interpretation, report, risk_score

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def _collect_missing(data: Dict[str, Optional[float]]) -> List[str]:
    missing = []
    for key, value in data.items():
        if value is None:
            missing.append(key)
    return missing


def build_payload(
    ticker: str,
    data: Dict[str, Optional[float]],
    interpretations: Dict[str, str],
    score: Dict[str, object],
    alerts_list: List[Dict[str, str]],
    missing: List[str],
    errors: List[str],
) -> Dict[str, object]:
    return {
        "ticker": ticker,
        "data": data,
        "interpretations": interpretations,
        "risk_score": score,
        "alerts": alerts_list,
        "missing_metrics": missing,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analizador de contexto de mercado (sin recomendaciones)."
    )
    parser.add_argument("ticker", help="Ticker a analizar (ej. AAPL)")
    parser.add_argument(
        "--output",
        choices=["json", "csv"],
        help="Exportar resultados en JSON o CSV",
    )
    parser.add_argument(
        "--output-file",
        help="Ruta de salida para exportación (opcional)",
    )
    args = parser.parse_args()

    ticker = args.ticker.upper()
    data, errors = data_sources.collect_all(ticker)
    data.update(alerts.compute_short_term_returns(data))

    interpretations = {
        "short_interest": interpretation.interpret_short_interest(data.get("short_float")),
        "institutional": interpretation.interpret_institutional(
            data.get("percent_institutional")
        ),
        "volatility": interpretation.interpret_volatility(data.get("volatility_90d")),
        "momentum": interpretation.interpret_momentum(data.get("return_6m")),
    }

    score = risk_score.compute_market_risk_score(data)
    alerts_list = alerts.generate_alerts(data)
    missing = _collect_missing(data)

    print(
        report.build_report(
            ticker=ticker,
            data=data,
            interpretations=interpretations,
            score=score,
            alerts=alerts_list,
            missing=missing,
        )
    )

    if args.output:
        output_format = args.output
        if args.output_file:
            output_path = Path(args.output_file)
        else:
            output_path = Path(f"market_context_{ticker.lower()}.{output_format}")
        payload = build_payload(
            ticker,
            data,
            interpretations,
            score,
            alerts_list,
            missing,
            errors,
        )
        export.export_payload(payload, output_format, output_path)
        logging.info("Exportado a %s", output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
