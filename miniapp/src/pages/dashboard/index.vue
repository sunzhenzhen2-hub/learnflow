<template>
  <view class="dashboard">
    <!-- Header -->
    <view class="header">
      <view class="header-left">
        <text class="greeting">{{ greeting }}</text>
        <text class="sub-text">{{ todayDate }}</text>
      </view>
      <view class="header-right">
        <text class="streak-badge" v-if="store.streakDays > 0">&#x1F525; {{ store.streakDays }}天</text>
      </view>
    </view>

    <!-- Stats Grid -->
    <view class="stats-grid">
      <view class="stat-card">
        <text class="stat-num">{{ store.totalCompleted }}</text>
        <text class="stat-label">已完成</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ store.totalSteps }}</text>
        <text class="stat-label">总步骤</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ store.streakDays }}</text>
        <text class="stat-label">连续天数</text>
      </view>
      <view class="stat-card">
        <text class="stat-num">{{ store.milestones.filter(m => m.status === 'completed').length }}</text>
        <text class="stat-label">里程碑</text>
      </view>
    </view>

    <!-- Today's Task -->
    <view class="section" v-if="store.todayStep">
      <text class="section-title">今日任务</text>
      <view class="today-card" @click="goToLearn">
        <view class="today-info">
          <text class="today-title">{{ store.todayStep.title }}</text>
          <view class="today-meta">
            <text class="type-tag">{{ typeLabel(store.todayStep.step_type) }}</text>
            <text class="duration">{{ store.todayStep.duration_minutes }}分钟</text>
          </view>
          <text class="today-core" v-if="store.todayStep.core_20_percent">
            核心20%: {{ store.todayStep.core_20_percent }}
          </text>
        </view>
        <view class="today-action">
          <text class="action-btn">{{ store.todayStep.status === 'completed' ? '已完成 ✓' : '开始学习 →' }}</text>
        </view>
      </view>
    </view>

    <!-- No Plan Hint -->
    <view class="section" v-if="!store.activePlan && !store.loading">
      <view class="empty-state">
        <text class="empty-icon">&#x1F4DA;</text>
        <text class="empty-text">还没有学习计划</text>
        <view class="create-btn" @click="goToWizard">
          <text class="create-btn-text">创建学习计划</text>
        </view>
      </view>
    </view>

    <!-- Upcoming Steps -->
    <view class="section" v-if="store.upcomingSteps.length">
      <text class="section-title">即将到来</text>
      <view v-for="step in store.upcomingSteps.slice(0, 3)" :key="step.id" class="upcoming-item">
        <text class="upcoming-title">{{ step.title }}</text>
        <text class="upcoming-date">{{ step.date }}</text>
      </view>
    </view>

    <!-- Milestones -->
    <view class="section" v-if="store.milestones.length">
      <text class="section-title">里程碑</text>
      <view v-for="ms in store.milestones" :key="ms.week_num" class="milestone-item" :class="{ completed: ms.status === 'completed' }">
        <text class="milestone-week">W{{ ms.week_num }}</text>
        <text class="milestone-title">{{ ms.title }}</text>
        <text class="milestone-status">{{ ms.status === 'completed' ? '✓' : '○' }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { usePlanStore } from '../../stores/plan'
import dayjs from 'dayjs'

const store = usePlanStore()

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了 &#x1F319;'
  if (hour < 12) return '早上好 ☀️'
  if (hour < 14) return '中午好 &#x1F324;&#xFE0F;'
  if (hour < 18) return '下午好 &#x1F307;'
  return '晚上好 &#x1F319;'
})

const todayDate = computed(() => dayjs().format('YYYY年M月D日 ddd'))

function typeLabel(type) {
  const labels = { study: '系统学习', project: '动手实践', deep_project: '深度实战', output: '总结输出', cheat_sheet: '速查表', test: '知识测试' }
  return labels[type] || type
}

function goToLearn() {
  if (store.activePlan) {
    uni.navigateTo({ url: `/pages/learn/index?planId=${store.activePlan.id}` })
  }
}

function goToWizard() {
  uni.switchTab({ url: '/pages/wizard/index' })
}

onMounted(() => {
  store.fetchDashboard()
})

onPullDownRefresh(() => {
  store.fetchDashboard().then(() => uni.stopPullDownRefresh())
})
</script>

<style scoped>
.dashboard { padding: 0 24rpx 24rpx; }
.header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 24rpx 0 16rpx; margin-top: env(safe-area-inset-top, 88rpx);
}
.greeting { font-size: 40rpx; font-weight: 700; color: #303133; display: block; }
.sub-text { font-size: 24rpx; color: #909399; margin-top: 4rpx; }
.streak-badge {
  font-size: 26rpx; background: linear-gradient(135deg, #ff9a56, #ff6b6b);
  color: #fff; padding: 8rpx 20rpx; border-radius: 24rpx;
}
.stats-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 16rpx; margin: 24rpx 0;
}
.stat-card {
  background: #fff; border-radius: 16rpx; padding: 24rpx; text-align: center;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04);
}
.stat-num { font-size: 44rpx; font-weight: 700; color: #409eff; display: block; }
.stat-label { font-size: 22rpx; color: #909399; margin-top: 4rpx; }
.section { margin-top: 32rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 16rpx; }
.today-card {
  background: linear-gradient(135deg, #409eff 0%, #7c5ce7 100%);
  border-radius: 20rpx; padding: 28rpx; color: #fff;
}
.today-title { font-size: 30rpx; font-weight: 600; display: block; margin-bottom: 12rpx; }
.today-meta { display: flex; gap: 12rpx; margin-bottom: 12rpx; }
.type-tag { font-size: 22rpx; background: rgba(255,255,255,0.2); padding: 4rpx 12rpx; border-radius: 8rpx; }
.duration { font-size: 22rpx; opacity: 0.8; }
.today-core { font-size: 24rpx; opacity: 0.9; line-height: 1.6; }
.today-action { margin-top: 20rpx; text-align: right; }
.action-btn { font-size: 28rpx; font-weight: 600; }
.empty-state { text-align: center; padding: 60rpx 0; }
.empty-icon { font-size: 80rpx; display: block; margin-bottom: 16rpx; }
.empty-text { font-size: 28rpx; color: #909399; display: block; margin-bottom: 24rpx; }
.create-btn {
  display: inline-block; background: #409eff; color: #fff;
  padding: 16rpx 40rpx; border-radius: 32rpx; font-size: 28rpx; font-weight: 600;
}
.upcoming-item {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16rpx 0; border-bottom: 1rpx solid #ebeef5;
}
.upcoming-title { font-size: 26rpx; color: #606266; flex: 1; }
.upcoming-date { font-size: 22rpx; color: #909399; }
.milestone-item {
  display: flex; align-items: center; gap: 16rpx;
  padding: 16rpx 0; border-bottom: 1rpx solid #ebeef5;
}
.milestone-item.completed .milestone-title { color: #67c23a; }
.milestone-week {
  font-size: 22rpx; color: #fff; background: #909399;
  padding: 4rpx 12rpx; border-radius: 8rpx;
}
.milestone-item.completed .milestone-week { background: #67c23a; }
.milestone-title { font-size: 26rpx; color: #606266; flex: 1; }
.milestone-status { font-size: 28rpx; }
</style>
