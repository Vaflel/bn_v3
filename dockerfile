FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libfontconfig1

WORKDIR /app

RUN pip install uv
COPY uv.lock .
COPY pyproject.toml .
RUN uv sync

RUN mkdir data
RUN mkdir data/ind_sched

VOLUME ["/app/data"]

COPY . .

RUN uv run alembic upgrade head

CMD ["uv", "run", "main.py"]

