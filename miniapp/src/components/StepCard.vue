<template>
  <view class="step-card" :class="{ locked: step.locked, active: isActive, completed: step.status === 'completed' }" @click="$emit('select', step)">
    <view class="step-icon">
      <text v-if="step.locked" class="icon-text">🔒</text>
      <text v-else-if="step.status === 'completed'" class="icon-text">✅</text>
      <text v-else-if="step.status === 'in_progress'" class="icon-text">⏳</text>
      <text v-else class="icon-text">○</text>
    </view>
    <view class="step-content">
      <view class="step-header">
        <text v-if="step.ladder_name" class="ladder-tag">{{ step.ladder_name }}</text>
        <text class="step-title">{{ step.title }}</text>
      </view>
      <view class="step-meta">
        <text class="type-tag" :class="step.step_type">{{ typeLabel }}</text>
        <text class="meta-text">{{ step.duration_minutes }}分钟</text>
        <text class="meta-text">{{ formatDate }}</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  step: { type: Object, required: true },
  isActive: { type: Boolean, default: false },
})

defineEmits(['select'])

const TYPE_LABELS = {
  study: '系统学习', project: '动手实践', deep_project: '深度实战',
  output: '总结输出', cheat_sheet: '速查表', test: '知识测试',
}

const typeLabel = computed(() => TYPE_LABELS[props.step.step_type] || props.step.step_type)
const formatDate = computed(() => dayjs(props.step.date).format('MM/DD'))
</script>

<style scoped>
.step-card {
  display: flex; align-items: center; gap: 20rpx; padding: 24rpx;
  background: #fff; border-radius: 16rpx; margin-bottom: 16rpx;
  border: 2rpx solid transparent; transition: all 0.2s;
}
.step-card.active { border-color: #409eff; background: #ecf5ff; }
.step-card.locked { opacity: 0.5; }
.step-card.completed { background: #f0f9eb; }
.step-icon { width: 60rpx; text-align: center; }
.icon-text { font-size: 36rpx; }
.step-content { flex: 1; }
.step-header { display: flex; align-items: center; gap: 12rpx; flex-wrap: wrap; margin-bottom: 8rpx; }
.ladder-tag {
  font-size: 20rpx; color: #909399; background: #f4f4f5;
  padding: 2rpx 12rpx; border-radius: 6rpx; border: 1rpx solid #dcdfe6;
}
.step-title { font-size: 28rpx; font-weight: 600; color: #303133; }
.step-meta { display: flex; align-items: center; gap: 12rpx; }
.type-tag {
  font-size: 22rpx; padding: 2rpx 12rpx; border-radius: 6rpx;
  background: #e8f4ff; color: #409eff;
}
.type-tag.project { background: #e8f8e8; color: #67c23a; }
.type-tag.output { background: #fef0f0; color: #f56c6c; }
.meta-text { font-size: 22rpx; color: #909399; }
</style>
