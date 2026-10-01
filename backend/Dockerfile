FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y nodejs npm && \
    rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt ./backend/app/requirements.txt
RUN pip install --no-cache-dir -r ./backend/app/requirements.txt
COPY app ./backend/app
COPY component_compiler ./backend/component_compiler
EXPOSE 8000

CMD ["sh", "-c", "python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]