<template>
  <router-view />
</template>

<script setup>
import { useTheme } from './composables/useTheme.js'
// Ensure theme is applied on app mount
useTheme()
</script>

<style>
/* Global reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* ============================================
   THEME: DARK (default)
   — Improved contrast: boosted --text2 and --border
   ============================================ */
html[data-theme="dark"],
html:not([data-theme]) {
  --bg: #06060f;
  --surface: #111127;
  --surface2: #181838;
  --border: rgba(255,255,255,0.1);
  --cyan: #00e5ff;
  --gold: #ffd740;
  --purple: #c06cff;
  --green: #69f0ae;
  --red: #ff5252;
  --text: #e0e0e0;
  --text2: rgba(255,255,255,0.6);
  --heading: #ffffff;
  --mono: 'JetBrains Mono', monospace;
  --sans: 'Space Grotesk', 'JetBrains Mono', monospace;

  /* Theme-toggle icon */
  --toggle-icon: '\263E'; /* moon */
}

/* ============================================
   THEME: LIGHT
   ============================================ */
html[data-theme="light"] {
  --bg: #ffffff;
  --surface: #ffffff;
  --surface2: #eaeaf0;
  --border: rgba(0,0,0,0.1);
  --cyan: #0097a7;
  --gold: #b8860b;
  --purple: #7b2ff2;
  --green: #2e7d32;
  --red: #c62828;
  --text: #1a1a2e;
  --text2: rgba(0,0,0,0.55);
  --heading: #0d0d1a;
  --mono: 'JetBrains Mono', monospace;
  --sans: 'Space Grotesk', 'JetBrains Mono', monospace;

  --toggle-icon: '\2600'; /* sun */
}

#app {
  font-family: var(--mono);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text);
  background-color: var(--bg);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: var(--surface);
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text2);
}

/* Global button reset */
button {
  font-family: inherit;
}

/* ---- Theme toggle button (shared style) ---- */
.theme-toggle {
  background: none;
  border: 1px solid var(--border);
  color: var(--text2);
  font-size: 16px;
  width: 34px;
  height: 34px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.theme-toggle:hover {
  color: var(--cyan);
  border-color: var(--cyan);
}
</style>
