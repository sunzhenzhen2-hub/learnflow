<template>
  <div class="wizard">
    <el-steps :active="currentStep" finish-status="success" align-center>
      <el-step :title="$t('wizard.stepTopic')" />
      <el-step :title="$t('wizard.stepLevel')" />
      <el-step :title="$t('wizard.stepSchedule')" />
      <el-step :title="$t('wizard.stepConfirm')" />
    </el-steps>

    <!-- Step 1: Topic & Goal -->
    <div v-show="currentStep === 0" class="wizard-step">
      <h2>{{ $t('wizard.topicTitle') }}</h2>
      <el-form :model="form" label-position="top">
        <el-form-item :label="$t('wizard.topicLabel')" required>
          <el-input
            v-model="form.topic"
            :placeholder="$t('wizard.topicPlaceholder')"
            size="large"
          />
        </el-form-item>
        <el-form-item :label="$t('wizard.goalLabel')" required>
          <el-select v-model="form.goal" :placeholder="$t('wizard.goalPlaceholder')" size="large" style="width: 100%">
            <el-option
              v-for="(desc, key) in goalOptions"
              :key="key"
              :label="desc"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('wizard.focusLabel')">
          <el-select v-model="form.focus_areas" multiple filterable allow-create :placeholder="$t('wizard.focusPlaceholder')">
          </el-select>
        </el-form-item>
      </el-form>
    </div>

    <!-- Step 2: Level -->
    <div v-show="currentStep === 1" class="wizard-step">
      <h2>{{ $t('wizard.levelTitle') }}</h2>
      <div class="level-cards">
        <div
          v-for="lvl in levels"
          :key="lvl.value"
          class="level-card"
          :class="{ selected: form.current_level === lvl.value }"
          @click="form.current_level = lvl.value"
        >
          <div class="level-name">{{ lvl.label }}</div>
          <div class="level-desc">{{ lvl.desc }}</div>
        </div>
      </div>
    </div>

    <!-- Step 3: Schedule -->
    <div v-show="currentStep === 2" class="wizard-step">
      <h2>{{ $t('wizard.scheduleTitle') }}</h2>
      <el-form :model="form" label-position="top">
        <el-form-item :label="$t('wizard.hoursPerWeek')">
          <el-slider v-model="form.weekly_hours" :min="3" :max="30" :step="1" show-input />
        </el-form-item>
        <el-form-item :label="$t('wizard.studyDays')">
          <el-checkbox-group v-model="form.preferred_days">
            <el-checkbox-button v-for="d in 7" :key="d" :value="d">
              {{ $t('wizard.dayShort.' + d) }}
            </el-checkbox-button>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item :label="$t('wizard.startDate')">
          <el-date-picker v-model="form.start_date" type="date" :placeholder="$t('wizard.pickDate')" />
        </el-form-item>
      </el-form>
    </div>

    <!-- Step 4: Confirm -->
    <div v-show="currentStep === 3" class="wizard-step">
      <h2>{{ $t('wizard.confirmTitle') }}</h2>
      <el-descriptions :column="1" border>
        <el-descriptions-item :label="$t('wizard.topicField')">{{ form.topic }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wizard.goalField')">{{ form.goal ? goalOptions[form.goal] || form.goal : '-' }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wizard.levelField')">{{ form.current_level }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wizard.hoursField')">{{ form.weekly_hours }}h</el-descriptions-item>
        <el-descriptions-item :label="$t('wizard.daysField')">{{ dayNames }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wizard.startDateField')">{{ form.start_date || $t('wizard.today') }}</el-descriptions-item>
        <el-descriptions-item :label="$t('wizard.focusField')" v-if="form.focus_areas.length">
          {{ form.focus_areas.join(', ') }}
        </el-descriptions-item>
      </el-descriptions>
    </div>

    <!-- Navigation -->
    <div class="wizard-nav">
      <el-button v-if="currentStep > 0" @click="currentStep--">{{ $t('wizard.back') }}</el-button>
      <el-button
        v-if="currentStep < 3"
        type="primary"
        @click="nextStep"
        :disabled="!canProceed"
      >
        {{ $t('wizard.next') }}
      </el-button>
      <el-button
        v-if="currentStep === 3"
        type="success"
        @click="createPlan"
        :loading="creating"
      >
        {{ $t('wizard.generate') }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePlanStore } from '../stores/plan'
import { ElMessage } from 'element-plus'

const router = useRouter()
const store = usePlanStore()
const { t, tm } = useI18n()
const currentStep = ref(0)
const creating = ref(false)

const goalOptions = computed(() => {
  const raw = tm('wizard.goalOptions')
  return typeof raw === 'object' && raw !== null ? raw : {}
})

const levels = computed(() => [
  { value: 'beginner', label: t('wizard.beginner'), desc: t('wizard.beginnerDesc') },
  { value: 'intermediate', label: t('wizard.intermediate'), desc: t('wizard.intermediateDesc') },
  { value: 'advanced', label: t('wizard.advanced'), desc: t('wizard.advancedDesc') },
])

const form = ref({
  topic: '',
  goal: '',
  current_level: 'beginner',
  weekly_hours: 10,
  preferred_days: [1, 3, 5, 6, 7],
  start_date: null,
  focus_areas: [],
})

const dayNames = computed(() => {
  return form.value.preferred_days.map(d => t('wizard.days.' + d)).join(', ')
})

const canProceed = computed(() => {
  if (currentStep.value === 0) return form.value.topic && form.value.goal
  if (currentStep.value === 1) return form.value.current_level
  if (currentStep.value === 2) return form.value.preferred_days.length > 0
  return true
})

const nextStep = () => {
  if (canProceed.value) currentStep.value++
}

const createPlan = async () => {
  creating.value = true
  try {
    const plan = await store.createPlan({
      ...form.value,
      start_date: form.value.start_date || new Date().toISOString().split('T')[0],
    })
    ElMessage.success(t('wizard.success'))
    router.push(`/learn/${plan.id}`)
  } catch (e) {
    ElMessage.error(t('wizard.failed') + (e.response?.data?.detail || e.message))
  } finally {
    creating.value = false
  }
}
</script>

<style scoped>
.wizard { max-width: 600px; margin: 0 auto; }

.wizard-step {
  margin: 32px 0;
  min-height: 300px;
}

.wizard-step h2 {
  font-size: 22px;
  margin-bottom: 24px;
  color: #303133;
}

.wizard-nav {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px 0;
}

.level-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 400px;
  margin: 0 auto;
}

.level-card {
  padding: 20px 24px;
  border: 2px solid #dcdfe6;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: center;
}

.level-card:hover {
  border-color: #409eff;
  background: #f5f7fa;
}

.level-card.selected {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.2);
}

.level-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.level-desc {
  font-size: 13px;
  color: #909399;
}

@media (max-width: 480px) {
  .wizard {
    max-width: 100%;
    padding: 0 4px;
  }

  .wizard-step {
    margin: 20px 0;
    min-height: 250px;
  }

  .wizard-step h2 {
    font-size: 18px;
    margin-bottom: 16px;
  }

  .level-cards {
    max-width: 100%;
  }

  .level-card {
    padding: 16px;
  }

  .level-name {
    font-size: 16px;
  }

  .wizard-nav {
    padding: 16px 0;
  }

  .el-descriptions {
    font-size: 13px;
  }
}
</style>
