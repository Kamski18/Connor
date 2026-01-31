FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock /app/

RUN pip install --no-cache-dir uv
RUN uv sync --frozen

COPY . /app

CMD ["uv", "run", "main.py"]
