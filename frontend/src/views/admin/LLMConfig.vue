<template>
  <div class="llm-config">
    <!-- 配置状态卡片 -->
    <div class="status-card" :class="{ configured: configStatus.configured }">
      <div class="status-icon">
        <el-icon :size="28"><component :is="configStatus.configured ? 'CircleCheck' : 'Warning'" /></el-icon>
      </div>
      <div class="status-info">
        <div class="status-title">{{ configStatus.configured ? $t('admin.llmConfigured') : $t('admin.llmNotConfigured') }}</div>
        <div class="status-detail" v-if="configStatus.configured">
          {{ $t('admin.currentModel') }}: <strong>{{ configStatus.model }}</strong>
          <span v-if="configStatus.defaultModel && configStatus.defaultModel !== configStatus.model">
            ({{ $t('admin.defaultModel') }}: {{ configStatus.defaultModel }})
          </span>
        </div>
        <div class="status-detail" v-else>
          {{ configStatus.hasKey ? $t('admin.hasApiKey') : $t('admin.noApiKey') }}
        </div>
      </div>
    </div>

    <!-- 配置表单 -->
    <el-form :model="form" label-width="120px" style="max-width: 600px;">
      <el-form-item :label="$t('admin.llmApiBase')">
        <el-input v-model="form.api_base" placeholder="https://api.openai.com/v1" />
      </el-form-item>

      <el-form-item :label="$t('admin.llmApiKey')">
        <el-input v-model="form.api_key" type="password" show-password
          :placeholder="hasExistingKey ? '•••••••• (留空保留原值)' : 'sk-...'" />
      </el-form-item>

      <!-- 模型选择 -->
      <el-form-item :label="$t('admin.llmModel')">
        <el-select v-model="form.model" filterable allow-create
          default-first-option :placeholder="$t('admin.selectModel')"
          style="width: 100%;" @change="onModelChange">
          <el-option-group v-for="group in modelGroups" :key="group.provider" :label="group.provider">
            <el-option v-for="m in group.models" :key="m.id" :value="m.id" :label="m.name">
              <div class="model-option">
                <span>{{ m.name }}</span>
                <span class="model-desc">{{ m.description }}</span>
              </div>
            </el-option>
          </el-option-group>
        </el-select>
      </el-form-item>

      <!-- 默认模型 -->
      <el-form-item :label="$t('admin.defaultModel')">
        <el-select v-model="form.default_model" filterable allow-create
          default-first-option :placeholder="$t('admin.defaultModelHint')" style="width: 100%;">
          <el-option v-for="m in allModels" :key="m.id" :value="m.id" :label="m.name">
            <div class="model-option">
              <span>{{ m.name }}</span>
              <span class="model-desc">{{ m.provider }}</span>
            </div>
          </el-option>
        </el-select>
        <div class="form-hint">{{ $t('admin.defaultModelDesc') }}</div>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="saveConfig" :loading="saving">
          {{ $t('admin.save') }}
        </el-button>
        <el-button @click="testConfig" :loading="testing" :disabled="!configStatus.hasKey">
          {{ $t('admin.test') }}
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 测试结果 -->
    <div v-if="testResult" class="test-result" :class="{ success: testResult.success }">
      <el-icon :size="18"><component :is="testResult.success ? 'CircleCheck' : 'CircleClose'" /></el-icon>
      <span>{{ testResult.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { configApi } from '../../api/client'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const form = ref({
  api_base: '',
  api_key: '',
  model: '',
  default_model: '',
})

const hasExistingKey = ref(false)
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)
const presetModels = ref([])

const configStatus = ref({
  configured: false,
  hasKey: false,
  model: '',
  defaultModel: '',
})

// 按 provider 分组
const modelGroups = computed(() => {
  const groups = {}
  for (const m of presetModels.value) {
    if (!groups[m.provider]) groups[m.provider] = { provider: m.provider, models: [] }
    groups[m.provider].models.push(m)
  }
  return Object.values(groups)
})

const allModels = computed(() => presetModels.value)

function onModelChange(val) {
  // 选择模型时同步到默认模型（如果默认模型未设置）
  if (!form.value.default_model) {
    form.value.default_model = val
  }
}

const loadConfig = async () => {
  try {
    const { data } = await configApi.get()
    form.value = {
      api_base: data.api_base || '',
      api_key: '',
      model: data.model || '',
      default_model: data.default_model || data.model || '',
    }
    hasExistingKey.value = data.has_key
    configStatus.value = {
      configured: data.configured,
      hasKey: data.has_key,
      model: data.model,
      defaultModel: data.default_model,
    }
  } catch (e) {
    console.error('Failed to load LLM config:', e)
  }
}

const loadModels = async () => {
  try {
    const { data } = await configApi.models()
    presetModels.value = data.models || []
  } catch (e) {
    console.error('Failed to load models:', e)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    const payload = { ...form.value }
    // 如果 key 没改（留空或还是占位符），发送空字符串让后端保留原值
    if (!payload.api_key || payload.api_key.includes('•')) {
      payload.api_key = ''
    }
    await configApi.update(payload)
    ElMessage.success(t('admin.llmSaved'))
    hasExistingKey.value = true
    configStatus.value.configured = true
    configStatus.value.model = form.value.model
    configStatus.value.defaultModel = form.value.default_model
    configStatus.value.hasKey = true
  } catch (e) {
    ElMessage.error(t('admin.llmSaveFailed'))
  } finally {
    saving.value = false
  }
}

const testConfig = async () => {
  testing.value = true
  testResult.value = null
  try {
    const { data } = await configApi.test()
    testResult.value = data
    if (data.success) {
      ElMessage.success(data.message)
    } else {
      ElMessage.error(data.message)
    }
  } catch (e) {
    testResult.value = { success: false, message: e.message || '连接失败' }
    ElMessage.error(t('admin.testFailed', { name: 'LLM' }))
  } finally {
    testing.value = false
  }
}

onMounted(() => {
  loadConfig()
  loadModels()
})
</script>

<style scoped>
.llm-config { padding: 20px 0; }

.status-card {
  display: flex; align-items: center; gap: 16px;
  padding: 16px 20px; border-radius: 12px; margin-bottom: 24px;
  background: #fef0f0; border: 1px solid #fde2e2; color: #f56c6c;
}
.status-card.configured {
  background: #f0f9eb; border-color: #e1f3d8; color: #67c23a;
}
.status-icon { display: flex; align-items: center; }
.status-title { font-size: 15px; font-weight: 600; }
.status-detail { font-size: 13px; margin-top: 4px; opacity: 0.85; }

.model-option {
  display: flex; justify-content: space-between; align-items: center; width: 100%;
}
.model-desc { font-size: 12px; color: #909399; margin-left: 8px; }

.form-hint { font-size: 12px; color: #909399; margin-top: 4px; line-height: 1.5; }

.test-result {
  margin-top: 16px; padding: 12px 16px; border-radius: 8px;
  display: flex; align-items: center; gap: 8px;
  background: #fef0f0; color: #f56c6c; border: 1px solid #fde2e2;
}
.test-result.success {
  background: #f0f9eb; color: #67c23a; border-color: #e1f3d8;
}
</style>
