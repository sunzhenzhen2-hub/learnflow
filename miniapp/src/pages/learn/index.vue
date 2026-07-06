<template>
  <view class="learn-page">
    <!-- Week Navigation -->
    <view class="week-nav">
      <button class="nav-btn" :disabled="currentWeek <= 1" @click="prevWeek">←</button>
      <text class="week-label">第{{ currentWeek }}周</text>
      <button class="nav-btn" :disabled="currentWeek >= totalWeeks" @click="nextWeek">→</button>
    </view>

    <!-- Step List -->
    <scroll-view scroll-y class="step-list" v-if="!showDetail">
      <StepCard
        v-for="step in weekSteps"
        :key="step.id"
        :step="step"
        :isActive="selectedStep?.id === step.id"
        @select="selectStep"
      />
      <view v-if="weekSteps.length === 0" class="empty">
        <text class="empty-text">本周暂无学习步骤</text>
      </view>
    </scroll-view>

    <!-- Step Detail -->
    <scroll-view scroll-y class="step-detail" v-if="showDetail && selectedStep && !selectedStep.locked">
      <!-- Back Button -->
      <view class="detail-header">
        <text class="back-btn" @click="showDetail = false">← 返回</text>
        <text class="detail-title">{{ selectedStep.title }}</text>
      </view>

      <!-- Video Resources -->
      <view class="section" v-if="videoResources.length">
        <text class="section-title">学习资源</text>
        <VideoPlayer
          v-for="(res, i) in videoResources"
          :key="i"
          :url="res.url"
          :embedUrl="res.embed_url"
          :title="res.title"
          :platform="res.platform"
          :duration="res.duration"
        />
      </view>

      <!-- Knowledge Document (Markdown) -->
      <view class="section doc-section" v-if="selectedStep.doc_content">
        <text class="section-title">知识文档</text>
        <MarkdownViewer :content="selectedStep.doc_content" />
      </view>

      <!-- Core 20% -->
      <view class="section core-section" v-if="selectedStep.core_20_percent">
        <text class="section-title">核心20%</text>
        <text class="core-text">{{ selectedStep.core_20_percent }}</text>
      </view>

      <!-- Learning Content -->
      <view class="section" v-if="selectedStep.content">
        <text class="section-title">学习内容</text>
        <text class="content-text">{{ selectedStep.content }}</text>
      </view>

      <!-- Actions -->
      <view class="actions" v-if="selectedStep.status !== 'completed'">
        <button v-if="selectedStep.status === 'available'" class="action-btn primary" @click="startStep">
          开始此步骤
        </button>
        <button v-if="selectedStep.status === 'in_progress' || selectedStep.status === 'review_failed'" class="action-btn success" @click="showOutputDialog = true">
          {{ selectedStep.test_question ? '提交测试答案' : '提交输出接受评审' }}
        </button>
      </view>

      <!-- Completed State -->
      <view v-if="selectedStep.status === 'completed'" class="completed-state">
        <text class="completed-icon">&#x1F389;</text>
        <text class="completed-text">步骤已完成</text>
        <text class="completed-score">得分: {{ selectedStep.ai_score || 'N/A' }}/100</text>
      </view>

      <!-- AI Review Result -->
      <view v-if="selectedStep.ai_review_result" class="review-section">
        <text class="section-title">AI 评审</text>
        <view class="review-card" :class="selectedStep.ai_score >= 70 ? 'passed' : 'failed'">
          <text class="review-status">{{ selectedStep.ai_score >= 70 ? '✓ 通过' : '✗ 需要改进' }}</text>
          <text class="review-feedback">{{ selectedStep.ai_review_result.feedback }}</text>
        </view>
        <view v-if="selectedStep.ai_review_result.suggestions?.length" class="suggestions">
          <text class="sub-title">改进建议：</text>
          <view v-for="(s, i) in selectedStep.ai_review_result.suggestions" :key="i" class="suggestion-item">
            <text>{{ i + 1 }}. {{ s }}</text>
          </view>
        </view>
        <view v-if="selectedStep.ai_review_result.socratic_question" class="socratic">
          <text class="sub-title">苏格拉底追问</text>
          <text class="socratic-text">{{ selectedStep.ai_review_result.socratic_question }}</text>
        </view>
      </view>
    </scroll-view>

    <!-- Output Dialog -->
    <view v-if="showOutputDialog" class="dialog-overlay">
      <view class="dialog-content">
        <text class="dialog-title">{{ selectedStep?.test_question ? '完成知识测试' : '提交学习输出' }}</text>
        <textarea
          v-model="outputContent"
          class="output-input"
          placeholder="写下你的理解... 尽量详细，展示你对核心概念的理解"
          :maxlength="5000"
          auto-height
        />
        <view class="dialog-actions">
          <button class="dialog-btn cancel" @click="showOutputDialog = false">取消</button>
          <button class="dialog-btn submit" :loading="submitting" @click="submitOutput">提交 AI 评审</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { planApi, stepApi, reviewApi } from '../../api/client'
import StepCard from '../../components/StepCard.vue'
import VideoPlayer from '../../components/VideoPlayer.vue'
import MarkdownViewer from '../../components/MarkdownViewer.vue'

const planId = ref(null)
const steps = ref([])
const currentWeek = ref(1)
const totalWeeks = ref(16)
const selectedStep = ref(null)
const showDetail = ref(false)
const showOutputDialog = ref(false)
const outputContent = ref('')
const submitting = ref(false)

const weekSteps = computed(() =>
  steps.value.filter(s => s.week_num === currentWeek.value)
)

const videoResources = computed(() => {
  if (!selectedStep.value?.resources) return []
  return selectedStep.value.resources.filter(r => r.type === 'video')
})

function prevWeek() { if (currentWeek.value > 1) currentWeek.value-- }
function nextWeek() { if (currentWeek.value < totalWeeks.value) currentWeek.value++ }

function selectStep(step) {
  if (!step.locked) {
    selectedStep.value = step
    showDetail.value = true
  }
}

async function loadSteps() {
  if (!planId.value) return
  try {
    const { data } = await planApi.getSteps(planId.value)
    steps.value = data
    const plan = await planApi.get(planId.value)
    totalWeeks.value = plan.data.total_weeks

    // Auto-select today's step
    const today = new Date().toISOString().split('T')[0]
    const todayStep = data.find(s => s.date === today && !s.locked)
    if (todayStep) {
      selectedStep.value = todayStep
      currentWeek.value = todayStep.week_num
    } else {
      const firstAvailable = data.find(s => !s.locked)
      if (firstAvailable) {
        selectedStep.value = firstAvailable
        currentWeek.value = firstAvailable.week_num
      }
    }
  } catch (e) {
    uni.showToast({ title: '加载失败', icon: 'none' })
  }
}

async function startStep() {
  try {
    await stepApi.start(selectedStep.value.id)
    selectedStep.value.status = 'in_progress'
    uni.showToast({ title: '步骤已开始', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '失败: ' + e.message, icon: 'none' })
  }
}

async function submitOutput() {
  if (!outputContent.value.trim()) {
    uni.showToast({ title: '请先写下你的输出', icon: 'none' })
    return
  }
  submitting.value = true
  try {
    await stepApi.submitOutput(selectedStep.value.id, outputContent.value)
    const { data: review } = await reviewApi.review(selectedStep.value.id)

    selectedStep.value.ai_score = review.score
    selectedStep.value.ai_review_result = {
      feedback: review.feedback,
      suggestions: review.suggestions,
      socratic_question: review.socratic_question,
      feynman_score: review.feynman_score,
      feynman_analysis: review.feynman_analysis,
      cheat_sheet: review.cheat_sheet,
    }

    if (review.passed) {
      await stepApi.complete(selectedStep.value.id)
      selectedStep.value.status = 'completed'
      uni.showToast({ title: `通过！得分: ${review.score}/100`, icon: 'success' })
      showOutputDialog.value = false
      outputContent.value = ''
      await loadSteps()
    } else {
      uni.showToast({ title: `得分: ${review.score}/100 - 需要改进`, icon: 'none' })
      showOutputDialog.value = false
    }
  } catch (e) {
    uni.showToast({ title: '评审失败: ' + e.message, icon: 'none' })
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // Get planId from page options
  const pages = getCurrentPages()
  const currentPage = pages[pages.length - 1]
  planId.value = currentPage?.options?.planId || currentPage?.$page?.options?.planId
  if (planId.value) {
    loadSteps()
  }
})

onPullDownRefresh(() => {
  loadSteps().then(() => uni.stopPullDownRefresh())
})

watch(currentWeek, () => {
  showDetail.value = false
  selectedStep.value = null
})
</script>

<style scoped>
.learn-page { height: 100vh; display: flex; flex-direction: column; background: #f5f7fa; }
.week-nav {
  display: flex; align-items: center; justify-content: center; gap: 24rpx;
  padding: 16rpx 24rpx; background: #fff; border-bottom: 1rpx solid #ebeef5;
}
.nav-btn {
  width: 64rpx; height: 64rpx; line-height: 64rpx; text-align: center;
  border-radius: 50%; background: #f5f7fa; font-size: 28rpx; border: none;
}
.nav-btn[disabled] { opacity: 0.3; }
.week-label { font-size: 32rpx; font-weight: 600; color: #303133; min-width: 120rpx; text-align: center; }
.step-list { flex: 1; padding: 16rpx 24rpx; }
.step-detail { flex: 1; padding: 0 24rpx 24rpx; }
.detail-header { padding: 16rpx 0; }
.back-btn { font-size: 28rpx; color: #409eff; display: block; margin-bottom: 12rpx; }
.detail-title { font-size: 34rpx; font-weight: 700; color: #303133; display: block; }
.section { margin-top: 24rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 12rpx; }
.doc-section { background: #f5f7fa; border-radius: 16rpx; padding: 20rpx; border-left: 6rpx solid #67c23a; }
.core-section { background: linear-gradient(135deg, #fff7e6, #fff3cd); border-radius: 16rpx; padding: 20rpx; border-left: 6rpx solid #e6a23c; }
.core-text { font-size: 28rpx; line-height: 1.8; color: #606266; font-weight: 500; }
.content-text { font-size: 28rpx; line-height: 1.8; color: #606266; white-space: pre-wrap; }
.actions { margin-top: 32rpx; display: flex; gap: 16rpx; }
.action-btn { flex: 1; height: 80rpx; line-height: 80rpx; border-radius: 40rpx; font-size: 28rpx; font-weight: 600; text-align: center; border: none; }
.action-btn.primary { background: #409eff; color: #fff; }
.action-btn.success { background: #67c23a; color: #fff; }
.completed-state { text-align: center; padding: 40rpx; }
.completed-icon { font-size: 60rpx; display: block; }
.completed-text { font-size: 32rpx; font-weight: 600; color: #67c23a; display: block; margin-top: 12rpx; }
.completed-score { font-size: 26rpx; color: #909399; }
.review-section { margin-top: 32rpx; }
.review-card { padding: 20rpx; border-radius: 12rpx; margin-bottom: 16rpx; }
.review-card.passed { background: #f0f9eb; border-left: 6rpx solid #67c23a; }
.review-card.failed { background: #fdf6ec; border-left: 6rpx solid #e6a23c; }
.review-status { font-size: 28rpx; font-weight: 600; display: block; margin-bottom: 8rpx; }
.review-feedback { font-size: 26rpx; color: #606266; line-height: 1.6; }
.sub-title { font-size: 26rpx; font-weight: 600; color: #303133; display: block; margin: 16rpx 0 8rpx; }
.suggestion-item { font-size: 26rpx; color: #606266; margin: 6rpx 0; padding-left: 16rpx; }
.socratic { background: #ecf5ff; padding: 16rpx; border-radius: 12rpx; border-left: 6rpx solid #409eff; }
.socratic-text { font-size: 26rpx; color: #303133; font-style: italic; line-height: 1.6; }
.empty { text-align: center; padding: 80rpx 0; }
.empty-text { font-size: 28rpx; color: #909399; }
/* Dialog */
.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center;
  z-index: 999;
}
.dialog-content {
  width: 85%; background: #fff; border-radius: 20rpx; padding: 32rpx;
}
.dialog-title { font-size: 32rpx; font-weight: 600; display: block; margin-bottom: 16rpx; }
.output-input {
  width: 100%; min-height: 300rpx; border: 1rpx solid #dcdfe6; border-radius: 12rpx;
  padding: 16rpx; font-size: 28rpx; box-sizing: border-box;
}
.dialog-actions { display: flex; gap: 16rpx; margin-top: 24rpx; }
.dialog-btn { flex: 1; height: 72rpx; line-height: 72rpx; border-radius: 36rpx; font-size: 28rpx; text-align: center; border: none; }
.dialog-btn.cancel { background: #f5f7fa; color: #606266; }
.dialog-btn.submit { background: #409eff; color: #fff; }
</style>
