<template>
  <div class="create-root">
    <nav class="nav">
      <router-link to="/" class="nav-brand">SWARM MIND</router-link>
      <div class="nav-right">
        <button class="theme-toggle" @click="toggle" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
          {{ theme === 'dark' ? '\u2600' : '\u263E' }}
        </button>
        <router-link to="/game" class="nav-link">PLAY</router-link>
      </div>
    </nav>

    <main class="create-main">
      <div class="form-col">
        <h1 class="page-title">Create Your Scenario</h1>
        <p class="page-sub">Design a custom challenge and share it with friends via a link. No account needed.</p>

        <!-- Scenario Details -->
        <section class="form-section">
          <div class="section-label">SCENARIO DETAILS</div>

          <label class="field">
            <span class="field-label">Title <span class="req">*</span></span>
            <input v-model="form.title" maxlength="80" placeholder="e.g. The Crypto Cult" class="field-input" />
          </label>

          <label class="field">
            <span class="field-label">Description</span>
            <input v-model="form.description" maxlength="200" placeholder="Short tagline for the scenario card" class="field-input" />
          </label>

          <label class="field">
            <span class="field-label">Objective <span class="req">*</span></span>
            <textarea v-model="form.objective" rows="2" maxlength="300" placeholder="What must the player achieve? e.g. Get the majority to invest in your fake crypto coin." class="field-textarea"></textarea>
          </label>

          <label class="field">
            <span class="field-label">Opening Context <span class="req">*</span></span>
            <textarea v-model="form.opening" rows="2" maxlength="300" placeholder="Set the scene. e.g. Friends are chatting in a group about investment ideas." class="field-textarea"></textarea>
          </label>

          <label class="field">
            <span class="field-label">Evaluation Question</span>
            <textarea v-model="form.eval_q" rows="2" maxlength="300" placeholder="How should the AI judge score? Leave blank to auto-generate from objective." class="field-textarea"></textarea>
          </label>

          <label class="field">
            <span class="field-label">Rounds</span>
            <div class="rounds-row">
              <input v-model.number="form.rounds" type="range" min="3" max="6" class="range-input" />
              <span class="rounds-val">{{ form.rounds }}</span>
            </div>
          </label>
        </section>

        <!-- Agents -->
        <section class="form-section">
          <div class="section-label">AGENTS <span class="agent-count">{{ form.agents.length }} / 6</span></div>

          <div v-for="(agent, i) in form.agents" :key="i" class="agent-form-card">
            <div class="agent-form-header">
              <span class="agent-num">{{ i + 1 }}</span>
              <input v-model="agent.emoji" class="emoji-input" maxlength="4" placeholder="&#x1F916;" />
              <input v-model="agent.name" class="name-input" placeholder="Agent name" maxlength="30" />
              <button v-if="form.agents.length > 2" class="remove-agent" @click="removeAgent(i)" title="Remove agent">&times;</button>
            </div>
            <input v-model="agent.bio" class="field-input agent-field" placeholder="One-line bio (e.g. Dog walker with 3 golden retrievers)" maxlength="120" />
            <textarea v-model="agent.personality" class="field-textarea agent-field" rows="2" placeholder="Personality traits (e.g. Sarcastic, contrarian, always plays devil's advocate)" maxlength="250"></textarea>
          </div>

          <button v-if="form.agents.length < 6" class="add-agent-btn" @click="addAgent">+ ADD AGENT</button>
        </section>

        <!-- Actions -->
        <section class="actions-section">
          <div v-if="validationError" class="validation-error">{{ validationError }}</div>

          <div class="action-row">
            <button class="btn-play" @click="playNow">PLAY NOW</button>
          </div>
        </section>
      </div>

      <!-- Live Preview -->
      <div class="preview-col">
        <div class="preview-sticky">
          <div class="preview-label">PREVIEW</div>
          <div class="preview-card">
            <div class="pc-title">{{ form.title || 'Your Scenario' }}</div>
            <div class="pc-desc">{{ form.description || form.objective || 'Add a description...' }}</div>
            <div class="pc-obj">{{ form.objective || 'Set your objective...' }}</div>
            <div class="pc-agents">
              <span v-for="(a, i) in form.agents" :key="i" class="pc-emoji" :title="a.name">{{ a.emoji || '\u{1F916}' }}</span>
            </div>
            <div class="pc-meta">{{ form.agents.length }} agents &middot; {{ form.rounds }} rounds</div>
          </div>

          <!-- Share box (always visible) -->
          <div class="share-box">
            <div class="share-label">SHARE LINK</div>
            <template v-if="shareUrl">
              <div class="share-url-row">
                <input :value="shareUrl" readonly class="share-url-input" ref="shareInput" @click="selectShareInput" />
                <button class="copy-btn" @click="copyLink">{{ copied ? 'COPIED!' : 'COPY' }}</button>
              </div>
              <div class="share-hint">Anyone with this link can play your scenario. No sign-up required.</div>
              <div class="share-socials">
                <a :href="twitterShareUrl" target="_blank" class="social-btn social-x">Share on X</a>
                <a :href="whatsappShareUrl" target="_blank" class="social-btn social-wa">WhatsApp</a>
              </div>
            </template>
            <div v-else class="share-hint">Fill in the required fields to generate a share link.</div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from '../composables/useTheme.js'

const router = useRouter()
const { theme, toggle } = useTheme()

// --- Form State ---
const form = reactive({
  title: '',
  description: '',
  objective: '',
  opening: '',
  eval_q: '',
  rounds: 6,
  agents: [
    { name: '', emoji: '', personality: '', bio: '' },
    { name: '', emoji: '', personality: '', bio: '' },
    { name: '', emoji: '', personality: '', bio: '' },
  ],
})

const copied = ref(false)
const validationError = ref('')
const shareInput = ref(null)

// --- Agents ---
function addAgent() {
  if (form.agents.length < 6) {
    form.agents.push({ name: '', emoji: '', personality: '', bio: '' })
  }
}

function removeAgent(i) {
  if (form.agents.length > 2) {
    form.agents.splice(i, 1)
  }
}

// --- Validation ---
function validate() {
  if (!form.title.trim()) return 'Title is required.'
  if (!form.objective.trim()) return 'Objective is required.'
  if (!form.opening.trim()) return 'Opening context is required.'

  const namedAgents = form.agents.filter(a => a.name.trim())
  if (namedAgents.length < 2) return 'At least 2 agents with names are required.'

  for (let i = 0; i < form.agents.length; i++) {
    const a = form.agents[i]
    if (a.name.trim() && !a.personality.trim() && !a.bio.trim()) {
      return `Agent "${a.name}" needs a personality or bio.`
    }
  }
  return ''
}

// --- Encoding ---
function buildCompact() {
  const agents = form.agents
    .filter(a => a.name.trim())
    .map(a => ({
      n: a.name.trim(),
      e: a.emoji.trim() || '\u{1F916}',
      y: a.personality.trim(),
      b: a.bio.trim(),
    }))

  return {
    t: form.title.trim(),
    d: form.description.trim(),
    o: form.objective.trim(),
    p: form.opening.trim(),
    q: form.eval_q.trim() || form.objective.trim(),
    r: form.rounds,
    a: agents,
  }
}

function encodeScenario(compact) {
  const json = JSON.stringify(compact)
  const bytes = new TextEncoder().encode(json)
  let binary = ''
  for (const b of bytes) binary += String.fromCharCode(b)
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '')
}

// --- Share URL (auto-computed) ---
const shareUrl = computed(() => {
  if (validate()) return ''
  const compact = buildCompact()
  const encoded = encodeScenario(compact)
  return `${window.location.origin}/game#custom=${encoded}`
})

// --- Actions ---
function playNow() {
  const err = validate()
  if (err) { validationError.value = err; return }
  validationError.value = ''

  const compact = buildCompact()
  const encoded = encodeScenario(compact)
  router.push(`/game#custom=${encoded}`)
}

function copyLink() {
  navigator.clipboard.writeText(shareUrl.value).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

function selectShareInput() {
  shareInput.value?.select()
}

// --- Social sharing ---
const twitterShareUrl = computed(() => {
  if (!shareUrl.value) return '#'
  const text = `I created a custom Swarm Mind challenge: "${form.title}". Can you beat it?`
  return `https://x.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(shareUrl.value)}`
})

const whatsappShareUrl = computed(() => {
  if (!shareUrl.value) return '#'
  const text = `I made a Swarm Mind challenge for you! "${form.title}" \u2014 try to beat it: ${shareUrl.value}`
  return `https://wa.me/?text=${encodeURIComponent(text)}`
})
</script>

<style scoped>
.create-root {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
}

/* Nav */
.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
  height: 56px;
  border-bottom: 1px solid var(--border);
}
.nav-brand {
  font-family: var(--sans);
  font-weight: 700;
  font-size: 15px;
  color: var(--cyan);
  letter-spacing: 2px;
  text-decoration: none;
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-link {
  color: var(--text2);
  text-decoration: none;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 2px;
  transition: color 0.2s;
}
.nav-link:hover { color: var(--heading); }

/* Main */
.create-main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 48px 40px 80px;
  display: flex;
  gap: 48px;
  align-items: flex-start;
}
.form-col { flex: 1; min-width: 0; }
.preview-col { width: 320px; flex-shrink: 0; }

.page-title {
  font-family: var(--sans);
  font-size: 32px;
  font-weight: 700;
  color: var(--heading);
  margin: 0 0 8px;
}
.page-sub {
  font-size: 13px;
  color: var(--text2);
  margin: 0 0 36px;
  line-height: 1.6;
}

/* Sections */
.form-section {
  margin-bottom: 36px;
}
.section-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--cyan);
  margin-bottom: 16px;
}
.agent-count {
  color: var(--text2);
  margin-left: 8px;
}

/* Fields */
.field {
  display: block;
  margin-bottom: 14px;
}
.field-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  color: var(--text2);
  margin-bottom: 6px;
  letter-spacing: 0.5px;
}
.req { color: var(--gold); }

.field-input, .field-textarea {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--mono);
  font-size: 13px;
  padding: 10px 12px;
  border-radius: 6px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.field-input:focus, .field-textarea:focus {
  border-color: var(--cyan);
}
.field-textarea {
  resize: vertical;
  min-height: 48px;
}
.field-input::placeholder, .field-textarea::placeholder {
  color: var(--text2);
  opacity: 0.5;
}

/* Rounds slider */
.rounds-row {
  display: flex;
  align-items: center;
  gap: 16px;
}
.range-input {
  flex: 1;
  accent-color: var(--cyan);
  height: 4px;
}
.rounds-val {
  font-size: 20px;
  font-weight: 700;
  color: var(--cyan);
  min-width: 28px;
  text-align: center;
}

/* Agent cards */
.agent-form-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 12px;
  transition: border-color 0.2s;
}
.agent-form-card:focus-within {
  border-color: var(--cyan);
}

.agent-form-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}
.agent-num {
  font-size: 10px;
  font-weight: 700;
  color: var(--text2);
  width: 18px;
  text-align: center;
}
.emoji-input {
  width: 44px;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 20px;
  text-align: center;
  padding: 4px;
  border-radius: 6px;
  outline: none;
}
.emoji-input:focus { border-color: var(--cyan); }

.name-input {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--heading);
  font-family: var(--sans);
  font-size: 14px;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 6px;
  outline: none;
}
.name-input:focus { border-color: var(--cyan); }
.name-input::placeholder { color: var(--text2); opacity: 0.5; }

.remove-agent {
  background: none;
  border: none;
  color: var(--text2);
  font-size: 20px;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  transition: color 0.2s;
}
.remove-agent:hover { color: var(--red); }

.agent-field {
  margin-bottom: 8px;
}
.agent-field:last-child { margin-bottom: 0; }

.add-agent-btn {
  display: block;
  width: 100%;
  padding: 12px;
  background: transparent;
  border: 1px dashed var(--cyan);
  color: var(--cyan);
  font-family: var(--mono);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  opacity: 0.6;
}
.add-agent-btn:hover {
  opacity: 1;
}

/* Validation */
.validation-error {
  background: rgba(255,82,82,0.1);
  border: 1px solid rgba(255,82,82,0.25);
  color: var(--red);
  padding: 10px 14px;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 14px;
}

/* Actions */
.actions-section {
  margin-top: 8px;
}
.action-row {
  display: flex;
  gap: 12px;
}
.btn-play {
  flex: 1;
  padding: 14px 20px;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--cyan);
  border: 2px solid var(--cyan);
  color: var(--bg);
}
.btn-play:hover { opacity: 0.85; transform: translateY(-1px); }

/* Preview */
.preview-sticky {
  position: sticky;
  top: 80px;
}
.preview-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--text2);
  margin-bottom: 12px;
}
.preview-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 24px 20px;
}
.pc-title {
  font-family: var(--sans);
  font-size: 17px;
  font-weight: 700;
  color: var(--heading);
  margin-bottom: 8px;
}
.pc-desc {
  font-size: 12px;
  color: var(--text2);
  line-height: 1.5;
  margin-bottom: 12px;
}
.pc-obj {
  font-size: 11px;
  color: var(--gold);
  line-height: 1.4;
  margin-bottom: 14px;
}
.pc-agents {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}
.pc-emoji {
  font-size: 20px;
  cursor: default;
}
.pc-meta {
  font-size: 10px;
  color: var(--text2);
}

/* Share box */
.share-box {
  margin-top: 20px;
  background: var(--surface);
  border: 1px solid var(--purple);
  border-radius: 10px;
  padding: 20px;
}
.share-label {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--purple);
  margin-bottom: 12px;
}
.share-url-row {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
}
.share-url-input {
  flex: 1;
  background: var(--surface2);
  border: 1px solid var(--border);
  color: var(--text);
  font-family: var(--mono);
  font-size: 10px;
  padding: 8px 10px;
  border-radius: 4px;
  outline: none;
  min-width: 0;
}
.copy-btn {
  background: var(--purple);
  border: none;
  color: #fff;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 4px;
  cursor: pointer;
  letter-spacing: 0.5px;
  white-space: nowrap;
  transition: opacity 0.2s;
}
.copy-btn:hover { opacity: 0.85; }

.share-hint {
  font-size: 10px;
  color: var(--text2);
  line-height: 1.4;
  margin-bottom: 12px;
}

.share-socials {
  display: flex;
  gap: 8px;
}
.social-btn {
  flex: 1;
  text-align: center;
  padding: 8px 12px;
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 600;
  border-radius: 4px;
  text-decoration: none;
  transition: opacity 0.2s;
}
.social-btn:hover { opacity: 0.8; }
.social-x {
  background: #1d9bf0;
  color: #fff;
}
.social-wa {
  background: #25d366;
  color: #fff;
}

/* Transitions */
.fade-enter-active { transition: opacity 0.3s; }
.fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 800px) {
  .create-main {
    flex-direction: column;
    padding: 32px 16px 60px;
  }
  .preview-col {
    width: 100%;
    order: -1;
  }
  .preview-sticky { position: static; }
  .page-title { font-size: 24px; }
  .action-row { flex-direction: column; }
  .nav { padding: 0 16px; }
}
</style>
