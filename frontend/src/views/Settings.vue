<template>
  <div class="settings-view">
    <h2>{{ $t('settings.title') }}</h2>

    <div class="card">
      <h3>{{ $t('settings.channels') }}</h3>
      <div class="channel-list">
        <div v-for="ch in channels" :key="ch.key" class="channel-item">
          <div class="channel-info">
            <el-icon :size="24"><component :is="ch.icon" /></el-icon>
            <div>
              <div class="channel-name">{{ $t('settings.' + ch.key) }}</div>
              <div class="channel-desc">{{ $t('settings.' + ch.key + 'Desc') }}</div>
            </div>
          </div>
          <div class="channel-actions">
            <el-switch v-model="ch.enabled" @change="toggleChannel(ch)" />
            <el-button size="small" @click="testChannel(ch.key)" :loading="ch.testing">
              {{ $t('settings.test') }}
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <div class="card" v-if="plans.length">
      <h3>{{ $t('settings.plans') }}</h3>
      <div v-for="plan in plans" :key="plan.id" class="plan-item">
        <div>
          <strong>{{ plan.topic }}</strong>
          <el-tag size="small" :type="plan.status === 'active' ? 'success' : 'info'">
            {{ plan.status }}
          </el-tag>
          <span class="plan-progress">{{ plan.progress.toFixed(0) }}%</span>
        </div>
        <div>
          <el-button size="small" @click="$router.push(`/learn/${plan.id}`)">{{ $t('settings.open') }}</el-button>
          <el-popconfirm :title="$t('settings.deleteConfirm')" @confirm="deletePlan(plan.id)">
            <template #reference>
              <el-button size="small" type="danger">{{ $t('settings.delete') }}</el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>
    </div>

    <!-- LLM Configuration -->
    <div class="card">
      <h3>{{ $t('settings.llmConfig') }}</h3>

      <!-- 配置状态 -->
      <div class="llm-status" :class="{ configured: llmConfigured }">
        <el-icon :size="16"><component :is="llmConfigured ? 'CircleCheck' : 'Warning'" /></el-icon>
        <span v-if="llmConfigured">{{ $t('settings.llmConfigured') }} — <strong>{{ llmForm.model }}</strong></span>
        <span v-else>{{ $t('settings.llmNotConfigured') }}</span>
      </div>

      <el-form :model="llmForm" label-position="top" size="small">
        <el-form-item :label="$t('settings.llmApiBase')">
          <el-input v-model="llmForm.api_base" placeholder="https://api.openai.com/v1" />
        </el-form-item>
        <el-form-item :label="$t('settings.llmApiKey')">
          <el-input v-model="llmForm.api_key" type="password" show-password
            :placeholder="llmHasKey ? '••••••••' : 'sk-...'" />
        </el-form-item>
        <el-form-item :label="$t('settings.llmModel')">
          <el-select v-model="llmForm.model" filterable allow-create default-first-option
            :placeholder="$t('settings.selectModel')" style="width: 100%;">
            <el-option-group v-for="group in modelGroups" :key="group.provider" :label="group.provider">
              <el-option v-for="m in group.models" :key="m.id" :value="m.id" :label="m.name">
                <span>{{ m.name }}</span>
                <span style="font-size:12px;color:#909399;margin-left:8px;">{{ m.description }}</span>
              </el-option>
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item :label="$t('settings.defaultModel')">
          <el-select v-model="llmForm.default_model" filterable allow-create default-first-option
            :placeholder="$t('settings.defaultModelHint')" style="width: 100%;">
            <el-option v-for="m in presetModels" :key="m.id" :value="m.id" :label="m.name">
              <span>{{ m.name }}</span>
              <span style="font-size:12px;color:#909399;margin-left:8px;">{{ m.provider }}</span>
            </el-option>
          </el-select>
        </el-form-item>
        <div class="llm-actions">
          <el-button type="primary" @click="saveLLMConfig" :loading="savingLLM">
            {{ $t('settings.save') }}
          </el-button>
          <el-button @click="testLLMConfig" :loading="testingLLM" :disabled="!llmHasKey">
            {{ $t('settings.test') }}
          </el-button>
        </div>
      </el-form>
    </div>

    <div class="card">
      <h3>{{ $t('settings.about') }}</h3>
      <p>{{ $t('settings.aboutDesc') }}</p>
      <p>{{ $t('settings.techStack') }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { planApi, reminderApi, configApi } from '../api/client'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const plans = ref([])
const llmForm = ref({ api_base: '', api_key: '', model: '', default_model: '' })
const savingLLM = ref(false)
const testingLLM = ref(false)
const llmHasKey = ref(false)
const llmConfigured = ref(false)
const presetModels = ref([])
const channels = ref([
  { key: 'feishu', icon: 'ChatDotRound', enabled: false, testing: false },
  { key: 'dingtalk', icon: 'Message', enabled: false, testing: false },
  { key: 'windows', icon: 'Monitor', enabled: true, testing: false },
])

const modelGroups = computed(() => {
  const groups = {}
  for (const m of presetModels.value) {
    if (!groups[m.provider]) groups[m.provider] = { provider: m.provider, models: [] }
    groups[m.provider].models.push(m)
  }
  return Object.values(groups)
})

const loadPlans = async () => {
  const { data } = await planApi.list()
  plans.value = data
}

const toggleChannel = async (ch) => {
  const status = ch.enabled ? t('settings.enabled') : t('settings.disabled')
  ElMessage.success(`${t('settings.' + ch.key)} ${status}`)
}

const testChannel = async (key) => {
  const ch = channels.value.find(c => c.key === key)
  ch.testing = true
  try {
    const { data } = await reminderApi.test(key)
    if (data.success) {
      ElMessage.success(t('settings.testSuccess', { name: t('settings.' + key) }))
    } else {
      ElMessage.error(`${t('settings.' + key)} failed: ${data.message}`)
    }
  } catch (e) {
    ElMessage.error(t('settings.testFailed', { name: t('settings.' + key) }))
  } finally {
    ch.testing = false
  }
}

const deletePlan = async (id) => {
  await planApi.delete(id)
  ElMessage.success(t('settings.planDeleted'))
  loadPlans()
}

const loadLLMConfig = async () => {
  try {
    const { data } = await configApi.get()
    llmForm.value = {
      api_base: data.api_base,
      api_key: '',
      model: data.model,
      default_model: data.default_model || data.model,
    }
    llmHasKey.value = data.has_key
    llmConfigured.value = data.configured
  } catch (e) { console.error(e) }
}

const loadModels = async () => {
  try {
    const { data } = await configApi.models()
    presetModels.value = data.models || []
  } catch (e) { console.error(e) }
}

const saveLLMConfig = async () => {
  savingLLM.value = true
  try {
    const key = (!llmForm.value.api_key || llmForm.value.api_key.includes('•')) ? '' : llmForm.value.api_key
    await configApi.update({ ...llmForm.value, api_key: key })
    ElMessage.success(t('settings.llmSaved'))
    llmHasKey.value = true
    llmConfigured.value = true
  } catch (e) {
    ElMessage.error(t('settings.llmSaveFailed'))
  } finally {
    savingLLM.value = false
  }
}

const testLLMConfig = async () => {
  testingLLM.value = true
  try {
    const { data } = await configApi.test()
    if (data.success) {
      ElMessage.success(data.message)
    } else {
      ElMessage.error(data.message)
    }
  } catch (e) {
    ElMessage.error(t('settings.testFailed', { name: 'LLM' }))
  } finally {
    testingLLM.value = false
  }
}

onMounted(() => { loadPlans(); loadLLMConfig(); loadModels() })
</script>

<style scoped>
.settings-view { max-width: 600px; margin: 0 auto; }
.settings-view h2 { margin-bottom: 24px; }
.card { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card h3 { font-size: 16px; margin-bottom: 16px; }
.channel-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.channel-info { display: flex; gap: 12px; align-items: center; }
.channel-name { font-weight: 600; }
.channel-desc { font-size: 12px; color: #909399; }
.channel-actions { display: flex; gap: 8px; align-items: center; }
.plan-item { display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.plan-progress { margin-left: 8px; color: #409eff; font-size: 14px; }
.llm-status {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px; border-radius: 8px; margin-bottom: 16px;
  background: #fef0f0; color: #f56c6c; font-size: 13px;
}
.llm-status.configured { background: #f0f9eb; color: #67c23a; }
.llm-actions { display: flex; gap: 8px; }

@media (max-width: 480px) {
  .settings-view {
    max-width: 100%;
    padding: 0 4px;
  }

  .channel-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .channel-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .plan-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .plan-item > div:last-child {
    width: 100%;
    display: flex;
    gap: 8px;
  }

  .plan-item > div:last-child .el-button {
    flex: 1;
  }
}
</style>
