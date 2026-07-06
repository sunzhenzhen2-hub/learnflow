// 移动端路由配置（不包含配置管理相关路由，无需登录）
const mobileRoutes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/wizard',
    name: 'Wizard',
    component: () => import('../views/PlanWizard.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/learn/:planId',
    name: 'Learn',
    component: () => import('../views/LearningView.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: false },
  },
]

export default mobileRoutes
