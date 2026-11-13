FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY qinglong ./qinglong

RUN pip install --no-cache-dir .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "from qinglong import api; api.health_check()" || exit 1

CMD ["qinglong-mcp", "--transport", "http", "--port", "8000"]
