import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Plans
export const planApi = {
  list: () => api.get('/plans/'),
  get: (id) => api.get(`/plans/${id}`),
  create: (data) => api.post('/plans/', data),
  wizardCreate: (data) => api.post('/plans/wizard', data),
  delete: (id) => api.delete(`/plans/${id}`),
  getSteps: (id, week) => api.get(`/plans/${id}/steps`, { params: { week } }),
  getMilestones: (id) => api.get(`/plans/${id}/milestones`),
}

// Steps
export const stepApi = {
  getToday: () => api.get('/steps/today'),
  get: (id) => api.get(`/steps/${id}`),
  start: (id) => api.post(`/steps/${id}/start`),
  submitOutput: (id, content) => api.post(`/steps/${id}/submit-output`, { content }),
  complete: (id) => api.post(`/steps/${id}/complete`),
}

// Review
export const reviewApi = {
  review: (stepId) => api.post(`/review/${stepId}/review`),
  retry: (stepId, content) => api.post(`/review/${stepId}/review-retry`, { content }),
}

// Reminders
export const reminderApi = {
  list: (planId) => api.get(`/reminders/plan/${planId}`),
  add: (planId, data) => api.post(`/reminders/plan/${planId}`, data),
  toggle: (id) => api.put(`/reminders/${id}/toggle`),
  delete: (id) => api.delete(`/reminders/${id}`),
  test: (channel) => api.post(`/reminders/test/${channel}`),
}

// Achievements
export const achievementApi = {
  list: (planId) => api.get(`/achievements/plan/${planId}`),
}

// LLM Config
export const configApi = {
  get: () => api.get('/llm-config'),
  update: (data) => api.put('/llm-config', data),
  models: () => api.get('/llm-models'),
  test: () => api.post('/llm-config/test'),
}

// Dashboard
export const dashboardApi = {
  get: () => api.get('/dashboard'),
}

// Profile
export const profileApi = {
  get: () => api.get('/profile/'),
}

export default api
