<template>
  <view class="wizard-page">
    <!-- Progress -->
    <view class="progress-bar">
      <view class="progress" :style="{ width: (step / 4) * 100 + '%' }"></view>
    </view>
    <text class="step-indicator">步骤 {{ step }}/4</text>

    <!-- Step 1: Topic -->
    <view v-if="step === 1" class="wizard-step">
      <text class="step-title">你想学什么？</text>
      <text class="step-desc">输入你想学习的主题或技能</text>
      <input v-model="form.topic" class="form-input" placeholder="例如：React、Python、机器学习" />
      <view class="quick-tags">
        <text class="tag" v-for="t in quickTopics" :key="t" @click="form.topic = t">{{ t }}</text>
      </view>
    </view>

    <!-- Step 2: Goal -->
    <view v-if="step === 2" class="wizard-step">
      <text class="step-title">你的学习目标？</text>
      <text class="step-desc">选择最符合你的学习目标</text>
      <view class="goal-list">
        <view v-for="g in goals" :key="g.value" class="goal-card" :class="{ selected: form.goal === g.value }" @click="form.goal = g.value">
          <text class="goal-name">{{ g.label }}</text>
          <text class="goal-desc">{{ g.desc }}</text>
        </view>
      </view>
    </view>

    <!-- Step 3: Level + Hours -->
    <view v-if="step === 3" class="wizard-step">
      <text class="step-title">你的基础和时间？</text>
      <text class="section-label">当前水平</text>
      <view class="level-group">
        <view v-for="l in levels" :key="l.value" class="level-btn" :class="{ active: form.current_level === l.value }" @click="form.current_level = l.value">
          <text class="level-name">{{ l.label }}</text>
          <text class="level-desc">{{ l.desc }}</text>
        </view>
      </view>
      <text class="section-label">每周可用时间（小时）</text>
      <slider :value="form.weekly_hours" :min="2" :max="30" :step="1" show-value activeColor="#409eff" @change="e => form.weekly_hours = e.detail.value" />
      <text class="hours-label">{{ form.weekly_hours }} 小时/周</text>
    </view>

    <!-- Step 4: Confirm -->
    <view v-if="step === 4" class="wizard-step">
      <text class="step-title">确认计划</text>
      <view class="confirm-card">
        <view class="confirm-row">
          <text class="confirm-label">学习主题</text>
          <text class="confirm-value">{{ form.topic }}</text>
        </view>
        <view class="confirm-row">
          <text class="confirm-label">学习目标</text>
          <text class="confirm-value">{{ goalLabel }}</text>
        </view>
        <view class="confirm-row">
          <text class="confirm-label">当前水平</text>
          <text class="confirm-value">{{ levelLabel }}</text>
        </view>
        <view class="confirm-row">
          <text class="confirm-label">每周时间</text>
          <text class="confirm-value">{{ form.weekly_hours }} 小时</text>
        </view>
      </view>
      <text class="confirm-hint">AI 将为你生成个性化的每日学习计划</text>
    </view>

    <!-- Navigation -->
    <view class="wizard-nav">
      <button v-if="step > 1" class="nav-btn back" @click="step--">上一步</button>
      <view v-else class="nav-placeholder"></view>
      <button v-if="step < 4" class="nav-btn next" :disabled="!canNext" @click="step++">下一步</button>
      <button v-else class="nav-btn create" :loading="creating" @click="createPlan">生成学习计划</button>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { usePlanStore } from '../../stores/plan'

const store = usePlanStore()
const step = ref(1)
const creating = ref(false)

const form = ref({
  topic: '',
  goal: 'systematic',
  current_level: 'beginner',
  weekly_hours: 8,
  preferred_days: [1, 3, 5],
  focus_areas: [],
})

const quickTopics = ['React', 'Python', 'Vue.js', 'TypeScript', '机器学习', '大模型(LLM)']

const goals = [
  { value: 'beginner_intro', label: '入门了解', desc: '快速了解基本概念和术语' },
  { value: 'systematic', label: '系统学习', desc: '系统掌握核心知识体系' },
  { value: 'project_ready', label: '项目实战', desc: '能独立完成实际项目' },
  { value: 'deep_mastery', label: '深度精通', desc: '达到能指导他人的水平' },
]

const levels = [
  { value: 'beginner', label: '零基础', desc: '完全没接触过' },
  { value: 'intermediate', label: '有一些基础', desc: '了解基本概念' },
  { value: 'advanced', label: '有经验', desc: '做过相关项目' },
]

const goalLabel = computed(() => goals.find(g => g.value === form.value.goal)?.label || '')
const levelLabel = computed(() => levels.find(l => l.value === form.value.current_level)?.label || '')
const canNext = computed(() => {
  if (step.value === 1) return form.value.topic.trim().length > 0
  return true
})

async function createPlan() {
  creating.value = true
  try {
    await store.createPlan(form.value)
    uni.showToast({ title: '计划生成成功！', icon: 'success' })
    setTimeout(() => {
      uni.switchTab({ url: '/pages/dashboard/index' })
    }, 1500)
  } catch (e) {
    uni.showToast({ title: '生成失败: ' + (e.message || '未知错误'), icon: 'none' })
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.wizard-page { padding: 24rpx; min-height: 100vh; background: #fff; }
.progress-bar { height: 6rpx; background: #ebeef5; border-radius: 3rpx; margin-bottom: 12rpx; }
.progress { height: 100%; background: #409eff; border-radius: 3rpx; transition: width 0.3s; }
.step-indicator { font-size: 24rpx; color: #909399; display: block; margin-bottom: 32rpx; }
.wizard-step { min-height: 60vh; }
.step-title { font-size: 36rpx; font-weight: 700; color: #303133; display: block; margin-bottom: 12rpx; }
.step-desc { font-size: 26rpx; color: #909399; display: block; margin-bottom: 32rpx; }
.form-input {
  width: 100%; height: 88rpx; border: 2rpx solid #dcdfe6; border-radius: 12rpx;
  padding: 0 24rpx; font-size: 30rpx; box-sizing: border-box;
}
.quick-tags { display: flex; flex-wrap: wrap; gap: 12rpx; margin-top: 20rpx; }
.tag {
  font-size: 26rpx; color: #409eff; background: #ecf5ff;
  padding: 10rpx 24rpx; border-radius: 24rpx; border: 1rpx solid #d9ecff;
}
.goal-list { display: flex; flex-direction: column; gap: 16rpx; }
.goal-card {
  padding: 24rpx; border: 2rpx solid #ebeef5; border-radius: 16rpx;
  transition: all 0.2s;
}
.goal-card.selected { border-color: #409eff; background: #ecf5ff; }
.goal-name { font-size: 30rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 6rpx; }
.goal-desc { font-size: 24rpx; color: #909399; }
.section-label { font-size: 28rpx; font-weight: 600; color: #303133; display: block; margin: 24rpx 0 16rpx; }
.level-group { display: flex; flex-direction: column; gap: 12rpx; }
.level-btn {
  padding: 20rpx; border: 2rpx solid #ebeef5; border-radius: 12rpx;
  display: flex; justify-content: space-between; align-items: center;
}
.level-btn.active { border-color: #409eff; background: #ecf5ff; }
.level-name { font-size: 28rpx; font-weight: 600; color: #303133; }
.level-desc { font-size: 24rpx; color: #909399; }
.hours-label { font-size: 26rpx; color: #409eff; font-weight: 600; text-align: center; display: block; margin-top: 8rpx; }
.confirm-card { background: #f5f7fa; border-radius: 16rpx; padding: 24rpx; margin-top: 16rpx; }
.confirm-row { display: flex; justify-content: space-between; padding: 12rpx 0; border-bottom: 1rpx solid #ebeef5; }
.confirm-row:last-child { border-bottom: none; }
.confirm-label { font-size: 26rpx; color: #909399; }
.confirm-value { font-size: 26rpx; color: #303133; font-weight: 600; }
.confirm-hint { font-size: 24rpx; color: #909399; text-align: center; margin-top: 24rpx; display: block; }
.wizard-nav { display: flex; gap: 16rpx; margin-top: 40rpx; padding-bottom: 40rpx; }
.nav-btn { flex: 1; height: 84rpx; line-height: 84rpx; border-radius: 42rpx; font-size: 30rpx; font-weight: 600; text-align: center; border: none; }
.nav-btn.back { background: #f5f7fa; color: #606266; }
.nav-btn.next { background: #409eff; color: #fff; }
.nav-btn.create { background: linear-gradient(135deg, #409eff, #7c5ce7); color: #fff; }
.nav-btn[disabled] { opacity: 0.5; }
.nav-placeholder { flex: 1; }
</style>
