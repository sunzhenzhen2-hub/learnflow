import { defineStore } from 'pinia'
import { dashboardApi, planApi, stepApi } from '../api/client'

export const usePlanStore = defineStore('plan', {
  state: () => ({
    activePlan: null,
    todayStep: null,
    upcomingSteps: [],
    milestones: [],
    achievements: [],
    streakDays: 0,
    totalCompleted: 0,
    totalSteps: 0,
    loading: false,
  }),

  actions: {
    async fetchDashboard() {
      this.loading = true
      try {
        const { data } = await dashboardApi.get()
        this.activePlan = data.active_plan
        this.todayStep = data.today_step
        this.upcomingSteps = data.upcoming_steps
        this.milestones = data.milestones
        this.achievements = data.achievements || []
        this.streakDays = data.streak_days
        this.totalCompleted = data.total_completed
        this.totalSteps = data.total_steps
      } catch (e) {
        console.error('Failed to fetch dashboard:', e)
      } finally {
        this.loading = false
      }
    },

    async fetchTodayStep() {
      try {
        const { data } = await stepApi.getToday()
        this.todayStep = data
      } catch (e) {
        console.error('Failed to fetch today step:', e)
      }
    },

    async createPlan(wizardData) {
      const { data } = await planApi.wizardCreate(wizardData)
      this.activePlan = data
      return data
    },
  },
})
