<template>
  <view class="profile-page">
    <!-- User Card -->
    <view class="user-card">
      <view class="avatar-area">
        <view class="avatar">
          <text class="avatar-text">📚</text>
        </view>
        <view class="user-info">
          <text class="user-name">LearnFlow 学习者</text>
          <text class="user-desc">AI 驱动的学习执行系统</text>
        </view>
      </view>
    </view>

    <!-- Stats -->
    <view class="stats-row">
      <view class="stat-item">
        <text class="stat-num">{{ profile.total_completed || 0 }}</text>
        <text class="stat-label">已完成</text>
      </view>
      <view class="stat-item">
        <text class="stat-num">{{ profile.streak_days || 0 }}</text>
        <text class="stat-label">连续天数</text>
      </view>
      <view class="stat-item">
        <text class="stat-num">{{ profile.total_plans || 0 }}</text>
        <text class="stat-label">学习计划</text>
      </view>
      <view class="stat-item">
        <text class="stat-num">{{ profile.achievements_count || 0 }}</text>
        <text class="stat-label">成就</text>
      </view>
    </view>

    <!-- Streak Card -->
    <view class="streak-card" v-if="profile.streak_days > 0">
      <text class="streak-fire">🔥</text>
      <view class="streak-info">
        <text class="streak-num">{{ profile.streak_days }} 天</text>
        <text class="streak-text">连续学习</text>
      </view>
    </view>

    <!-- Active Plan -->
    <view class="section" v-if="activePlan">
      <text class="section-title">当前计划</text>
      <view class="plan-card" @click="goToLearn">
        <text class="plan-topic">{{ activePlan.topic }}</text>
        <view class="plan-progress">
          <view class="progress-bar">
            <view class="progress" :style="{ width: progressPercent + '%' }"></view>
          </view>
          <text class="progress-text">{{ progressPercent }}%</text>
        </view>
        <view class="plan-meta">
          <text>{{ activePlan.total_weeks }}周计划</text>
          <text>{{ activePlan.weekly_hours }}小时/周</text>
        </view>
      </view>
    </view>

    <!-- Achievements -->
    <view class="section" v-if="achievements.length">
      <text class="section-title">成就徽章</text>
      <view class="achievement-grid">
        <view v-for="a in achievements" :key="a.badge_key" class="achievement-item" :class="a.rarity">
          <text class="achievement-icon">{{ rarityIcon(a.rarity) }}</text>
          <text class="achievement-name">{{ a.title }}</text>
        </view>
      </view>
    </view>

    <!-- Menu -->
    <view class="section">
      <view class="menu-item" @click="goToSettings">
        <text class="menu-icon">⚙️</text>
        <text class="menu-text">设置</text>
        <text class="menu-arrow">→</text>
      </view>
      <view class="menu-item" @click="goToLearn">
        <text class="menu-icon">📖</text>
        <text class="menu-text">进入学习</text>
        <text class="menu-arrow">→</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { profileApi, planApi, achievementApi } from '../../api/client'

const profile = ref({})
const activePlan = ref(null)
const achievements = ref([])

const progressPercent = computed(() => {
  if (!activePlan.value) return 0
  return Math.round((activePlan.value.progress || 0) * 100)
})

function rarityIcon(rarity) {
  return { common: '🏅', rare: '🏆', epic: '💎', legendary: '👑' }[rarity] || '🏅'
}

function goToLearn() {
  if (activePlan.value) {
    uni.navigateTo({ url: `/pages/learn/index?planId=${activePlan.value.id}` })
  }
}

function goToSettings() {
  uni.navigateTo({ url: '/pages/settings/index' })
}

onMounted(async () => {
  try {
    const { data } = await profileApi.get()
    profile.value = data
    if (data.active_plan) activePlan.value = data.active_plan
  } catch (e) {
    console.error('Profile load failed:', e)
  }
  // Load plans for active plan
  try {
    const { data } = await planApi.list()
    if (data.length > 0) {
      activePlan.value = data.find(p => p.status === 'active') || data[0]
      // Load achievements
      if (activePlan.value) {
        const achRes = await achievementApi.list(activePlan.value.id)
        achievements.value = achRes.data || []
      }
    }
  } catch (e) {
    console.error('Plans load failed:', e)
  }
})
</script>

<style scoped>
.profile-page { padding: 0 24rpx 24rpx; }
.user-card { padding: 32rpx 0 16rpx; margin-top: env(safe-area-inset-top, 88rpx); }
.avatar-area { display: flex; align-items: center; gap: 20rpx; }
.avatar { width: 96rpx; height: 96rpx; border-radius: 50%; background: linear-gradient(135deg, #409eff, #7c5ce7); display: flex; align-items: center; justify-content: center; }
.avatar-text { font-size: 48rpx; }
.user-name { font-size: 34rpx; font-weight: 700; color: #303133; display: block; }
.user-desc { font-size: 24rpx; color: #909399; }
.stats-row { display: flex; background: #fff; border-radius: 16rpx; padding: 24rpx 0; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); margin: 16rpx 0; }
.stat-item { flex: 1; text-align: center; }
.stat-num { font-size: 40rpx; font-weight: 700; color: #409eff; display: block; }
.stat-label { font-size: 22rpx; color: #909399; margin-top: 4rpx; }
.streak-card { display: flex; align-items: center; gap: 20rpx; background: linear-gradient(135deg, #ff9a56, #ff6b6b); border-radius: 16rpx; padding: 24rpx; margin: 16rpx 0; color: #fff; }
.streak-fire { font-size: 48rpx; }
.streak-num { font-size: 36rpx; font-weight: 700; display: block; }
.streak-text { font-size: 24rpx; opacity: 0.9; }
.section { margin-top: 32rpx; }
.section-title { font-size: 30rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 16rpx; }
.plan-card { background: #fff; border-radius: 16rpx; padding: 24rpx; box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.04); }
.plan-topic { font-size: 30rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 16rpx; }
.plan-progress { margin-bottom: 12rpx; }
.progress-bar { height: 12rpx; background: #ebeef5; border-radius: 6rpx; }
.progress { height: 100%; background: linear-gradient(90deg, #409eff, #7c5ce7); border-radius: 6rpx; transition: width 0.3s; }
.progress-text { font-size: 24rpx; color: #409eff; font-weight: 600; margin-top: 6rpx; display: block; text-align: right; }
.plan-meta { display: flex; gap: 16rpx; }
.plan-meta text { font-size: 24rpx; color: #909399; }
.achievement-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16rpx; }
.achievement-item { text-align: center; padding: 16rpx 0; }
.achievement-icon { font-size: 48rpx; display: block; }
.achievement-name { font-size: 20rpx; color: #909399; margin-top: 4rpx; display: block; }
.achievement-item.rare .achievement-name { color: #409eff; }
.achievement-item.epic .achievement-name { color: #e6a23c; }
.achievement-item.legendary .achievement-name { color: #f56c6c; }
.menu-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid #ebeef5; }
.menu-icon { font-size: 36rpx; margin-right: 16rpx; }
.menu-text { flex: 1; font-size: 28rpx; color: #303133; }
.menu-arrow { font-size: 28rpx; color: #c0c4cc; }
</style>
