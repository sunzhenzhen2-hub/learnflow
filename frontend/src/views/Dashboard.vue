<template>
  <div class="dashboard">
    <div v-if="!store.activePlan" class="empty-state">
      <el-icon :size="64" color="#409eff"><Reading /></el-icon>
      <h2>{{ $t('dashboard.welcome') }}</h2>
      <p>{{ $t('dashboard.subtitle') }}</p>
      <el-button type="primary" size="large" @click="$router.push('/wizard')">
        {{ $t('dashboard.createFirst') }}
      </el-button>
    </div>

    <div v-else>
      <div class="card progress-card">
        <div class="progress-header">
          <h3>{{ store.activePlan.topic }}</h3>
          <el-tag :type="statusType">{{ store.activePlan.status }}</el-tag>
        </div>
        <el-progress
          :percentage="store.activePlan.progress"
          :stroke-width="12"
          striped
          striped-flow
        />
        <div class="stats-row">
          <div class="stat">
            <span class="stat-value">{{ store.streakDays }}</span>
            <span class="stat-label">{{ $t('dashboard.dayStreak') }}</span>
          </div>
          <div class="stat">
            <span class="stat-value">{{ store.totalCompleted }}/{{ store.totalSteps }}</span>
            <span class="stat-label">{{ $t('dashboard.stepsDone') }}</span>
          </div>
          <div class="stat">
            <span class="stat-value">W{{ currentWeek }}</span>
            <span class="stat-label">{{ $t('dashboard.currentWeek') }}</span>
          </div>
        </div>
      </div>

      <div class="card today-card" v-if="store.todayStep">
        <div class="card-header">
          <el-icon><Calendar /></el-icon>
          <span>{{ $t('dashboard.todayTask') }}</span>
          <el-tag v-if="store.todayStep.ladder_name" size="small" type="info" effect="plain" class="ladder-badge">
            {{ $t('learning.ladderLevel') }}: {{ store.todayStep.ladder_name }}
          </el-tag>
        </div>
        <div class="today-content">
          <h4>{{ store.todayStep.title }}</h4>
          <p class="today-meta">
            <el-tag size="small">{{ $t('learning.stepTypes.' + store.todayStep.step_type) }}</el-tag>
            <span>{{ store.todayStep.duration_minutes }} {{ $t('dashboard.min') }}</span>
          </p>
          <div v-if="store.todayStep.core_20_percent" class="core20-highlight">
            <strong>{{ $t('learning.core20') }}:</strong> {{ store.todayStep.core_20_percent }}
          </div>
          <p class="today-desc">{{ store.todayStep.content }}</p>
          <el-button
            type="primary"
            @click="startTodayStep"
            :disabled="store.todayStep.status === 'completed'"
          >
            {{ store.todayStep.status === 'completed' ? $t('dashboard.completed') : $t('dashboard.startLearning') }}
          </el-button>
        </div>
      </div>

      <div class="card" v-if="store.upcomingSteps.length > 0">
        <div class="card-header">
          <el-icon><Clock /></el-icon>
          <span>{{ $t('dashboard.upcoming') }}</span>
        </div>
        <div class="step-list">
          <div
            v-for="step in store.upcomingSteps"
            :key="step.id"
            class="step-item"
            :class="{ completed: step.status === 'completed' }"
          >
            <div class="step-date">{{ formatDate(step.date) }}</div>
            <div class="step-info">
              <span class="step-title">{{ step.title }}</span>
              <el-tag size="small" :type="stepTypeTag(step.step_type)">
                {{ $t('learning.stepTypes.' + step.step_type) }}
              </el-tag>
            </div>
            <el-icon v-if="step.status === 'completed'" color="#67c23a">
              <CircleCheckFilled />
            </el-icon>
          </div>
        </div>
      </div>

      <div class="card" v-if="store.milestones.length > 0">
        <div class="card-header">
          <el-icon><Trophy /></el-icon>
          <span>{{ $t('dashboard.milestones') }}</span>
        </div>
        <div class="milestone-list">
          <div
            v-for="ms in store.milestones"
            :key="ms.id"
            class="milestone-item"
            :class="{ completed: ms.status === 'completed' }"
          >
            <div class="milestone-icon">
              <el-icon v-if="ms.status === 'completed'" color="#67c23a"><CircleCheckFilled /></el-icon>
              <el-icon v-else color="#e6a23c"><Clock /></el-icon>
            </div>
            <div class="milestone-info">
              <span class="milestone-title">{{ $t('dashboard.week', { week: ms.week_num }) }}: {{ ms.title }}</span>
              <span class="milestone-desc">{{ ms.description }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Achievements -->
      <div class="card" v-if="store.achievements.length > 0">
        <div class="card-header">
          <el-icon><Medal /></el-icon>
          <span>{{ $t('dashboard.achievements') }}</span>
          <el-tag size="small" type="warning">{{ store.achievements.length }}</el-tag>
        </div>
        <div class="achievement-list">
          <div
            v-for="a in store.achievements"
            :key="a.id"
            class="achievement-item"
            :class="a.rarity"
          >
            <div class="achievement-icon">
              <el-icon :size="28"><component :is="a.icon" /></el-icon>
            </div>
            <div class="achievement-info">
              <span class="achievement-title">{{ a.title }}</span>
              <span class="achievement-desc">{{ a.description }}</span>
            </div>
            <el-tag size="small" :type="rarityType(a.rarity)">{{ rarityLabel(a.rarity) }}</el-tag>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { usePlanStore } from '../stores/plan'
import { stepApi } from '../api/client'
import dayjs from 'dayjs'

const router = useRouter()
const store = usePlanStore()

const currentWeek = computed(() => {
  if (!store.activePlan) return 0
  const start = dayjs(store.activePlan.created_at)
  const now = dayjs()
  return now.diff(start, 'week') + 1
})

const statusType = computed(() => {
  const s = store.activePlan?.status
  return s === 'active' ? 'success' : s === 'paused' ? 'warning' : 'info'
})

const formatDate = (date) => dayjs(date).format('MM/DD ddd')

const stepTypeTag = (type) => {
  const map = { study: '', project: 'success', deep_project: 'warning', output: 'danger', cheat_sheet: 'warning', test: 'info' }
  return map[type] || ''
}

const rarityType = (r) => ({ common: 'info', rare: '', epic: 'warning', legendary: 'danger' }[r] || 'info')
const rarityLabel = (r) => ({ common: '普通', rare: '稀有', epic: '史诗', legendary: '传说' }[r] || r)

const startTodayStep = async () => {
  if (!store.todayStep) return
  try {
    await stepApi.start(store.todayStep.id)
    router.push(`/learn/${store.activePlan.id}`)
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  store.fetchDashboard()
})
</script>

<style scoped>
.dashboard { padding: 0; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 16px;
  text-align: center;
}

.empty-state h2 { font-size: 24px; color: #303133; }
.empty-state p { color: #909399; }

.card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #606266;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-header h3 { font-size: 18px; }

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value { font-size: 20px; font-weight: 700; color: #409eff; }
.stat-label { font-size: 12px; color: #909399; }

.today-content h4 { font-size: 16px; margin-bottom: 8px; }

.today-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: #909399;
  font-size: 14px;
}

.today-desc { color: #606266; font-size: 14px; margin-bottom: 12px; line-height: 1.6; }

.ladder-badge { margin-left: auto; }

.core20-highlight {
  background: linear-gradient(135deg, #fff7e6 0%, #fff3cd 100%);
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 13px;
  color: #606266;
  border-left: 3px solid #e6a23c;
}

.step-list { display: flex; flex-direction: column; gap: 8px; }

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  background: #f9f9f9;
}

.step-item.completed { opacity: 0.6; }

.step-date { font-size: 12px; color: #909399; min-width: 60px; }

.step-info { flex: 1; display: flex; align-items: center; gap: 8px; }
.step-title { font-size: 14px; }

.milestone-list { display: flex; flex-direction: column; gap: 12px; }

.milestone-item { display: flex; align-items: flex-start; gap: 12px; }

.milestone-info { display: flex; flex-direction: column; gap: 4px; }
.milestone-title { font-weight: 600; font-size: 14px; }
.milestone-desc { font-size: 12px; color: #909399; }

.achievement-list { display: flex; flex-direction: column; gap: 10px; }
.achievement-item { display: flex; align-items: center; gap: 12px; padding: 10px; border-radius: 8px; background: #f9f9f9; }
.achievement-item.rare { background: #ecf5ff; }
.achievement-item.epic { background: #fdf6ec; }
.achievement-item.legendary { background: #fef0f0; }
.achievement-icon { color: #e6a23c; }
.achievement-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.achievement-title { font-weight: 600; font-size: 14px; }
.achievement-desc { font-size: 12px; color: #909399; }

@media (max-width: 480px) {
  .stats-row {
    gap: 8px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .today-content h4 {
    font-size: 15px;
  }

  .step-item {
    flex-wrap: wrap;
    gap: 6px;
  }

  .step-date {
    min-width: auto;
    font-size: 11px;
  }

  .milestone-item {
    gap: 8px;
  }

  .achievement-item {
    flex-wrap: wrap;
    gap: 8px;
  }

  .card {
    padding: 12px;
  }
}
</style>
