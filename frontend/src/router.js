import { createRouter, createWebHistory } from 'vue-router'
import mobileRoutes from './router/mobile'
import pcRoutes from './router/pc'

// 根据设备类型选择路由配置
const isMobile = window.innerWidth < 768
const routes = isMobile ? mobileRoutes : pcRoutes

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
