<div align="center">

# Prompt Survivors

**Whisper to AI agents. Shape reality.**

An LLM-powered social manipulation game where you're a hidden puppet master in a room of AI personalities.

</div>

## What Is This?

You enter a room full of AI agents — each with a unique personality, opinions, and goals. Your mission: **whisper** to any agent to secretly influence the conversation and achieve your **secret objective** before the rounds run out.

Every agent response is a real LLM call — no scripts, no canned answers. Every game plays out differently.

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Frontend** | Vue 3, Vue Router, Vite, Axios |
| **Backend** | Python 3.11+, Flask, Flask-CORS |
| **LLM** | OpenAI SDK (any OpenAI-compatible API) |
| **Auth** | OpenRouter OAuth (BYOK fallback) |
| **Infra** | Docker, GitHub Actions (GHCR) |

## Quick Start

### Prerequisites

- **Node.js** 18+ — `node -v`
- **Python** 3.11+ — `python --version`
- **uv** (Python package manager) — `uv --version`

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env` with your LLM provider credentials:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
```

### 2. Install & Run

```bash
npm run setup:all
npm run dev
```

Open **http://localhost:3000** and click **PLAY NOW**.

### Docker

```bash
cp .env.example .env
docker compose up -d
```

## How It Works

1. **Choose a scenario** — pick a mission with unique agents and a secret objective
2. **Observe** — watch agents debate in Round 1 using their distinct personalities
3. **Whisper** — each round, secretly message one agent to steer their thinking
4. **Watch emergence** — agents respond with real LLM intelligence, shaped by your whisper and group dynamics
5. **Get judged** — an AI evaluator scores how well you achieved your objective

## Project Structure

```
backend/
  app/
    api/game.py              # Game API endpoints
    api/auth.py              # OpenRouter OAuth callback
    services/game_engine.py  # Game logic, scenarios, LLM agent orchestration
    utils/llm_client.py      # OpenAI SDK wrapper
    config.py                # LLM + BYOK configuration

frontend/
  src/
    views/Home.vue           # Landing page
    views/GameView.vue       # Main game UI + BYOK modal
    views/CreateView.vue     # Custom scenario creator
    views/AuthCallback.vue   # OpenRouter OAuth callback handler
    composables/useAuth.js   # BYOK auth state (localStorage, no DB)
    api/game.js              # Game API client
    api/index.js             # Axios instance + interceptors
    router/index.js          # Routes
```

## License

AGPL-3.0
