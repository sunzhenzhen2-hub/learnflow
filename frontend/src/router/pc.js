// PC 端路由配置（包含配置管理相关路由）
const pcRoutes = [
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
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
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
