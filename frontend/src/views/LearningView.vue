<template>
  <div class="learning-view">
    <!-- Week Navigation -->
    <div class="week-nav">
      <el-button text @click="prevWeek" :disabled="currentWeek <= 1">
        <el-icon><ArrowLeft /></el-icon>
      </el-button>
      <span class="week-label">{{ $t('learning.week', { week: currentWeek }) }}</span>
      <el-button text @click="nextWeek" :disabled="currentWeek >= totalWeeks">
        <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>

    <!-- Step List for Current Week -->
    <div class="steps-container">
      <div
        v-for="step in weekSteps"
        :key="step.id"
        class="step-card"
        :class="{
          locked: step.locked,
          active: selectedStep?.id === step.id,
          completed: step.status === 'completed'
        }"
        @click="selectStep(step)"
      >
        <div class="step-status-icon">
          <el-icon v-if="step.locked" color="#c0c4cc"><Lock /></el-icon>
          <el-icon v-else-if="step.status === 'completed'" color="#67c23a"><CircleCheckFilled /></el-icon>
          <el-icon v-else-if="step.status === 'in_progress'" color="#409eff"><Loading /></el-icon>
          <el-icon v-else color="#e6a23c"><CircleFilled /></el-icon>
        </div>
        <div class="step-content">
          <div class="step-title">
            <el-tag v-if="step.ladder_name" size="small" type="info" class="ladder-badge" effect="plain">
              {{ step.ladder_name }}
            </el-tag>
            {{ step.title }}
          </div>
          <div class="step-meta">
            <el-tag size="small" :type="typeTag(step.step_type)">{{ typeLabel(step.step_type) }}</el-tag>
            <span>{{ step.duration_minutes }}{{ $t('dashboard.min') }}</span>
            <span>{{ formatDate(step.date) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Selected Step Detail -->
    <div v-if="selectedStep && !selectedStep.locked" class="step-detail">
      <el-divider />
      <h3>{{ selectedStep.title }}</h3>

      <!-- Learning Resources -->
      <div class="resources-section" v-if="selectedStep.resources?.length">
        <h4>{{ $t('learning.resources') }}</h4>
        <div class="resource-list">
          <div v-for="(res, i) in selectedStep.resources.filter(r => !r.synthesized)" :key="i" class="resource-item">
            <template v-if="res.type === 'video' && res.embed_url">
              <div class="video-player-wrapper">
                <iframe
                  :src="res.embed_url"
                  scrolling="no"
                  frameborder="0"
                  allowfullscreen="true"
                  class="video-iframe"
                ></iframe>
              </div>
              <div class="resource-video-info">
                <span class="resource-link">{{ res.title }}</span>
                <span class="resource-meta">{{ res.platform }}{{ res.duration ? ' \u00b7 ' + res.duration : '' }}</span>
              </div>
            </template>
            <template v-else>
              <el-icon :color="resourceColor(res.type)">
                <VideoPlay v-if="res.type === 'video'" />
                <Document v-else-if="res.type === 'article'" />
                <Notebook v-else />
              </el-icon>
              <div class="resource-info">
                <a v-if="res.url" :href="res.url" target="_blank" class="resource-link">{{ res.title }}</a>
                <span v-else class="resource-link">{{ res.title }}</span>
                <span class="resource-meta">{{ res.platform }}{{ res.duration ? '· ' + res.duration : '' }}</span>
                <span v-if="res.why" class="resource-why">{{ res.why }}</span>
              </div>
            </template>
          </div>
        </div>
      </div>

      <!-- Core 20% Highlight -->
      <div class="core20-section" v-if="selectedStep.core_20_percent">
        <h4>{{ $t('learning.core20') }}</h4>
        <div class="core20-text">{{ selectedStep.core_20_percent }}</div>
      </div>

      <!-- Learning Content (text summary) -->
      <div class="content-section" v-if="selectedStep.content">
        <h4>{{ $t('learning.learningContent') }}</h4>
        <div class="content-text">{{ selectedStep.content }}</div>
      </div>

      <!-- Knowledge Point Tabs (LLM synthesized) -->
      <div class="knowledge-tabs-section" v-if="knowledgePoints.length">
        <h4>{{ $t('learning.knowledgePoints') || "核心知识点" }}</h4>
        <el-tabs v-model="activeTab" class="knowledge-tabs" tab-position="top">
          <el-tab-pane
            v-for="kp in knowledgePoints"
            :key="kp.index"
            :label="kp.title"
            :name="String(kp.index)"
          >
            <div class="knowledge-body" v-html="renderMarkdown(kp.body)"></div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- Test Question -->
      <div class="test-section" v-if="selectedStep.test_question">
        <h4>{{ $t('learning.testQuestion') }}</h4>
        <div class="test-question">{{ selectedStep.test_question }}</div>
      </div>

      <!-- Test Taking (structured) -->
      <div v-if="selectedStep.test_questions?.length" class="test-section-full">
        <TestTaking
          :step-id="selectedStep.id"
          :questions="selectedStep.test_questions"
          :test-title="selectedStep.title + ' - 测试' + (selectedStep.ladder_name ? ' [' + selectedStep.ladder_name + ']' : '')"
          @test-passed="onTestPassed"
        />
      </div>

      <!-- Actions based on step status -->
      <div class="actions" v-if="selectedStep.status !== 'completed' && !selectedStep.test_questions?.length">
        <el-button
          v-if="selectedStep.status === 'available'"
          type="primary"
          @click="startStep"
        >
          {{ $t('learning.startStep') }}
        </el-button>

        <template v-if="selectedStep.status === 'in_progress' || selectedStep.status === 'review_failed'">
          <el-button type="success" @click="showOutputDialog = true">
            {{ selectedStep.test_question ? $t('learning.submitTest') : $t('learning.submitOutput') }}
          </el-button>
        </template>
      </div>

      <!-- Completed State -->
      <div v-if="selectedStep.status === 'completed'" class="completed-state">
        <el-result
          icon="success"
          :title="$t('learning.stepCompleted')"
          :sub-title="`${$t('learning.score')}: ${selectedStep.ai_score || $t('learning.na')}/100`"
        />
      </div>

      <!-- AI Review Result -->
      <div v-if="selectedStep.ai_review_result" class="review-result">
        <h4>{{ $t('learning.aiReview') }}</h4>
        <el-alert
          :title="selectedStep.ai_score >= 70 ? $t('learning.passed') : $t('learning.needsImprovement')"
          :type="selectedStep.ai_score >= 70 ? 'success' : 'warning'"
          :description="selectedStep.ai_review_result.feedback"
          show-icon
          :closable="false"
        />
        <div v-if="selectedStep.ai_review_result.suggestions?.length" class="suggestions">
          <h5>{{ $t('learning.suggestions') }}</h5>
          <ul>
            <li v-for="(s, i) in selectedStep.ai_review_result.suggestions" :key="i">{{ s }}</li>
          </ul>
        </div>
        <div v-if="selectedStep.ai_review_result.socratic_question" class="socratic-section">
          <h5>{{ $t('learning.socraticQuestion') }}</h5>
          <div class="socratic-question">{{ selectedStep.ai_review_result.socratic_question }}</div>
        </div>
        <div v-if="selectedStep.ai_review_result.feynman_score != null" class="feynman-section">
          <h5>{{ $t('learning.feynmanScore') }}: {{ selectedStep.ai_review_result.feynman_score }}/100</h5>
          <div v-if="selectedStep.ai_review_result.feynman_analysis" class="feynman-detail">
            <span v-if="selectedStep.ai_review_result.feynman_analysis.simple_language">✓ {{ $t('learning.feynmanDesc') }}</span>
            <span v-if="selectedStep.ai_review_result.feynman_analysis.improvement"> — {{ selectedStep.ai_review_result.feynman_analysis.improvement }}</span>
          </div>
        </div>
        <div v-if="selectedStep.ai_review_result.cheat_sheet" class="cheatsheet-section">
          <h5>{{ $t('learning.cheatSheetTitle') }}</h5>
          <div class="cheatsheet-text">{{ selectedStep.ai_review_result.cheat_sheet }}</div>
        </div>
      </div>
    </div>

    <!-- Output/Test Dialog -->
    <el-dialog v-model="showOutputDialog" :title="dialogTitle" width="90%">
      <p class="dialog-hint">{{ dialogHint }}</p>
      <el-input
        v-model="outputContent"
        type="textarea"
        :rows="10"
        :placeholder="dialogPlaceholder"
      />
      <template #footer>
        <el-button @click="showOutputDialog = false">{{ $t('learning.cancel') }}</el-button>
        <el-button type="primary" @click="submitOutput" :loading="submitting">
          {{ $t('learning.submitForReview') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { planApi, stepApi, reviewApi } from '../api/client'
import TestTaking from './TestTaking.vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()
const planId = parseInt(route.params.planId)

const steps = ref([])
const currentWeek = ref(1)
const totalWeeks = ref(16)
const selectedStep = ref(null)
const showOutputDialog = ref(false)
const outputContent = ref('')
const submitting = ref(false)

const weekSteps = computed(() =>
  steps.value.filter(s => s.week_num === currentWeek.value)
)

const activeTab = ref('0')

// Simple markdown renderer (bolds, code blocks, quotes)
const renderMarkdown = (text) => {
  if (!text) return ''
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/\n/g, '<br>')
}

// Parse doc_content into knowledge point tabs
const knowledgePoints = computed(() => {
  const doc = selectedStep.value?.doc_content
  if (!doc) return []
  const SEP = '---知识点分隔符---'
  if (doc.includes(SEP)) {
    return doc.split(SEP).map((section, idx) => {
      const trimmed = section.trim()
      const firstHash = trimmed.indexOf('## ')
      let title = '知识点 ' + (idx + 1)
      let body = trimmed
      if (firstHash !== -1) {
        const nextNewline = trimmed.indexOf("\n", firstHash)
        if (nextNewline !== -1) {
          title = trimmed.slice(firstHash + 3, nextNewline).trim()
          body = trimmed.slice(nextNewline + 1).trim()
        } else {
          title = trimmed.slice(firstHash + 3).trim()
          body = ''
        }
      }
      return { title, body, index: idx }
    })
  }
  // Fallback: treat whole doc as single tab
  return doc.trim() ? [{ title: '知识内容', body: doc.trim(), index: 0 }] : []
})

const formatDate = (d) => dayjs(d).format('MM/DD ddd')
const typeTag = (t) => ({ study: 'info', project: 'success', deep_project: 'warning', output: 'danger', cheat_sheet: 'warning', test: 'info' }[t] || 'info')
const typeLabel = (type) => t('learning.stepTypes.' + type) || type

const resourceColor = (type) => ({ video: '#409eff', article: '#67c23a', doc: '#e6a23c' }[type] || '#909399')

const dialogTitle = computed(() =>
  selectedStep.value?.test_question ? t('learning.testTitle') : t('learning.outputTitle')
)
const dialogHint = computed(() =>
  selectedStep.value?.test_question
    ? t('learning.testHint')
    : t('learning.outputHint')
)
const dialogPlaceholder = computed(() =>
  selectedStep.value?.test_question
    ? t('learning.testPlaceholder')
    : t('learning.outputPlaceholder')
)

const prevWeek = () => { if (currentWeek.value > 1) currentWeek.value-- }
const nextWeek = () => { if (currentWeek.value < totalWeeks.value) currentWeek.value++ }

const selectStep = (step) => {
  if (!step.locked) selectedStep.value = step
}

const loadSteps = async () => {
  const { data } = await planApi.getSteps(planId)
  steps.value = data
  const plan = await planApi.get(planId)
  totalWeeks.value = plan.data.total_weeks
  const today = dayjs().format('YYYY-MM-DD')
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
}

const onTestPassed = async ({ score, stepId }) => {
  ElMessage.success('测试通过！得分 ' + score + '/100')
  await loadSteps()
}

const startStep = async () => {
  try {
    await stepApi.start(selectedStep.value.id)
    selectedStep.value.status = 'in_progress'
    ElMessage.success(t('learning.stepStarted'))
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || t('learning.reviewFailed') + e.message)
  }
}

const submitOutput = async () => {
  if (!outputContent.value.trim()) {
    ElMessage.warning(t('learning.outputEmpty'))
    return
  }
  submitting.value = true
  try {
    await stepApi.submitOutput(selectedStep.value.id, outputContent.value)
    const { data: review } = await reviewApi.review(selectedStep.value.id)

    if (review.passed) {
      await stepApi.complete(selectedStep.value.id)
      selectedStep.value.status = 'completed'
      selectedStep.value.ai_score = review.score
      selectedStep.value.ai_review_result = {
        feedback: review.feedback,
        suggestions: review.suggestions,
        socratic_question: review.socratic_question,
        feynman_score: review.feynman_score,
        feynman_analysis: review.feynman_analysis,
        cheat_sheet: review.cheat_sheet,
      }
      ElMessage.success(t('learning.passedMsg', { score: review.score }))
      showOutputDialog.value = false
      outputContent.value = ''
      await loadSteps()
    } else {
      selectedStep.value.ai_score = review.score
      selectedStep.value.ai_review_result = {
        feedback: review.feedback,
        suggestions: review.suggestions,
        socratic_question: review.socratic_question,
        feynman_score: review.feynman_score,
        feynman_analysis: review.feynman_analysis,
        cheat_sheet: review.cheat_sheet,
      }
      ElMessage.warning(t('learning.failedMsg', { score: review.score }))
      showOutputDialog.value = false
    }
  } catch (e) {
    ElMessage.error(t('learning.reviewFailed') + (e.response?.data?.detail || e.message))
  } finally {
    submitting.value = false
  }
}

onMounted(loadSteps)
watch(currentWeek, () => { selectedStep.value = null })
</script>

<style scoped>
.learning-view { padding: 0; }

.week-nav {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
}

.week-label { font-size: 18px; font-weight: 600; }

.step-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.step-card:hover { background: #f5f7fa; }
.step-card.active { border-color: #409eff; background: #ecf5ff; }
.step-card.locked { opacity: 0.5; cursor: not-allowed; }
.step-card.completed { background: #f0f9eb; }

.step-content { flex: 1; }
.step-title { font-weight: 600; font-size: 14px; }
.step-meta { display: flex; gap: 8px; align-items: center; margin-top: 4px; font-size: 12px; color: #909399; }

.step-detail { margin-top: 16px; }
.step-detail h3 { font-size: 18px; margin-bottom: 16px; }
.step-detail h4 { font-size: 15px; margin-bottom: 10px; color: #303133; }

.resources-section { background: #f0f5ff; padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 3px solid #409eff; }
.resource-list { display: flex; flex-direction: column; gap: 10px; }
.resource-item { display: flex; align-items: flex-start; gap: 10px; }
.resource-info { flex: 1; }
.resource-link { font-size: 14px; color: #409eff; text-decoration: none; font-weight: 500; }
.resource-link:hover { text-decoration: underline; }
.resource-meta { font-size: 12px; color: #909399; margin-left: 8px; }
.resource-why { display: block; font-size: 12px; color: #67c23a; margin-top: 2px; font-style: italic; }

.content-section { background: #f9f9f9; padding: 16px; border-radius: 8px; margin-bottom: 16px; }
.content-text { white-space: pre-wrap; line-height: 1.8; font-size: 14px; }

.knowledge-tabs-section {
  background: #f0f9ff;
  border-radius: 8px;
  margin-bottom: 16px;
  border: 1px solid #dcdfe6;
  overflow: hidden;
}
.knowledge-tabs-section h4 { padding: 12px 16px 0; font-size: 15px; color: #303133; margin: 0; }
.knowledge-tabs { margin: 0; }
.knowledge-tabs :deep(.el-tabs__header) { margin: 0; background: #f5f7fa; }
.knowledge-tabs :deep(.el-tabs__item) { font-size: 13px; }
.knowledge-tabs :deep(.el-tabs__content) { padding: 16px; }
.knowledge-body { font-size: 14px; line-height: 1.8; color: #303133; }
.knowledge-body blockquote {
  border-left: 3px solid #e6a23c;
  background: #fff7e6;
  padding: 8px 12px;
  margin: 8px 0;
  border-radius: 0 4px 4px 0;
  color: #865a00;
}
.knowledge-body code {
  background: #f0f0f0;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 13px;
  color: #e03e3e;
}

.test-section { background: #fdf6ec; padding: 16px; border-radius: 8px; margin-bottom: 16px; border-left: 3px solid #e6a23c; }
.test-question { font-size: 14px; line-height: 1.8; color: #606266; white-space: pre-wrap; }

.actions { display: flex; gap: 12px; margin: 16px 0; }

.review-result { margin-top: 16px; }
.suggestions { margin-top: 12px; }
.suggestions ul { padding-left: 20px; }
.suggestions li { margin-bottom: 4px; color: #606266; font-size: 14px; }

.dialog-hint { color: #909399; margin-bottom: 16px; font-size: 14px; }

.ladder-badge { margin-right: 6px; }

.core20-section {
  background: linear-gradient(135deg, #fff7e6 0%, #fff3cd 100%);
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
  border-left: 3px solid #e6a23c;
}
.core20-text { font-size: 14px; line-height: 1.8; color: #606266; font-weight: 500; }

.socratic-section {
  background: linear-gradient(135deg, #f0f5ff 0%, #e8f0fe 100%);
  padding: 14px;
  border-radius: 8px;
  margin-top: 12px;
  border-left: 3px solid #409eff;
}
.socratic-question { font-size: 14px; line-height: 1.8; color: #303133; font-style: italic; }

.feynman-section {
  background: #f0f9eb;
  padding: 14px;
  border-radius: 8px;
  margin-top: 12px;
  border-left: 3px solid #67c23a;
}
.feynman-detail { font-size: 13px; color: #606266; margin-top: 4px; }

.cheatsheet-section {
  background: #f9f0ff;
  padding: 14px;
  border-radius: 8px;
  margin-top: 12px;
  border-left: 3px solid #9b59b6;
}
.cheatsheet-text { font-size: 13px; line-height: 1.8; color: #606266; white-space: pre-wrap; }

@media (max-width: 480px) {
  .week-nav {
    padding: 10px;
    gap: 12px;
  }

  .week-label {
    font-size: 16px;
  }

  .step-card {
    padding: 10px 12px;
    gap: 8px;
  }

  .step-title {
    font-size: 13px;
  }

  .step-meta {
    flex-wrap: wrap;
    gap: 4px;
  }

  .step-detail h3 {
    font-size: 16px;
  }

  .resources-section,
  .content-section,
  .test-section {
    padding: 12px;
  }

  .actions {
    flex-direction: column;
    gap: 8px;
  }

  .actions .el-button {
    width: 100%;
  }
}
</style>
