<div align="center">

# SWARM MIND

**Whisper to AI agents. Shape reality.**

An LLM-powered social manipulation game built on the [MiroFish](https://github.com/666ghj/MiroFish) multi-agent infrastructure.

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/MiroFish?style=flat-square&color=DAA520)](https://github.com/666ghj/MiroFish/stargazers)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)

</div>

## What Is This?

You're a hidden puppet master in a room of AI agents. Each agent has a unique personality, opinions, and goals. **Whisper** to any agent to secretly influence the conversation and achieve your **secret objective** before the rounds run out.

Every agent response is a real LLM call — no scripts, no canned answers. Every game plays out differently.

## Scenarios

| Scenario | Objective |
|---|---|
| **The Pineapple Ultimatum** | Get the office to agree on pineapple pizza |
| **Operation: Long Weekend** | Convince coworkers to call in sick Monday |
| **Operation: Flat Earth** | Make scientists doubt Earth's shape |
| **The Cat Agenda** | Convert everyone to Team Cat |
| **Karaoke Coup** | Get the team hyped for karaoke night |
| **First Contact Protocol** | Convince a government panel aliens are real |

6 scenarios, 36 unique agents, infinite replayability.

## How It Works

1. **Choose a scenario** — pick a mission with unique agents and a secret objective
2. **Observe** — watch agents debate in Round 1 using their distinct personalities
3. **Whisper** — each round, secretly message one agent to steer their thinking
4. **Watch emergence** — agents respond through real LLM intelligence, influenced by your whisper and group dynamics
5. **Get judged** — an AI judge scores how well you achieved your objective

## Quick Start

### Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| **Node.js** | 18+ | `node -v` |
| **Python** | ≥3.11 | `python --version` |
| **uv** | Latest | `uv --version` |

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env` with your LLM API key (any OpenAI-compatible endpoint):

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o-mini
```

### 2. Install

```bash
npm run setup:all
```

### 3. Run

```bash
npm run dev
```

Open `http://localhost:3000` — click **PLAY NOW**.

### Docker

```bash
cp .env.example .env
docker compose up -d
```

## Tech Stack

- **Frontend**: Vue 3 + Vite + Axios
- **Backend**: Flask + OpenAI SDK
- **LLM**: Any OpenAI-compatible API (GPT, Claude, Qwen, Gemini, etc.)
- **Infrastructure**: Built on [MiroFish](https://github.com/666ghj/MiroFish) multi-agent engine

## Project Structure

```
backend/
  app/
    api/game.py            # Game API endpoints
    services/game_engine.py # Game logic, scenarios, LLM agent orchestration
    utils/llm_client.py    # OpenAI SDK wrapper
    config.py              # LLM configuration

frontend/
  src/
    views/GameView.vue     # Full game UI
    views/Home.vue         # Landing page
    api/game.js            # Game API client
    router/index.js        # Routes
```

## License

AGPL-3.0

## Acknowledgments

Built on **[MiroFish](https://github.com/666ghj/MiroFish)** swarm intelligence infrastructure, supported by Shanda Group. Simulation engine powered by **[OASIS](https://github.com/camel-ai/oasis)** from the CAMEL-AI team.
