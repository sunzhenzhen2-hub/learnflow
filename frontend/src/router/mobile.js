// 移动端路由配置（不包含配置管理相关路由）
const mobileRoutes = [
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/wizard',
    name: 'Wizard',
    component: () => import('../views/PlanWizard.vue'),
  },
  {
    path: '/learn/:planId',
    name: 'Learn',
    component: () => import('../views/LearningView.vue'),
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
  },
]

export default mobileRoutes
