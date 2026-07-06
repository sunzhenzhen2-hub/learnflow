/**
 * LearnFlow API Client for uni-app
 * Uses uni.request instead of Axios
 */

const BASE_URL = 'http://localhost:8001/api'

function getToken() {
  return uni.getStorageSync('token') || ''
}

function request(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': getToken() ? `Bearer ${getToken()}` : '',
      },
      timeout: 60000,
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve({ data: res.data, status: res.statusCode })
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.showToast({ title: '登录已过期', icon: 'none' })
          reject(new Error('Unauthorized'))
        } else {
          reject(new Error(res.data?.detail || `HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(new Error(err.errMsg || 'Network error'))
      }
    })
  })
}

// Plans API
export const planApi = {
  list: () => request('/plans/'),
  get: (id) => request(`/plans/${id}`),
  create: (data) => request('/plans/', 'POST', data),
  wizardCreate: (data) => request('/plans/wizard', 'POST', data),
  delete: (id) => request(`/plans/${id}`, 'DELETE'),
  getSteps: (id, week = null) => request(`/plans/${id}/steps${week ? `?week=${week}` : ''}`),
  getMilestones: (id) => request(`/plans/${id}/milestones`),
}

// Steps API
export const stepApi = {
  getToday: () => request('/steps/today'),
  get: (id) => request(`/steps/${id}`),
  start: (id) => request(`/steps/${id}/start`, 'POST'),
  submitOutput: (id, content) => request(`/steps/${id}/submit-output`, 'POST', { content }),
  complete: (id) => request(`/steps/${id}/complete`, 'POST'),
}

// Review API
export const reviewApi = {
  review: (id) => request(`/review/${id}/review`, 'POST'),
  retry: (id) => request(`/review/${id}/review-retry`, 'POST'),
}

// Reminders API
export const reminderApi = {
  list: (planId) => request(`/reminders/plan/${planId}`),
  add: (planId, data) => request(`/reminders/plan/${planId}`, 'POST', data),
  toggle: (id) => request(`/reminders/${id}/toggle`, 'PUT'),
  delete: (id) => request(`/reminders/${id}`, 'DELETE'),
  test: (id) => request(`/reminders/${id}/test`, 'POST'),
}

// Achievements API
export const achievementApi = {
  list: (planId) => request(`/achievements/plan/${planId}`),
}

// Config API
export const configApi = {
  get: () => request('/llm-config'),
  update: (data) => request('/llm-config', 'PUT', data),
}

// Dashboard API
export const dashboardApi = {
  get: () => request('/dashboard'),
}

// Profile API
export const profileApi = {
  get: () => request('/profile/'),
}

// Auth API (WeChat mini program login)
export const authApi = {
  wxLogin: (code) => request('/auth/wx-login', 'POST', { code }),
  devLogin: () => request('/auth/dev-login', 'POST'),
}

export default { planApi, stepApi, reviewApi, reminderApi, achievementApi, configApi, dashboardApi, profileApi, authApi }
