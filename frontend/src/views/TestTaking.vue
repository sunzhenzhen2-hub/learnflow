<template>
  <div class="test-taking">
    <div class="test-header">
      <h3>{{ testTitle || $t('learning.testTitle') }}</h3>
      <div class="test-progress">
        <span>进度 {{ answeredCount }}/{{ questions.length }}</span>
        <el-progress :percentage="progressPercent" :stroke-width="6" :show-text="false" />
      </div>
    </div>

    <div class="questions">
      <div
        v-for="(q, idx) in questions"
        :key="idx"
        class="question-card"
        :class="{ answered: answers[idx] !== undefined && answers[idx] !== '' }"
      >
        <div class="question-header">
          <el-tag size="small" :type="questionTypeTag(q.type)" class="type-badge">
            {{ questionTypeLabel(q.type) }}
          </el-tag>
          <span class="q-number">第 {{ idx + 1 }} 题</span>
        </div>

        <div class="question-text">{{ q.question }}</div>

        <!-- Choice -->
        <div v-if="q.type === 'choice'" class="choice-options">
          <div
            v-for="(opt, oi) in q.options"
            :key="oi"
            class="option-item"
            :class="{
              selected: answers[idx] === optionLetter(oi),
              correct: submitted && answers[idx] !== optionLetter(oi) && optionLetter(oi) === q.correct,
              wrong: submitted && answers[idx] === optionLetter(oi) && optionLetter(oi) !== q.correct,
            }"
            @click="!submitted && selectChoice(idx, optionLetter(oi))"
          >
            <span class="option-letter">{{ optionLetter(oi) }}</span>
            <span class="option-text">{{ opt }}</span>
            <el-icon v-if="submitted && optionLetter(oi) === q.correct" class="correct-icon" color="#67c23a"><CircleCheck /></el-icon>
            <el-icon v-if="submitted && answers[idx] === optionLetter(oi) && optionLetter(oi) !== q.correct" class="wrong-icon" color="#f56c6c"><CircleClose /></el-icon>
          </div>
        </div>

        <!-- True/False -->
        <div v-else-if="q.type === 'true_false'" class="tf-options">
          <div
            v-for="val in ['true', 'false']"
            :key="val"
            class="tf-item"
            :class="{
              selected: answers[idx] === val,
              correct: submitted && val === q.correct,
              wrong: submitted && answers[idx] === val && val !== q.correct,
            }"
            @click="!submitted && selectChoice(idx, val)"
          >
            <span>{{ val === 'true' ? 'T 正确' : 'F 错误' }}</span>
            <el-icon v-if="submitted && val === q.correct" color="#67c23a"><CircleCheck /></el-icon>
          </div>
        </div>

        <!-- Short Answer -->
        <div v-else-if="q.type === 'short'" class="short-answer">
          <el-input
            v-model="answers[idx]"
            type="textarea"
            :rows="3"
            placeholder="请用自己的话回答，答到参考答案关键词即可得分"
            :disabled="submitted"
          />
          <div v-if="submitted" class="short-result" :class="questionResults[idx]?.correct ? 'correct' : 'wrong'">
            <div class="short-score">得分: {{ questionResults[idx]?.score }}/100</div>
            <div class="short-keywords">
              参考关键词: <span v-for="kw in q.keywords" :key="kw" class="kw-tag">{{ kw }}</span>
            </div>
          </div>
        </div>

        <!-- Choice/TF result -->
        <div v-if="submitted && q.type !== 'short'" class="question-result" :class="questionResults[idx]?.correct ? 'correct' : 'wrong'">
          <span v-if="questionResults[idx]?.correct" class="result-badge pass">正确</span>
          <span v-else class="result-badge fail">错误 (正确答案: {{ q.correct }})</span>
        </div>
      </div>
    </div>

    <div class="test-actions">
      <div v-if="!submitted && answeredCount > 0" class="submit-hint">
        {{ unansweredCount > 0 ? '还有 ' + unansweredCount + ' 题未作答' : '准备提交测试' }}
      </div>
      <el-button
        v-if="!submitted"
        type="primary"
        size="large"
        :disabled="answeredCount === 0"
        :loading="submitting"
        @click="submitTest"
      >
        提交测试
      </el-button>
      <el-button
        v-if="submitted && !passed"
        type="warning"
        size="large"
        @click="retryTest"
      >
        重新测试
      </el-button>
    </div>

    <el-dialog v-model="showResultDialog" title="测试结果" width="80%">
      <div class="result-summary" :class="passed ? 'passed' : 'failed'">
        <div class="score-display">
          <div class="score-circle" :class="passed ? 'pass' : 'fail'">
            <span class="score-num">{{ testResult?.score || 0 }}</span>
            <span class="score-denom">/100</span>
          </div>
          <div class="score-label">{{ passed ? '通过' : '未通过' }}</div>
          <div class="score-detail">{{ testResult?.correct || 0 }}/{{ testResult?.total || 0 }} 题正确</div>
        </div>

        <el-alert
          v-if="testResult?.feedback"
          :title="testResult.feedback"
          :type="passed ? 'success' : 'warning'"
          show-icon
          :closable="false"
          style="margin: 16px 0"
        />

        <div v-if="testResult?.suggestions?.length" class="suggestions">
          <h4>改进建议</h4>
          <ul>
            <li v-for="(s, i) in testResult.suggestions" :key="i">{{ s }}</li>
          </ul>
        </div>
      </div>
      <template #footer>
        <el-button v-if="!passed" type="primary" @click="retryTest">重新测试</el-button>
        <el-button v-else type="success" @click="onPassed">继续学习</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { reviewApi } from '../api/client'
import { ElMessage } from 'element-plus'
import { CircleCheck, CircleClose } from '@element-plus/icons-vue'

const props = defineProps({
  stepId: { type: Number, required: true },
  questions: { type: Array, default: () => [] },
  testTitle: { type: String, default: '' },
})

const emit = defineEmits(['test-passed'])

const answers = ref({})
const submitted = ref(false)
const submitting = ref(false)
const showResultDialog = ref(false)
const testResult = ref(null)
const questionResults = ref({})

const answeredCount = computed(() =>
  Object.keys(answers.value).filter(k => answers.value[k] !== '' && answers.value[k] !== undefined).length
)
const unansweredCount = computed(() => props.questions.length - answeredCount.value)
const progressPercent = computed(() =>
  props.questions.length ? Math.round((answeredCount.value / props.questions.length) * 100) : 0
)
const passed = computed(() => testResult.value?.passed === true)

const optionLetter = (idx) => String.fromCharCode(65 + idx)

const questionTypeTag = (t) => ({ choice: 'primary', true_false: 'warning', short: 'info' }[t] || '')
const questionTypeLabel = (t) => ({ choice: 'CHOICE', true_false: 'JUDGE', short: 'SHORT' }[t] || t)

const selectChoice = (idx, val) => { answers.value[idx] = val }

const submitTest = async () => {
  if (submitting.value) return
  submitting.value = true
  try {
    const answerList = Object.entries(answers.value)
      .filter(([, v]) => v !== '' && v !== undefined)
      .map(([k, v]) => ({ question_index: parseInt(k), answer: String(v) }))

    const { data } = await reviewApi.gradeTest(props.stepId, answerList)
    testResult.value = data
    questionResults.value = {}
    for (const r of (data.results || [])) {
      questionResults.value[r.index] = r
    }
    submitted.value = true
    showResultDialog.value = true
  } catch (e) {
    ElMessage.error('提交失败: ' + (e.response?.data?.detail || e.message))
  } finally {
    submitting.value = false
  }
}

const retryTest = () => {
  showResultDialog.value = false
  answers.value = {}
  submitted.value = false
  testResult.value = null
  questionResults.value = {}
}

const onPassed = () => {
  showResultDialog.value = false
  emit('test-passed', { score: testResult.value?.score, stepId: props.stepId })
}
</script>

<style scoped>
.test-taking { padding: 0; }
.test-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.test-header h3 { margin: 0; font-size: 16px; }
.test-progress { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #909399; min-width: 140px; }
.questions { display: flex; flex-direction: column; gap: 14px; }
.question-card { border: 1px solid #e4e7ed; border-radius: 8px; padding: 16px; transition: all 0.2s; }
.question-card.answered { border-color: #409eff; background: #f5f9ff; }
.question-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.type-badge { font-size: 11px; letter-spacing: 0.5px; }
.q-number { font-size: 12px; color: #909399; }
.question-text { font-size: 15px; font-weight: 500; color: #303133; margin-bottom: 12px; line-height: 1.6; }

.choice-options { display: flex; flex-direction: column; gap: 8px; }
.option-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 14px; border: 1px solid #dcdfe6;
  border-radius: 6px; cursor: pointer; transition: all 0.15s; font-size: 14px;
}
.option-item:hover { border-color: #409eff; background: #ecf5ff; }
.option-item.selected { border-color: #409eff; background: #ecf5ff; }
.option-item.correct { border-color: #67c23a; background: #f0f9eb; }
.option-item.wrong { border-color: #f56c6c; background: #fef0f0; }
.option-letter {
  width: 24px; height: 24px; border-radius: 50%;
  background: #f0f2f5; display: flex; align-items: center; justify-content: center;
  font-weight: 600; font-size: 13px; flex-shrink: 0;
}
.option-item.selected .option-letter { background: #409eff; color: #fff; }
.option-item.correct .option-letter { background: #67c23a; color: #fff; }
.option-item.wrong .option-letter { background: #f56c6c; color: #fff; }
.option-text { flex: 1; }

.tf-options { display: flex; gap: 12px; }
.tf-item {
  flex: 1; padding: 14px; text-align: center;
  border: 1px solid #dcdfe6; border-radius: 6px;
  cursor: pointer; font-size: 15px; font-weight: 500; transition: all 0.15s;
}
.tf-item:hover { border-color: #409eff; background: #ecf5ff; }
.tf-item.selected { border-color: #409eff; background: #ecf5ff; }
.tf-item.correct { border-color: #67c23a; background: #f0f9eb; color: #67c23a; }
.tf-item.wrong { border-color: #f56c6c; background: #fef0f0; color: #f56c6c; }

.short-answer :deep(.el-textarea__inner) { font-size: 14px; }
.short-result { margin-top: 10px; padding: 10px; border-radius: 6px; font-size: 13px; }
.short-result.correct { background: #f0f9eb; border: 1px solid #67c23a; }
.short-result.wrong { background: #fef0f0; border: 1px solid #f56c6c; }
.short-score { font-weight: 600; margin-bottom: 6px; }
.kw-tag {
  display: inline-block; background: #e8f0fe; color: #409eff;
  padding: 2px 6px; border-radius: 3px; font-size: 12px; margin-right: 4px;
}

.question-result { margin-top: 10px; }
.result-badge { font-size: 13px; font-weight: 500; padding: 4px 10px; border-radius: 4px; }
.result-badge.pass { background: #f0f9eb; color: #67c23a; }
.result-badge.fail { background: #fef0f0; color: #f56c6c; }

.test-actions { margin-top: 20px; text-align: center; }
.submit-hint { font-size: 13px; color: #909399; margin-bottom: 10px; }

.score-display { text-align: center; margin-bottom: 16px; }
.score-circle {
  width: 100px; height: 100px; border-radius: 50%;
  display: inline-flex; flex-direction: column; align-items: center; justify-content: center;
  margin-bottom: 8px;
}
.score-circle.pass { border: 4px solid #67c23a; }
.score-circle.fail { border: 4px solid #f56c6c; }
.score-num { font-size: 32px; font-weight: 700; }
.score-circle.pass .score-num { color: #67c23a; }
.score-circle.fail .score-num { color: #f56c6c; }
.score-denom { font-size: 14px; color: #909399; }
.score-label { font-size: 18px; font-weight: 600; }
.score-detail { font-size: 14px; color: #909399; margin-top: 4px; }
.suggestions { text-align: left; }
.suggestions h4 { font-size: 14px; margin-bottom: 8px; }
.suggestions ul { padding-left: 20px; font-size: 14px; color: #606266; }
.suggestions li { margin-bottom: 4px; }

@media (max-width: 480px) {
  .test-header { flex-direction: column; align-items: flex-start; gap: 8px; }
  .tf-options { flex-direction: column; }
}
</style>
