<template>
  <div class="callback-root">
    <div class="callback-card">
      <template v-if="error">
        <div class="cb-icon">!</div>
        <div class="cb-title">Authentication Failed</div>
        <div class="cb-msg">{{ error }}</div>
        <router-link to="/game" class="cb-btn">Back to Game</router-link>
      </template>
      <template v-else>
        <div class="cb-dots"><span></span><span></span><span></span></div>
        <div class="cb-title">Connecting to OpenRouter...</div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { exchangeAuthCode } from '../api/game.js'
import { useAuth } from '../composables/useAuth.js'

const router = useRouter()
const { setKey } = useAuth()
const error = ref('')

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')

  if (!code) {
    error.value = 'No authorization code received.'
    return
  }

  try {
    const result = await exchangeAuthCode(code)
    setKey(result.key)

    // Return to wherever the user was before auth
    const returnUrl = sessionStorage.getItem('auth_return_url') || '/game'
    sessionStorage.removeItem('auth_return_url')
    router.replace(returnUrl)
  } catch (e) {
    error.value = e?.response?.data?.error || e?.message || 'Could not complete authentication.'
  }
})
</script>

<style scoped>
.callback-root {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
}
.callback-card {
  text-align: center;
  padding: 48px 40px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  max-width: 400px;
}
.cb-icon {
  font-size: 32px;
  color: var(--red);
  margin-bottom: 16px;
}
.cb-title {
  font-family: var(--sans);
  font-size: 18px;
  font-weight: 700;
  color: var(--heading);
  margin-bottom: 12px;
}
.cb-msg {
  font-size: 13px;
  color: var(--text2);
  margin-bottom: 24px;
  line-height: 1.5;
}
.cb-btn {
  display: inline-block;
  background: var(--cyan);
  color: var(--bg);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 700;
  padding: 10px 28px;
  border-radius: 6px;
}
/* loading dots */
.cb-dots { display: flex; gap: 6px; justify-content: center; margin-bottom: 20px; }
.cb-dots span {
  width: 8px; height: 8px;
  background: var(--cyan);
  border-radius: 50%;
  animation: cbdot 1.4s infinite ease-in-out;
}
.cb-dots span:nth-child(2) { animation-delay: 0.2s; }
.cb-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes cbdot {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}
</style>
