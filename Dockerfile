FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 ZERO_BURN_HOST=0.0.0.0 ZERO_BURN_PORT=8787
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY web ./web
RUN pip install --no-cache-dir .
EXPOSE 8787
CMD ["python","-m","zeroburn"]
