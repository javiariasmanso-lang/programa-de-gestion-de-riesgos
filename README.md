# Contexto de mercado (CLI)

Herramienta de consola para generar un informe **descriptivo** de contexto de riesgo de mercado. **No emite recomendaciones de inversión.**

## Requisitos

- Python 3.10+
- Librería `yfinance` (fuente **no oficial** que puede fallar o cambiar).

```bash
pip install yfinance
```

## Variables de entorno (opcional)

Si deseas ampliar fuentes externas, define claves de API en variables de entorno. Si no se configuran, los campos que dependan de esas fuentes quedarán como `None` y se informará en el reporte.

- `ALPHAVANTAGE_API_KEY`
- `FMP_API_KEY`
- `POLYGON_API_KEY`

> Nota: en esta implementación base se utiliza `yfinance` como fuente principal. Métricas como beta o participación institucional pueden no estar disponibles y se reportarán como faltantes.

## Uso

```bash
python market_context.py AAPL
```

Exportación:

```bash
python market_context.py AAPL --output json
python market_context.py AAPL --output csv --output-file /ruta/salida.csv
```

El informe resultante es únicamente descriptivo y explica riesgos/contexto. **No constituye recomendación.**

## App web (Streamlit)

Ejecuta la interfaz web:

```bash
streamlit run app.py
```

La app reutiliza las funciones internas del paquete `market_context` (sin subprocess), muestra métricas, score, alertas e interpretaciones, y mantiene el mismo enfoque descriptivo sin recomendaciones.
