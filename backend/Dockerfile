FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend

EXPOSE 8000

# UPGRADED for Render: Render assigns a random port at runtime via the
# $PORT env var and health-checks that exact port - a hardcoded
# "--port 8000" here would mean the container never actually listens
# where Render expects, and the deploy fails its health check even
# though the app "runs" fine. Falls back to 8000 for local `docker run`
# where $PORT isn't set. Needs the shell form (no brackets) so $PORT
# actually gets expanded - the exec form ["uvicorn", ...] does NOT
# expand environment variables.
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
