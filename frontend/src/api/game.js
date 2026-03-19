/**
 * SWARM MIND — Game API Client
 */
import service from './index.js'

export function getScenarios() {
  return service.get('/api/game/scenarios')
}

export function newGame(scenarioId) {
  return service.post('/api/game/new', { scenario_id: scenarioId || null })
}

export function newCustomGame(scenario) {
  return service.post('/api/game/new-custom', scenario)
}

export function getGame(gameId) {
  return service.get(`/api/game/${gameId}`)
}

export function whisper(gameId, agentId, message) {
  return service.post(`/api/game/${gameId}/whisper`, {
    agent_id: agentId,
    message: message,
  })
}

export function tick(gameId) {
  return service.post(`/api/game/${gameId}/tick`)
}

/** Exchange an OpenRouter auth code for an API key (via backend proxy). */
export function exchangeAuthCode(code) {
  return service.post('/api/auth/exchange', { code })
}

/** Check if the server LLM key is still active. */
export function getServerStatus() {
  return service.get('/api/auth/status')
}
