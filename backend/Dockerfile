# One-command local/staging deploy: `docker compose up --build`
# Needs backend/.env to exist first (copy from backend/.env.example).
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis-data:/data

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile
    restart: unless-stopped
    ports:
      # Host 8000 -> container 10000, matching the Dockerfile's new
      # default fallback port (used when Docker Compose doesn't set a
      # PORT env var, unlike Render which always sets one itself).
      - "8000:10000"
    env_file:
      - backend/.env
    environment:
      # Overrides backend/.env's REDIS_HOST so the backend reaches the
      # "redis" container by its service name, not localhost.
      REDIS_HOST: redis
    depends_on:
      - redis
    volumes:
      - chroma-data:/app/backend/app/vectorstore/chroma_db
      - uploads-data:/app/backend/uploads

  frontend:
    build:
      context: .
      dockerfile: frontend/Dockerfile
      args:
        VITE_API_URL: http://localhost:8000
    restart: unless-stopped
    ports:
      - "5173:80"
    depends_on:
      - backend

volumes:
  redis-data:
  chroma-data:
  uploads-data: