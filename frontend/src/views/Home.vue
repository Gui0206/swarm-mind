<template>
  <div class="home">
    <nav class="nav">
      <span class="nav-brand">SWARM MIND</span>
      <div class="nav-right">
        <button class="theme-toggle" @click="toggle" :title="theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'">
          {{ theme === 'dark' ? '\u2600' : '\u263E' }}
        </button>
      </div>
    </nav>

    <main class="hero">
      <div class="hero-content">
        <p class="hero-tag">LLM Agent Game</p>
        <h1 class="hero-title">
          Whisper to the swarm.<br />
          <span class="gradient">Shape reality.</span>
        </h1>
        <p class="hero-desc">
          You're a hidden manipulator in a room of AI agents. Each has a unique personality,
          opinions, and goals. <strong>Whisper</strong> to any agent to steer the conversation
          and achieve your <strong>secret objective</strong> before rounds run out.
        </p>

        <div class="hero-btns">
          <router-link to="/game" class="play-btn">
            PLAY NOW
          </router-link>
          <router-link to="/create" class="create-btn">
            CREATE YOUR OWN
          </router-link>
        </div>

        <a href="https://github.com/Gui0206/swarm-mind" target="_blank" class="github-btn">Star on GitHub</a>

        <div class="features">
          <div class="feat">
            <span class="feat-num">6</span>
            <span class="feat-label">Scenarios</span>
          </div>
          <div class="feat">
            <span class="feat-num">36</span>
            <span class="feat-label">Unique Agents</span>
          </div>
          <div class="feat">
            <span class="feat-num">&infin;</span>
            <span class="feat-label">Replayability</span>
          </div>
        </div>
      </div>

      <div class="hero-side">
        <div class="card-stack">
          <div class="scenario-preview">
            <div class="sp-label">SCENARIO</div>
            <div class="sp-title">The Pineapple Ultimatum</div>
            <div class="sp-desc">Convince the entire office that pineapple pizza is the way to go.</div>
            <div class="sp-agents">
              <span>&#x1F454;</span><span>&#x1F3A8;</span><span>&#x1F4AA;</span>
              <span>&#x1F4CA;</span><span>&#x1F468;&#x200D;&#x1F373;</span><span>&#x1F634;</span>
            </div>
          </div>
          <div class="scenario-preview sp2">
            <div class="sp-label">SCENARIO</div>
            <div class="sp-title">Operation: Flat Earth</div>
            <div class="sp-desc">Make scientists doubt the shape of the Earth at a cocktail party.</div>
            <div class="sp-agents">
              <span>&#x1F52D;</span><span>&#x1F30D;</span><span>&#x1F9EA;</span>
              <span>&#x1F4BB;</span><span>&#x1F4E1;</span><span>&#x1F393;</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <section class="how">
      <h2 class="how-title">How It Works</h2>
      <div class="steps">
        <div class="step">
          <span class="step-n">01</span>
          <div class="step-t">Choose a Scenario</div>
          <div class="step-d">Pick a mission with unique agents and a secret objective.</div>
        </div>
        <div class="step">
          <span class="step-n">02</span>
          <div class="step-t">Observe & Whisper</div>
          <div class="step-d">Watch agents debate, then whisper to one to influence the conversation.</div>
        </div>
        <div class="step">
          <span class="step-n">03</span>
          <div class="step-t">Shape the Outcome</div>
          <div class="step-d">Each agent reacts with real LLM intelligence. Manipulate the swarm mind.</div>
        </div>
        <div class="step">
          <span class="step-n">04</span>
          <div class="step-t">Get Judged</div>
          <div class="step-d">An AI judge scores how well you achieved your objective.</div>
        </div>
      </div>
    </section>

    <footer class="foot">
      <span>Built on <a href="https://github.com/Gui0206/swarm-mind" target="_blank">Swarm Mind</a> multi-agent infrastructure</span>
    </footer>
  </div>
</template>

<script setup>
import { useTheme } from '../composables/useTheme.js'
const { theme, toggle } = useTheme()
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
  font-family: var(--mono);
}

/* Nav */
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.github-btn {
  display: inline-block;
  color: var(--gold);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  padding: 10px 28px;
  border: 1px solid var(--gold);
  border-radius: 6px;
  margin-top: -20px;
  margin-bottom: 40px;
  transition: all 0.2s;
}
.github-btn:hover { filter: brightness(1.2); transform: translateY(-2px); }

/* Hero */
.hero {
  max-width: 1100px;
  margin: 0 auto;
  padding: 80px 40px 60px;
  display: flex;
  gap: 60px;
  align-items: center;
}
.hero-content { flex: 1; }
.hero-side { flex: 0.7; }

.hero-tag {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--cyan);
  margin-bottom: 16px;
  text-transform: uppercase;
}

.hero-title {
  font-family: var(--sans);
  font-size: 44px;
  font-weight: 700;
  line-height: 1.15;
  color: var(--heading);
  margin: 0 0 24px;
}
.gradient {
  background: linear-gradient(90deg, var(--cyan), var(--purple));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 14px;
  line-height: 1.7;
  color: var(--text2);
  max-width: 500px;
  margin-bottom: 32px;
}
.hero-desc strong { color: var(--cyan); }

.hero-btns {
  display: flex;
  gap: 14px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.play-btn {
  display: inline-block;
  background: var(--cyan);
  color: var(--bg);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  padding: 14px 40px;
  border-radius: 6px;
  letter-spacing: 1.5px;
  transition: all 0.2s;
}
.play-btn:hover { opacity: 0.85; transform: translateY(-2px); }

.create-btn {
  display: inline-block;
  background: transparent;
  color: var(--purple);
  text-decoration: none;
  font-family: var(--mono);
  font-size: 14px;
  font-weight: 700;
  padding: 14px 32px;
  border-radius: 6px;
  letter-spacing: 1.5px;
  border: 2px solid var(--purple);
  transition: all 0.2s;
}
.create-btn:hover { background: rgba(192,108,255,0.1); transform: translateY(-2px); }

.features {
  display: flex;
  gap: 32px;
}
.feat { text-align: center; }
.feat-num {
  display: block;
  font-family: var(--sans);
  font-size: 28px;
  font-weight: 700;
  color: var(--heading);
}
.feat-label {
  font-size: 11px;
  color: var(--text2);
  letter-spacing: 0.5px;
}

/* Card Stack */
.card-stack { position: relative; }
.scenario-preview {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 28px 24px;
  max-width: 320px;
}
.sp2 {
  position: absolute;
  top: 30px;
  left: 30px;
  opacity: 0.5;
  z-index: -1;
  transform: rotate(2deg);
}
.sp-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--gold);
  margin-bottom: 10px;
}
.sp-title {
  font-family: var(--sans);
  font-size: 17px;
  font-weight: 700;
  color: var(--heading);
  margin-bottom: 8px;
}
.sp-desc {
  font-size: 12px;
  color: var(--text2);
  line-height: 1.5;
  margin-bottom: 14px;
}
.sp-agents {
  display: flex;
  gap: 8px;
  font-size: 20px;
}

/* How section */
.how {
  max-width: 1100px;
  margin: 0 auto;
  padding: 60px 40px 80px;
  border-top: 1px solid var(--border);
}
.how-title {
  font-family: var(--sans);
  font-size: 24px;
  font-weight: 700;
  color: var(--heading);
  margin: 0 0 32px;
}
.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}
.step {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 24px 20px;
}
.step-n {
  font-size: 11px;
  font-weight: 700;
  color: var(--cyan);
  letter-spacing: 1px;
  margin-bottom: 10px;
  display: block;
}
.step-t {
  font-size: 14px;
  font-weight: 700;
  color: var(--heading);
  margin-bottom: 6px;
}
.step-d {
  font-size: 12px;
  color: var(--text2);
  line-height: 1.5;
}

/* Footer */
.foot {
  text-align: center;
  padding: 24px;
  font-size: 11px;
  color: var(--text2);
  border-top: 1px solid var(--border);
}
.foot a { color: var(--cyan); text-decoration: none; }
.foot a:hover { text-decoration: underline; }

@media (max-width: 800px) {
  .hero { flex-direction: column; padding: 40px 20px; gap: 30px; }
  .hero-side { display: none; }
  .hero-title { font-size: 32px; }
  .hero-desc { max-width: 100%; }
  .steps { grid-template-columns: 1fr 1fr; }
  .nav { padding: 0 16px; }
  .how { padding: 40px 20px 60px; }
  .features { flex-wrap: wrap; gap: 24px; }
  .github-btn { margin-top: 0; margin-bottom: 24px; }
}

@media (max-width: 480px) {
  .hero { padding: 28px 16px; }
  .hero-title { font-size: 26px; }
  .hero-desc { font-size: 13px; }
  .hero-btns { flex-direction: column; }
  .play-btn, .create-btn { text-align: center; padding: 14px 20px; }
  .steps { grid-template-columns: 1fr; }
  .how { padding: 30px 16px 40px; }
  .features { justify-content: center; }
}
</style>
