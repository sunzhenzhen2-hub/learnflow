// PC 端路由配置（包含配置管理相关路由，无需登录）
const pcRoutes = [
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
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: 'llm',
        name: 'AdminLLM',
        component: () => import('../views/admin/LLMConfig.vue'),
      },
      {
        path: 'dingtalk',
        name: 'AdminDingTalk',
        component: () => import('../views/admin/DingTalkConfig.vue'),
      },
      {
        path: 'feishu',
        name: 'AdminFeishu',
        component: () => import('../views/admin/FeishuConfig.vue'),
      },
    ],
  },
]

export default pcRoutes
