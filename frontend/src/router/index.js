import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GameView from '../views/GameView.vue'
import CreateView from '../views/CreateView.vue'
import AuthCallback from '../views/AuthCallback.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/game',
    name: 'Game',
    component: GameView,
  },
  {
    path: '/create',
    name: 'Create',
    component: CreateView,
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
