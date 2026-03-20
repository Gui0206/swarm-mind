🇧🇷 [Leia em Português](README-PT.md)

<div align="center">

# Swarm Mind

**Whisper to AI agents. Shape reality.**

An LLM-powered browser game where you try to persuade a swarm of stubborn AI agents to agree with absurd or highly debated ideas.

[Play Now](https://swarm-mind-three.vercel.app/)

</div>

## What Is This?

You enter a room full of AI agents — each with a unique personality, opinions, and goals. Your mission: **whisper** to any agent to secretly influence the conversation and achieve your **secret objective** before the rounds run out.

Every agent response is a real LLM call — no scripts, no canned answers. Every game plays out differently.

## How It Works

1. **Choose a scenario** — pick a mission with unique agents and a secret objective
2. **Observe** — watch agents debate in Round 1 using their distinct personalities
3. **Whisper** — each round, secretly message one agent to steer their thinking
4. **Watch emergence** — agents respond with real LLM intelligence, shaped by your whisper and group dynamics
5. **Get judged** — an AI evaluator scores how well you achieved your objective

## How I Built It

I was messing around with an open-source repo called [MiroFish](https://github.com/MiroFish/MiroFish) and thought it could become a game. So I prompted Claude with:

> *"Create a really really fun and viral browser game. Use your creativity to create something innovative and brand new. The game has to include swarm agents as a key mechanic. You can change the frontend, the backend, feel free to experiment (just don't break anything)."*

And then vibe-coded the whole thing from there.

## Contributing

The prompt engineering for the swarm agents is still rough — sometimes they agree too easily or become caricatures of their system prompts. If you're good at prompt engineering or want to tweak the debate loop, PRs are incredibly welcome.

## Stateless Custom Levels

The game has a custom scenario builder. Instead of a database, the entire configuration (agent personalities, goals, rules) is compressed and passed directly into the URL. You can build a scenario, copy the massive URL, and send it to a friend.

## Tech Stack

| Layer | Stack |
|-------|-------|
| **Frontend** | Vue 3, Vite, Vercel |
| **Backend** | Python, Flask, Railway |
| **LLM** | Google Gemini 3 Flash via OpenRouter |
| **Auth** | OpenRouter OAuth (BYOK) |

## Quick Start

### Prerequisites

- **Node.js** 18+
- **Python** 3.11+
- **uv** (Python package manager)

### 1. Configure

```bash
cp .env.example .env
```

Edit `.env` with your LLM provider credentials:

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL_NAME=google/gemini-3-flash-preview
```

### 2. Install & Run

```bash
npm run setup:all
npm run dev
```

Open **http://localhost:3000** and click **PLAY NOW**.

## License

AGPL-3.0
