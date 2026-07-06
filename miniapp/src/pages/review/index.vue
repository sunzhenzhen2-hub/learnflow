<template>
  <view class="review-page">
    <view class="review-header" :class="passed ? 'passed' : 'failed'">
      <text class="review-icon">{{ passed ? '🎉' : '💪' }}</text>
      <text class="review-title">{{ passed ? '评审通过！' : '需要改进' }}</text>
      <text class="review-score">{{ score }}/100</text>
    </view>

    <view class="review-body" v-if="feedback">
      <text class="section-title">评审反馈</text>
      <text class="feedback-text">{{ feedback }}</text>
    </view>

    <view class="review-body" v-if="suggestions.length">
      <text class="section-title">改进建议</text>
      <view v-for="(s, i) in suggestions" :key="i" class="suggestion-item">
        <text class="suggestion-num">{{ i + 1 }}</text>
        <text class="suggestion-text">{{ s }}</text>
      </view>
    </view>

    <view class="review-body" v-if="socraticQuestion">
      <text class="section-title">苏格拉底追问</text>
      <view class="socratic-card">
        <text class="socratic-text">{{ socraticQuestion }}</text>
      </view>
    </view>

    <view class="review-body" v-if="cheatSheet">
      <text class="section-title">速查表建议</text>
      <text class="cheatsheet-text">{{ cheatSheet }}</text>
    </view>

    <view class="actions">
      <button class="action-btn" @click="goBack">返回学习</button>
    </view>
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const passed = ref(false)
const score = ref(0)
const feedback = ref('')
const suggestions = ref([])
const socraticQuestion = ref('')
const cheatSheet = ref('')

function goBack() {
  uni.navigateBack()
}

onMounted(() => {
  const eventChannel = getCurrentPages()[getCurrentPages().length - 1]
  const opts = eventChannel?.options || eventChannel?.$page?.options || {}
  passed.value = opts.passed === 'true'
  score.value = parseInt(opts.score || '0')
  feedback.value = decodeURIComponent(opts.feedback || '')
  socraticQuestion.value = decodeURIComponent(opts.socratic || '')
  cheatSheet.value = decodeURIComponent(opts.cheatsheet || '')
  try { suggestions.value = JSON.parse(decodeURIComponent(opts.suggestions || '[]')) } catch (e) { suggestions.value = [] }
})
</script>

<style scoped>
.review-page { padding: 24rpx; min-height: 100vh; background: #f5f7fa; }
.review-header { text-align: center; padding: 48rpx 0; border-radius: 20rpx; margin-bottom: 24rpx; }
.review-header.passed { background: linear-gradient(135deg, #67c23a, #85ce61); color: #fff; }
.review-header.failed { background: linear-gradient(135deg, #e6a23c, #ebb563); color: #fff; }
.review-icon { font-size: 80rpx; display: block; }
.review-title { font-size: 36rpx; font-weight: 700; display: block; margin-top: 12rpx; }
.review-score { font-size: 60rpx; font-weight: 800; display: block; margin-top: 8rpx; }
.review-body { background: #fff; border-radius: 16rpx; padding: 24rpx; margin-bottom: 16rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 12rpx; }
.feedback-text { font-size: 28rpx; color: #606266; line-height: 1.8; }
.suggestion-item { display: flex; gap: 12rpx; margin: 12rpx 0; }
.suggestion-num { width: 40rpx; height: 40rpx; line-height: 40rpx; text-align: center; background: #409eff; color: #fff; border-radius: 50%; font-size: 22rpx; flex-shrink: 0; }
.suggestion-text { font-size: 26rpx; color: #606266; line-height: 1.6; flex: 1; }
.socratic-card { background: #ecf5ff; padding: 20rpx; border-radius: 12rpx; border-left: 6rpx solid #409eff; }
.socratic-text { font-size: 28rpx; color: #303133; font-style: italic; line-height: 1.6; }
.cheatsheet-text { font-size: 26rpx; color: #606266; line-height: 1.8; white-space: pre-wrap; }
.actions { margin-top: 32rpx; }
.action-btn { height: 84rpx; line-height: 84rpx; border-radius: 42rpx; background: #409eff; color: #fff; font-size: 30rpx; font-weight: 600; border: none; }
</style>
