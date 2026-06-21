FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY requirements.txt /app/

RUN uv pip install --system --no-cache -r requirements.txt

COPY . /app/

CMD ["python", "main.py"]