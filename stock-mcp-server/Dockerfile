FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server_v45.py .
COPY chrome_mcp_optimized.py .
COPY chrome_mcp_analyzer.py .
COPY capital_flow.py .
COPY sector_analysis.py .
COPY backtest.py .
COPY alert_system.py .

EXPOSE 8000

CMD ["python", "server_v45.py"]
