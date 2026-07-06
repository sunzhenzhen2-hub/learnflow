import { createRouter, createWebHistory } from 'vue-router'
import mobileRoutes from './router/mobile'
import pcRoutes from './router/pc'

const isMobile = window.innerWidth < 768
const routes = isMobile ? mobileRoutes : pcRoutes

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
