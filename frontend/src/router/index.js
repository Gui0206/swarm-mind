import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import GameView from '../views/GameView.vue'
import CreateView from '../views/CreateView.vue'

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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
