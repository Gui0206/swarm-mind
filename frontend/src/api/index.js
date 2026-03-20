import axios from 'axios'

const STORAGE_KEY = 'openrouter_user_key'

// Detect system language once at startup (URL ?lang= override supported)
const urlLang = new URLSearchParams(window.location.search).get('lang')
const systemLang = urlLang || navigator.language || navigator.userLanguage || 'en'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:5001' : ''),
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Attach user BYOK key and system language on every request
service.interceptors.request.use(
  config => {
    const key = localStorage.getItem(STORAGE_KEY)
    if (key) {
      config.headers['X-User-LLM-Key'] = key
    }
    config.headers['Accept-Language'] = systemLang
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor — detect 402 quota exceeded
service.interceptors.response.use(
  response => {
    const res = response.data

    if (!res.success && res.success !== undefined) {
      console.error('API Error:', res.error || res.message || 'Unknown error')
      return Promise.reject(new Error(res.error || res.message || 'Error'))
    }

    return res
  },
  error => {
    console.error('Response error:', error)

    // Emit a global event when the server returns 402 (quota exceeded)
    if (error.response?.status === 402) {
      window.dispatchEvent(new CustomEvent('quota-exceeded'))
    }

    if (error.code === 'ECONNABORTED' && error.message.includes('timeout')) {
      console.error('Request timeout')
    }

    if (error.message === 'Network Error') {
      console.error('Network error - please check your connection')
    }

    return Promise.reject(error)
  }
)

export const requestWithRetry = async (requestFn, maxRetries = 3, delay = 1000) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await requestFn()
    } catch (error) {
      if (i === maxRetries - 1) throw error
      console.warn(`Request failed, retrying (${i + 1}/${maxRetries})...`)
      await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
    }
  }
}

export default service
