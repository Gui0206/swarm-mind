<template>
  <div class="game-root">
    <!-- ========== LOBBY ========== -->
    <div v-if="phase === 'lobby'" class="lobby">
      <div class="lobby-top">
        <router-link to="/" class="top-back">&larr; MIROFISH</router-link>
        <button class="theme-toggle" @click="toggle" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
          {{ theme === 'dark' ? '\u2600' : '\u263E' }}
        </button>
      </div>

      <div class="lobby-header">
        <h1 class="lobby-title">SWARM MIND</h1>
        <p class="lobby-tagline">Whisper to the swarm. Shape reality.</p>
        <p class="lobby-desc">
          You're a hidden manipulator in a group of AI agents. Each has a unique personality.
          <strong>Whisper</strong> to any agent to influence the conversation and achieve your
          <strong>secret objective</strong> before the rounds run out.
        </p>
      </div>

      <div v-if="error" class="error-banner">{{ error }}</div>

      <!-- Custom scenario from shared link -->
      <template v-if="customScenario">
        <div class="custom-banner">CUSTOM SCENARIO</div>
        <div class="scenario-grid">
          <button
            class="scenario-card scenario-card-custom"
            @click="startCustomGame()"
            :disabled="starting"
          >
            <div class="sc-title">{{ customScenario.title }}</div>
            <div class="sc-desc">{{ customScenario.description }}</div>
            <div class="sc-meta">
              <span class="sc-obj">{{ customScenario.objective }}</span>
              <span class="sc-agents">{{ customScenario.agents.length }} agents</span>
            </div>
            <div class="sc-agent-emojis">
              <span v-for="(a, i) in customScenario.agents" :key="i">{{ a.emoji }}</span>
            </div>
          </button>
        </div>
        <button class="random-btn" @click="startCustomGame()" :disabled="starting">
          {{ starting ? 'INITIALIZING SWARM...' : 'PLAY THIS CHALLENGE' }}
        </button>
        <router-link to="/game" class="browse-link" @click.native="clearCustom">or browse all scenarios</router-link>
      </template>

      <!-- Normal scenario grid -->
      <template v-else>
        <div class="scenario-grid">
          <button
            v-for="s in scenarios"
            :key="s.id"
            class="scenario-card"
            @click="startGame(s.id)"
            :disabled="starting"
          >
            <div class="sc-title">{{ s.title }}</div>
            <div class="sc-desc">{{ s.description }}</div>
            <div class="sc-meta">
              <span class="sc-obj">{{ s.objective }}</span>
              <span class="sc-agents">{{ s.agent_count }} agents</span>
            </div>
          </button>
        </div>

        <button class="random-btn" @click="startGame(null)" :disabled="starting">
          {{ starting ? 'INITIALIZING SWARM...' : 'RANDOM SCENARIO' }}
        </button>
      </template>
    </div>

    <!-- ========== GAME ========== -->
    <div v-else class="game-container">
      <!-- HUD -->
      <div class="game-hud">
        <div class="hud-left">
          <button class="hud-btn" @click="confirmExit">EXIT</button>
          <a href="https://github.com/Gui0206/swarm-mind" target="_blank" class="hud-gh">Star on GitHub</a>
        </div>
        <span class="hud-scenario">{{ game?.scenario?.title }}</span>
        <div class="hud-right">
          <span class="hud-round">
            ROUND {{ game?.current_round || 0 }} / {{ game?.total_rounds || 0 }}
          </span>
          <button class="theme-toggle theme-toggle-sm" @click="toggle">
            {{ theme === 'dark' ? '\u2600' : '\u263E' }}
          </button>
        </div>
      </div>

      <div class="game-body">
        <!-- Conversation Panel -->
        <div class="conv-panel">
          <div class="conv-scroll" ref="convScroll">
            <template v-for="(msg, i) in visibleMessages" :key="i">
              <!-- Round divider -->
              <div v-if="i === 0 || visibleMessages[i-1]?.round !== msg.round" class="round-divider">
                <span>ROUND {{ msg.round }}</span>
              </div>
              <!-- Message -->
              <div class="msg" :class="{ 'msg-whispered': msg.is_whispered }">
                <div class="msg-avatar">{{ msg.agent_emoji }}</div>
                <div class="msg-body">
                  <span class="msg-name" :class="{ 'whispered-name': msg.is_whispered }">
                    {{ msg.agent_name }}
                    <span v-if="msg.is_whispered" class="whisper-badge" title="Influenced by your whisper">whispered</span>
                  </span>
                  <span class="msg-text">{{ msg.content }}</span>
                </div>
              </div>
            </template>

            <!-- Thinking indicator -->
            <div v-if="thinking" class="thinking-box">
              <div class="thinking-dots"><span></span><span></span><span></span></div>
              <span>Agents are discussing...</span>
            </div>

            <!-- Empty state -->
            <div v-if="!visibleMessages.length && !thinking" class="conv-empty">
              Waiting for agents to start the conversation...
            </div>

            <!-- Game Over result (inline) -->
            <Transition name="fade">
              <div v-if="phase === 'result' && evaluation" class="result-inline">
                <div class="result-divider"><span>GAME OVER</span></div>
                <div class="result-card">
                  <div class="result-badge" :class="evaluation.achieved ? 'badge-success' : 'badge-fail'">
                    {{ evaluation.achieved ? 'MISSION COMPLETE' : 'MISSION FAILED' }}
                  </div>
                  <div class="result-stars">
                    <span v-for="i in 3" :key="i" :class="i <= evaluation.stars ? 'star-on' : 'star-off'">
                      {{ i <= evaluation.stars ? '\u2B50' : '\u2606' }}
                    </span>
                  </div>
                  <div class="result-score">{{ evaluation.score }} / 100</div>
                  <div class="result-summary">{{ evaluation.summary }}</div>
                  <div class="result-stats">
                    {{ game.total_rounds }} rounds &middot; {{ game.whispers_used }} whispers &middot; {{ visibleMessages.length }} messages
                  </div>
                  <div class="result-actions">
                    <button class="rbtn" @click="startGame(game.scenario.id)">RETRY</button>
                    <button class="rbtn rbtn-alt" @click="backToLobby">ALL SCENARIOS</button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>

          <!-- Whisper Panel -->
          <div v-if="canWhisper" class="whisper-panel">
            <div class="whisper-row">
              <span class="whisper-label">WHISPER TO</span>
              <select v-model="selectedAgentId" class="agent-select">
                <option value="">Select an agent...</option>
                <option v-for="a in game.agents" :key="a.id" :value="a.id">
                  {{ a.emoji }} {{ a.name }}
                </option>
              </select>
            </div>
            <textarea
              v-model="whisperText"
              class="whisper-input"
              :placeholder="selectedAgentId
                ? `Only ${selectedAgentName} will hear this...`
                : 'Select an agent first, then type your whisper...'"
              rows="2"
              :disabled="!selectedAgentId"
              @keydown.enter.ctrl="advance"
            ></textarea>
            <div class="whisper-actions">
              <button class="btn-advance" @click="advance" :disabled="thinking || animating">
                {{ whisperText.trim() && selectedAgentId ? 'SEND WHISPER & CONTINUE' : 'SKIP & CONTINUE' }}
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="error-bar">{{ error }}</div>
        </div>

        <!-- Sidebar -->
        <div class="sidebar">
          <div class="obj-card">
            <div class="obj-label">MISSION</div>
            <div class="obj-text">{{ game?.scenario?.objective }}</div>
          </div>

          <div class="agents-section">
            <div class="agents-label">SWARM AGENTS</div>
            <div
              v-for="a in game?.agents"
              :key="a.id"
              class="agent-card"
              :class="{ selected: selectedAgentId === a.id }"
              @click="selectedAgentId = a.id"
            >
              <span class="agent-emoji">{{ a.emoji }}</span>
              <div class="agent-info">
                <div class="agent-name">{{ a.name }}</div>
                <div class="agent-bio">{{ a.bio }}</div>
              </div>
            </div>
          </div>

          <div class="stats-section">
            <div class="stat-row">
              <span>Whispers used</span>
              <span class="stat-val">{{ game?.whispers_used || 0 }}</span>
            </div>
            <div class="stat-row">
              <span>Messages</span>
              <span class="stat-val">{{ visibleMessages.length }}</span>
            </div>
          </div>

          <!-- Whisper History -->
          <div v-if="game?.whisper_log?.length" class="whisper-history">
            <div class="wh-label">YOUR WHISPERS</div>
            <div v-for="(w, i) in game.whisper_log" :key="i" class="wh-item">
              <span class="wh-round">R{{ w.round }}</span>
              <span class="wh-target">{{ w.agent_name }}</span>
              <span class="wh-msg">{{ w.message }}</span>
            </div>
          </div>

          <!-- Custom game share -->
          <div v-if="customShareUrl" class="custom-share-box">
            <div class="cs-label">SHARE THIS CHALLENGE</div>
            <div class="cs-url-row">
              <input :value="customShareUrl" readonly class="cs-url-input" @click="$event.target.select()" />
              <button class="cs-copy-btn" @click="copyCustomLink">{{ customCopied ? 'COPIED!' : 'COPY' }}</button>
            </div>
            <div class="cs-hint">Copy link to share this scenario.</div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import * as gameApi from '../api/game.js'
import { useTheme } from '../composables/useTheme.js'

const { theme, toggle } = useTheme()

// --- State ---
const phase = ref('lobby') // lobby | playing | result
const scenarios = ref([])
const customScenario = ref(null) // decoded custom scenario from URL
const game = ref(null)
const visibleMessages = ref([])
const selectedAgentId = ref('')
const whisperText = ref('')
const thinking = ref(false)
const animating = ref(false)
const evaluation = ref(null)
const error = ref(null)
const starting = ref(false)
const convScroll = ref(null)
const customShareUrl = ref('')
const customCopied = ref(false)

// --- Computed ---
const canWhisper = computed(() => {
  return phase.value === 'playing'
    && !thinking.value
    && !animating.value
    && game.value
    && game.value.current_round > 0
    && game.value.current_round < game.value.total_rounds
})

const selectedAgentName = computed(() => {
  if (!selectedAgentId.value || !game.value) return ''
  const a = game.value.agents.find(a => a.id === selectedAgentId.value)
  return a ? a.name : ''
})

// --- URL decoding for custom scenarios ---
function decodeCustomHash() {
  const hash = window.location.hash
  if (!hash.startsWith('#custom=')) return null
  try {
    const encoded = hash.slice('#custom='.length)
    const padded = encoded.replace(/-/g, '+').replace(/_/g, '/')
    const pad = (4 - padded.length % 4) % 4
    const b64 = padded + '='.repeat(pad)
    const binary = atob(b64)
    const bytes = new Uint8Array(binary.length)
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i)
    const compact = JSON.parse(new TextDecoder().decode(bytes))
    return {
      title: compact.t,
      description: compact.d || compact.t,
      objective: compact.o,
      opening: compact.p,
      eval_q: compact.q || compact.o,
      rounds: compact.r || 6,
      agents: (compact.a || []).map(a => ({
        name: a.n,
        emoji: a.e || '\u{1F916}',
        personality: a.y || a.b || '',
        bio: a.b || a.y || '',
      })),
    }
  } catch {
    return null
  }
}

// --- Lifecycle ---
onMounted(async () => {
  // Check for custom scenario in URL hash
  const custom = decodeCustomHash()
  if (custom) {
    customScenario.value = custom
    customShareUrl.value = window.location.href
    // Don't load built-in scenarios — show only the custom one
    return
  }

  try {
    scenarios.value = await gameApi.getScenarios()
  } catch (e) {
    error.value = 'Could not connect to backend. Make sure the Flask server is running on port 5001.'
  }
})

// --- Game Flow ---
async function startGame(scenarioId) {
  try {
    error.value = null
    starting.value = true
    phase.value = 'playing'
    thinking.value = true
    visibleMessages.value = []
    selectedAgentId.value = ''
    whisperText.value = ''
    evaluation.value = null

    game.value = await gameApi.newGame(scenarioId)

    // Auto-run round 1 (observation round — no whisper opportunity)
    await runTick()
    starting.value = false
  } catch (e) {
    starting.value = false
    error.value = e?.response?.data?.error || e?.error || e?.message || 'Failed to start game'
    phase.value = 'lobby'
    thinking.value = false
  }
}

async function startCustomGame() {
  if (!customScenario.value) return
  try {
    error.value = null
    starting.value = true
    phase.value = 'playing'
    thinking.value = true
    visibleMessages.value = []
    selectedAgentId.value = ''
    whisperText.value = ''
    evaluation.value = null

    game.value = await gameApi.newCustomGame(customScenario.value)

    await runTick()
    starting.value = false
  } catch (e) {
    starting.value = false
    error.value = e?.response?.data?.error || e?.error || e?.message || 'Failed to start custom game'
    phase.value = 'lobby'
    thinking.value = false
  }
}

async function advance() {
  if (thinking.value || animating.value) return

  // Send whisper if typed
  if (whisperText.value.trim() && selectedAgentId.value) {
    try {
      await gameApi.whisper(game.value.game_id, selectedAgentId.value, whisperText.value.trim())
      // Update local whisper log
      if (!game.value.whisper_log) game.value.whisper_log = []
      game.value.whisper_log.push({
        round: game.value.current_round + 1,
        agent_id: selectedAgentId.value,
        agent_name: selectedAgentName.value,
        message: whisperText.value.trim(),
      })
      game.value.whispers_used = (game.value.whispers_used || 0) + 1
    } catch (e) {
      error.value = e?.response?.data?.error || e?.error || e?.message || 'Whisper failed'
      return
    }
  }

  whisperText.value = ''
  selectedAgentId.value = ''
  await runTick()
}

async function runTick() {
  thinking.value = true
  error.value = null

  try {
    const result = await gameApi.tick(game.value.game_id)
    thinking.value = false

    // Animate messages appearing one by one
    animating.value = true
    for (const msg of result.messages) {
      visibleMessages.value.push(msg)
      await nextTick()
      scrollToBottom()
      await delay(550)
    }
    animating.value = false

    game.value.current_round = result.round

    if (result.game_over && result.evaluation) {
      evaluation.value = result.evaluation
      await delay(1200)
      phase.value = 'result'
      await nextTick()
      scrollToBottom()
    }
  } catch (e) {
    thinking.value = false
    animating.value = false
    error.value = e?.response?.data?.error || e?.error || e?.message || 'Round failed'
  }
}

function confirmExit() {
  if (game.value && phase.value === 'playing') {
    if (!confirm('Exit current game?')) return
  }
  backToLobby()
}

function backToLobby() {
  phase.value = 'lobby'
  game.value = null
  visibleMessages.value = []
  evaluation.value = null
  error.value = null
}

function clearCustom() {
  customScenario.value = null
  window.location.hash = ''
  // Load built-in scenarios
  gameApi.getScenarios().then(s => { scenarios.value = s }).catch(() => {})
}

function copyCustomLink() {
  navigator.clipboard.writeText(customShareUrl.value).then(() => {
    customCopied.value = true
    setTimeout(() => { customCopied.value = false }, 2000)
  })
}

function scrollToBottom() {
  if (convScroll.value) {
    convScroll.value.scrollTop = convScroll.value.scrollHeight
  }
}

function delay(ms) {
  return new Promise(r => setTimeout(r, ms))
}
</script>

<style scoped>
.game-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
}

/* ---- LOBBY ---- */
.lobby {
  max-width: 900px;
  margin: 0 auto;
  padding: 60px 24px;
}

.lobby-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.top-back {
  display: inline-block;
  color: var(--text2);
  text-decoration: none;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  border: 1px solid var(--border);
  padding: 6px 14px;
  border-radius: 4px;
  transition: all 0.2s;
}
.top-back:hover { color: var(--cyan); border-color: var(--cyan); }

.lobby-header { text-align: center; margin-bottom: 50px; }

.lobby-title {
  font-family: var(--sans);
  font-size: 52px;
  font-weight: 700;
  color: var(--cyan);
  margin: 0 0 10px;
}

.lobby-tagline {
  font-size: 16px;
  color: var(--text2);
  margin: 0 0 24px;
  font-style: italic;
}

.lobby-desc {
  font-size: 14px;
  color: var(--text2);
  max-width: 600px;
  margin: 0 auto;
  line-height: 1.7;
}
.lobby-desc strong { color: var(--cyan); }

.error-banner {
  background: rgba(255,82,82,0.12);
  border: 1px solid rgba(255,82,82,0.3);
  color: var(--red);
  padding: 12px 16px;
  border-radius: 6px;
  font-size: 13px;
  margin-bottom: 24px;
  text-align: center;
}

.scenario-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.scenario-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px 20px;
  text-align: left;
  cursor: pointer;
  transition: all 0.25s;
  color: var(--text);
  font-family: var(--mono);
}
.scenario-card:hover {
  border-color: var(--cyan);
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0,229,255,0.1);
}
.scenario-card:disabled { opacity: 0.5; cursor: wait; }

.sc-title {
  font-family: var(--sans);
  font-size: 17px;
  font-weight: 700;
  color: var(--heading);
  margin-bottom: 8px;
}
.sc-desc { font-size: 12px; color: var(--text2); line-height: 1.5; margin-bottom: 12px; }
.sc-meta { display: flex; justify-content: space-between; align-items: flex-end; gap: 8px; }
.sc-obj { font-size: 11px; color: var(--gold); flex: 1; }
.sc-agents { font-size: 10px; color: var(--text2); white-space: nowrap; }

.random-btn {
  display: block;
  width: 100%;
  max-width: 320px;
  margin: 0 auto;
  padding: 16px;
  background: transparent;
  border: 2px solid var(--cyan);
  color: var(--cyan);
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.random-btn:hover { background: rgba(0,229,255,0.1); }
.random-btn:disabled { opacity: 0.5; cursor: wait; }

.custom-banner {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--purple);
  text-align: center;
  margin-bottom: 16px;
}

.scenario-card-custom {
  border-color: var(--purple);
}
.scenario-card-custom:hover {
  border-color: var(--purple);
  box-shadow: 0 8px 30px rgba(192,108,255,0.12);
}

.sc-agent-emojis {
  display: flex;
  gap: 6px;
  margin-top: 10px;
  font-size: 18px;
}

.browse-link {
  display: block;
  text-align: center;
  margin-top: 16px;
  color: var(--text2);
  font-size: 12px;
  text-decoration: none;
  transition: color 0.2s;
}
.browse-link:hover { color: var(--cyan); }

/* ---- GAME LAYOUT ---- */
.game-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.game-hud {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 48px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}

.hud-btn {
  background: none;
  border: 1px solid var(--border);
  color: var(--text2);
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: all 0.2s;
}
.hud-btn:hover { color: var(--red); border-color: var(--red); }

.hud-scenario {
  font-family: var(--sans);
  font-size: 14px;
  font-weight: 600;
  color: var(--heading);
}

.hud-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.hud-round {
  font-size: 12px;
  color: var(--cyan);
  font-weight: 700;
  letter-spacing: 1px;
}

.theme-toggle-sm {
  width: 28px;
  height: 28px;
  font-size: 14px;
}

.hud-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hud-gh {
  color: var(--gold);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border: 1px solid var(--gold);
  border-radius: 4px;
  transition: all 0.2s;
}
.hud-gh:hover { filter: brightness(1.2); transform: translateY(-1px); }

.game-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* ---- CONVERSATION ---- */
.conv-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.conv-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  scroll-behavior: smooth;
}

.round-divider {
  text-align: center;
  margin: 20px 0 14px;
  position: relative;
}
.round-divider span {
  background: var(--bg);
  padding: 0 12px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text2);
  position: relative;
  z-index: 1;
}
.round-divider::before {
  content: '';
  position: absolute;
  left: 0; right: 0; top: 50%;
  border-top: 1px solid var(--border);
}

.msg {
  display: flex;
  gap: 12px;
  margin-bottom: 14px;
  padding: 10px 14px;
  border-radius: 8px;
  background: var(--surface);
  border: 1px solid transparent;
  animation: msgIn 0.35s ease-out;
}

.msg-whispered {
  background: rgba(192, 108, 255, 0.08);
  border-color: rgba(192, 108, 255, 0.2);
}

@keyframes msgIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.msg-avatar {
  font-size: 22px;
  flex-shrink: 0;
  width: 32px;
  text-align: center;
  padding-top: 2px;
}

.msg-body { flex: 1; min-width: 0; }

.msg-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  color: var(--cyan);
  margin-bottom: 4px;
}
.whispered-name { color: var(--purple); }

.whisper-badge {
  font-size: 9px;
  font-weight: 600;
  color: var(--purple);
  border: 1px solid rgba(192,108,255,0.3);
  padding: 1px 6px;
  border-radius: 3px;
  letter-spacing: 0.5px;
}

.msg-text {
  font-size: 13px;
  line-height: 1.55;
  color: var(--text);
}

.thinking-box {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  color: var(--text2);
  font-size: 13px;
}

.thinking-dots { display: flex; gap: 4px; }
.thinking-dots span {
  width: 6px; height: 6px;
  background: var(--cyan);
  border-radius: 50%;
  animation: dot 1.4s infinite ease-in-out;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dot {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
}

.conv-empty {
  text-align: center;
  color: var(--text2);
  font-size: 13px;
  padding: 40px 0;
}

/* ---- WHISPER PANEL ---- */
.whisper-panel {
  border-top: 1px solid var(--border);
  padding: 16px 24px;
  background: var(--surface);
  flex-shrink: 0;
}

.whisper-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.whisper-label {
  font-size: 11px;
  font-weight: 700;
  color: var(--purple);
  letter-spacing: 1px;
  white-space: nowrap;
}

.agent-select {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--mono);
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 4px;
  outline: none;
}
.agent-select:focus { border-color: var(--purple); }

.whisper-input {
  width: 100%;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--mono);
  font-size: 13px;
  padding: 10px 12px;
  border-radius: 6px;
  resize: none;
  outline: none;
  margin-bottom: 10px;
  box-sizing: border-box;
}
.whisper-input:focus { border-color: var(--purple); }
.whisper-input:disabled { opacity: 0.4; }
.whisper-input::placeholder { color: var(--text2); opacity: 0.5; }

.whisper-actions { display: flex; justify-content: flex-end; }

.btn-advance {
  background: var(--cyan);
  color: var(--bg);
  border: none;
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 700;
  padding: 10px 24px;
  border-radius: 6px;
  cursor: pointer;
  letter-spacing: 0.5px;
  transition: all 0.2s;
}
.btn-advance:hover { opacity: 0.85; transform: translateY(-1px); }
.btn-advance:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

.error-bar {
  background: rgba(255,82,82,0.1);
  border-top: 1px solid rgba(255,82,82,0.2);
  color: var(--red);
  padding: 8px 24px;
  font-size: 12px;
  flex-shrink: 0;
}

/* ---- SIDEBAR ---- */
.sidebar {
  width: 280px;
  flex-shrink: 0;
  border-left: 1px solid var(--border);
  background: var(--surface);
  overflow-y: auto;
  padding: 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.obj-card {
  background: rgba(255,215,64,0.06);
  border: 1px solid rgba(255,215,64,0.2);
  border-radius: 8px;
  padding: 16px;
}
.obj-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--gold);
  letter-spacing: 2px;
  margin-bottom: 8px;
}
.obj-text {
  font-size: 13px;
  line-height: 1.5;
  color: var(--text);
}

.agents-section {}
.agents-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--text2);
  letter-spacing: 2px;
  margin-bottom: 10px;
}

.agent-card {
  display: flex;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.2s;
  margin-bottom: 4px;
}
.agent-card:hover { background: rgba(128,128,128,0.08); }
.agent-card.selected {
  border-color: var(--purple);
  background: rgba(192,108,255,0.08);
}

.agent-emoji { font-size: 20px; flex-shrink: 0; }
.agent-info { flex: 1; min-width: 0; }
.agent-name { font-size: 12px; font-weight: 700; color: var(--heading); margin-bottom: 2px; }
.agent-bio { font-size: 10px; color: var(--text2); line-height: 1.3; }

.stats-section {}
.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text2);
  padding: 4px 0;
}
.stat-val { color: var(--cyan); font-weight: 700; }

.whisper-history {}
.wh-label {
  font-size: 10px;
  font-weight: 700;
  color: var(--purple);
  letter-spacing: 1px;
  margin-bottom: 8px;
}
.wh-item {
  font-size: 10px;
  color: var(--text2);
  padding: 6px 8px;
  background: rgba(192,108,255,0.06);
  border-radius: 4px;
  margin-bottom: 4px;
  line-height: 1.4;
}
.wh-round {
  color: var(--purple);
  font-weight: 700;
  margin-right: 6px;
}
.wh-target {
  color: var(--text);
  font-weight: 600;
  margin-right: 4px;
}
.wh-target::after { content: ':'; }
.wh-msg { color: var(--text2); }

/* ---- CUSTOM SHARE BOX ---- */
.custom-share-box {
  background: rgba(192,108,255,0.06);
  border: 1px solid rgba(192,108,255,0.2);
  border-radius: 8px;
  padding: 14px;
}
.cs-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--purple);
  margin-bottom: 10px;
}
.cs-url-row {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}
.cs-url-input {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--mono);
  font-size: 9px;
  padding: 6px 8px;
  border-radius: 4px;
  outline: none;
  min-width: 0;
}
.cs-copy-btn {
  background: var(--purple);
  border: none;
  color: #fff;
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 700;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.2s;
}
.cs-copy-btn:hover { opacity: 0.85; }
.cs-hint {
  font-size: 9px;
  color: var(--text2);
  line-height: 1.4;
}

/* ---- INLINE RESULT ---- */
.result-inline {
  margin: 24px 0 40px;
}

.result-divider {
  text-align: center;
  margin: 20px 0 14px;
  position: relative;
}
.result-divider span {
  background: var(--bg);
  padding: 0 12px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--gold);
  position: relative;
  z-index: 1;
}
.result-divider::before {
  content: '';
  position: absolute;
  left: 0; right: 0; top: 50%;
  border-top: 1px solid var(--gold);
}

.result-card {
  text-align: center;
  max-width: 440px;
  margin: 0 auto;
  padding: 32px 28px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
}

.result-badge {
  font-family: var(--sans);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 2px;
  margin-bottom: 16px;
}
.badge-success { color: var(--green); text-shadow: 0 0 40px rgba(105,240,174,0.3); }
.badge-fail { color: var(--red); text-shadow: 0 0 40px rgba(255,82,82,0.3); }

.result-stars {
  font-size: 36px;
  margin-bottom: 12px;
}
.star-on { filter: none; }
.star-off { opacity: 0.2; }

.result-score {
  font-size: 40px;
  font-weight: 700;
  color: var(--heading);
  margin-bottom: 16px;
}

.result-summary {
  font-size: 14px;
  color: var(--text);
  line-height: 1.6;
  margin-bottom: 20px;
}

.result-stats {
  font-size: 11px;
  color: var(--text2);
  margin-bottom: 30px;
}

.result-actions { display: flex; gap: 12px; justify-content: center; }

.rbtn {
  background: var(--cyan);
  color: var(--bg);
  border: none;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 700;
  padding: 12px 28px;
  border-radius: 6px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: all 0.2s;
}
.rbtn:hover { opacity: 0.85; }

.rbtn-alt {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text2);
}
.rbtn-alt:hover { border-color: var(--cyan); color: var(--cyan); }

/* Transitions */
.fade-enter-active { transition: opacity 0.4s; }
.fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ---- RESPONSIVE ---- */
@media (max-width: 800px) {
  .game-body { flex-direction: column; }
  .sidebar {
    width: 100%;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    border-left: none;
    border-top: 1px solid var(--border);
    max-height: 200px;
    overflow-y: auto;
  }
  .obj-card { flex: 1 1 100%; }
  .agents-section { flex: 1 1 100%; }
  .scenario-grid { grid-template-columns: 1fr; }
  .lobby { padding: 30px 16px; }
  .lobby-title { font-size: 36px; }
}

/* Scrollbar */
.conv-scroll::-webkit-scrollbar,
.sidebar::-webkit-scrollbar { width: 4px; }
.conv-scroll::-webkit-scrollbar-track,
.sidebar::-webkit-scrollbar-track { background: transparent; }
.conv-scroll::-webkit-scrollbar-thumb,
.sidebar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
