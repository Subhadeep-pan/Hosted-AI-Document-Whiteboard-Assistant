import axios from "axios";

const SESSION_ID_KEY = "session_id";

// Every browser tab/user gets its own random session id, saved in
// localStorage so it survives page refreshes. The backend uses this to
// keep each user's chat history and cache separate.
function getSessionId() {
  let sessionId = localStorage.getItem(SESSION_ID_KEY);

  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_ID_KEY, sessionId);
  }

  return sessionId;
}

const api = axios.create({
  // UPGRADED: back to reading from an env var, not hardcoded - now that
  // this deploys to two different real environments (local dev vs. your
  // live Render backend), a hardcoded URL would mean editing this file
  // and pushing a new commit every time the backend URL changes. This
  // does NOT require a committed .env file: Vercel lets you set
  // VITE_API_URL directly in its dashboard (Project Settings >
  // Environment Variables) - nothing with real values needs to be
  // checked into the repo. Falls back to localhost so local dev still
  // works with zero setup if you don't create a frontend/.env at all.
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
  config.headers["X-Session-Id"] = getSessionId();

  // Only sent if you set VITE_API_KEY in the frontend .env file, to
  // match an API_KEY set on the backend.
  if (import.meta.env.VITE_API_KEY) {
    config.headers["X-Api-Key"] = import.meta.env.VITE_API_KEY;
  }

  return config;
});

export default api;
