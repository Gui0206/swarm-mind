/**
 * BYOK Auth — OpenRouter OAuth flow + localStorage key management
 *
 * Stateless: everything lives in the browser (localStorage / sessionStorage).
 */
import { ref, computed } from 'vue'

const STORAGE_KEY = 'openrouter_user_key'
const GAMES_KEY = 'free_games_played'
const FREE_GAME_LIMIT = 5
const IS_DEV = import.meta.env.DEV

// Shared reactive state (module-level so all consumers share it)
const userKey = ref(localStorage.getItem(STORAGE_KEY) || '')
const gamesPlayed = ref(parseInt(localStorage.getItem(GAMES_KEY), 10) || 0)
const showByokModal = ref(false)

export function useAuth() {
  // In dev mode, act as if always authenticated (bypass limit & auth)
  const isAuthenticated = computed(() => IS_DEV || !!userKey.value)
  const freeGamesRemaining = computed(() => IS_DEV ? Infinity : Math.max(0, FREE_GAME_LIMIT - gamesPlayed.value))
  const freeQuotaExceeded = computed(() => IS_DEV ? false : (gamesPlayed.value >= FREE_GAME_LIMIT && !userKey.value))

  /**
   * Gate check — call before starting a game.
   * Returns true if the game is allowed, false if the BYOK modal was shown.
   */
  function canStartGame() {
    if (isAuthenticated.value) return true
    if (gamesPlayed.value >= FREE_GAME_LIMIT) {
      triggerByokModal()
      return false
    }
    return true
  }

  /** Record that a free game was started (only counts non-BYOK games). */
  function recordGamePlayed() {
    if (isAuthenticated.value) return
    gamesPlayed.value++
    localStorage.setItem(GAMES_KEY, String(gamesPlayed.value))
  }

  /** Kick off the OpenRouter OAuth redirect. */
  function login() {
    const callbackUrl = `${window.location.origin}/auth/callback`
    sessionStorage.setItem('auth_return_url', window.location.pathname + window.location.hash)
    window.location.href = `https://openrouter.ai/auth?callback_url=${encodeURIComponent(callbackUrl)}`
  }

  /** Store the key returned by the code exchange. */
  function setKey(key) {
    userKey.value = key
    localStorage.setItem(STORAGE_KEY, key)
  }

  /** Clear the stored key. */
  function logout() {
    userKey.value = ''
    localStorage.removeItem(STORAGE_KEY)
  }

  /** Call from the response interceptor when 402 is received. */
  function triggerByokModal() {
    if (IS_DEV) return
    showByokModal.value = true
  }

  function dismissByokModal() {
    showByokModal.value = false
  }

  return {
    userKey,
    isAuthenticated,
    showByokModal,
    gamesPlayed,
    freeGamesRemaining,
    freeQuotaExceeded,
    canStartGame,
    recordGamePlayed,
    login,
    logout,
    setKey,
    triggerByokModal,
    dismissByokModal,
  }
}
