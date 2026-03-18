import { ref, watchEffect } from 'vue'

const theme = ref(localStorage.getItem('swarm-theme') || 'dark')

function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t)
}

// Apply on first import
if (typeof document !== 'undefined') {
  applyTheme(theme.value)
}

watchEffect(() => {
  localStorage.setItem('swarm-theme', theme.value)
  if (typeof document !== 'undefined') {
    applyTheme(theme.value)
  }
})

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
  }

  return { theme, toggle }
}
