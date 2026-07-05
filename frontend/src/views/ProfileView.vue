<template>
  <div class="profile-view">
    <!-- Header Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: #ecf5ff;">
          <el-icon color="#409eff" :size="24"><Folder /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.total_plans }}</div>
          <div class="stat-label">{{ $t('profile.totalPlans') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #f0f9eb;">
          <el-icon color="#67c23a" :size="24"><CircleCheckFilled /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.completed_steps }}</div>
          <div class="stat-label">{{ $t('profile.completedSteps') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fdf6ec;">
          <el-icon color="#e6a23c" :size="24"><Timer /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.total_hours }}</div>
          <div class="stat-label">{{ $t('profile.totalHours') }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background: #fef0f0;">
          <el-icon color="#f56c6c" :size="24"><Trophy /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ profile.total_achievements }}</div>
          <div class="stat-label">{{ $t('profile.totalAchievements') }}</div>
        </div>
      </div>
    </div>

    <!-- Streak Card -->
    <div class="card streak-card" v-if="profile.streak_days > 0">
      <div class="streak-content">
        <el-icon :size="32" color="#e6a23c"><Flame /></el-icon>
        <div class="streak-info">
          <div class="streak-value">{{ profile.streak_days }} {{ $t('profile.days') }}</div>
          <div class="streak-label">{{ $t('profile.streakDays') }}</div>
        </div>
      </div>
    </div>

    <!-- Plans Progress -->
    <div class="card" v-if="profile.plans_progress.length > 0">
      <div class="card-header">
        <el-icon><List /></el-icon>
        <span>{{ $t('profile.plansProgress') }}</span>
      </div>
      <div class="plans-list">
        <div
          v-for="plan in profile.plans_progress"
          :key="plan.id"
          class="plan-item"
          @click="$router.push(`/learn/${plan.id}`)"
        >
          <div class="plan-info">
            <span class="plan-topic">{{ plan.topic }}</span>
            <el-tag size="small" :type="planStatusType(plan.status)">{{ planStatusText(plan.status) }}</el-tag>
          </div>
          <el-progress
            :percentage="plan.progress"
            :stroke-width="8"
            :show-text="true"
            style="width: 100%; margin-top: 8px;"
          />
          <div class="plan-meta">
            {{ plan.completed_steps }}/{{ plan.total_steps }} {{ $t('profile.completedSteps') }}
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="card" v-if="profile.recent_completed.length > 0">
      <div class="card-header">
        <el-icon><Clock /></el-icon>
        <span>{{ $t('profile.recentActivity') }}</span>
      </div>
      <div class="activity-list">
        <div
          v-for="item in profile.recent_completed"
          :key="item.id"
          class="activity-item"
        >
          <div class="activity-icon">
            <el-icon color="#67c23a"><CircleCheckFilled /></el-icon>
          </div>
          <div class="activity-info">
            <span class="activity-title">{{ item.title }}</span>
            <span class="activity-meta">
              {{ formatDate(item.completed_at) }}
              <span v-if="item.ai_score" class="score-badge">{{ item.ai_score }}分</span>
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="!loading && profile.total_steps === 0" class="empty-state">
      <el-icon :size="64" color="#c0c4cc"><Reading /></el-icon>
      <p>{{ $t('profile.noActivity') }}</p>
      <el-button type="primary" @click="$router.push('/wizard')">
        {{ $t('dashboard.createFirst') }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { profileApi } from '../api/client'
import dayjs from 'dayjs'

const { t } = useI18n()

const profile = ref({
  total_plans: 0,
  active_plans: 0,
  completed_plans: 0,
  total_steps: 0,
  completed_steps: 0,
  total_hours: 0,
  total_achievements: 0,
  streak_days: 0,
  plans_progress: [],
  recent_completed: [],
})

const loading = ref(true)

const formatDate = (d) => {
  if (!d) return ''
  return dayjs(d).format('MM/DD HH:mm')
}

const planStatusType = (status) => {
  const map = { active: 'success', paused: 'warning', completed: 'info' }
  return map[status] || 'info'
}

const planStatusText = (status) => {
  const map = { active: t('profile.activePlans'), paused: '已暂停', completed: t('profile.completedPlans') }
  return map[status] || status
}

const loadProfile = async () => {
  loading.value = true
  try {
    const { data } = await profileApi.get()
    profile.value = data
  } catch (e) {
    console.error('Failed to load profile:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.profile-view { padding: 0; }

.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info { flex: 1; }
.stat-value { font-size: 22px; font-weight: 700; color: #303133; }
.stat-label { font-size: 12px; color: #909399; margin-top: 2px; }

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

.streak-card {
  background: linear-gradient(135deg, #fdf6ec 0%, #faecd8 100%);
  border: 1px solid #faecd8;
}

.streak-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.streak-info { flex: 1; }
.streak-value { font-size: 24px; font-weight: 700; color: #e6a23c; }
.streak-label { font-size: 13px; color: #909399; }

.plans-list { display: flex; flex-direction: column; gap: 16px; }

.plan-item {
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.plan-item:hover { background: #f5f7fa; }

.plan-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.plan-topic { font-weight: 600; font-size: 14px; }
.plan-meta { font-size: 12px; color: #909399; margin-top: 4px; }

.activity-list { display: flex; flex-direction: column; gap: 12px; }

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 8px;
  background: #f9f9f9;
}

.activity-icon { color: #67c23a; }
.activity-info { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.activity-title { font-size: 14px; font-weight: 500; }
.activity-meta { font-size: 12px; color: #909399; }

.score-badge {
  margin-left: 8px;
  padding: 2px 6px;
  background: #f0f9eb;
  color: #67c23a;
  border-radius: 4px;
  font-size: 11px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  gap: 16px;
  text-align: center;
}

.empty-state p { color: #909399; }

@media (max-width: 480px) {
  .stats-grid {
    gap: 8px;
  }

  .stat-card {
    padding: 12px;
    gap: 8px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-value {
    font-size: 18px;
  }

  .stat-label {
    font-size: 11px;
  }

  .streak-value {
    font-size: 20px;
  }

  .card {
    padding: 12px;
  }
}
</style>
