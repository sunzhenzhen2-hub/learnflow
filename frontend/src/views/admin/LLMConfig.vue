<template>
  <div class="llm-config">
    <el-form :model="form" label-width="120px" style="max-width: 600px;">
      <el-form-item :label="$t('admin.llmApiBase')">
        <el-input v-model="form.api_base" placeholder="https://api.openai.com/v1" />
      </el-form-item>
      <el-form-item :label="$t('admin.llmApiKey')">
        <el-input v-model="form.api_key" type="password" show-password placeholder="sk-..." />
      </el-form-item>
      <el-form-item :label="$t('admin.llmModel')">
        <el-input v-model="form.model" placeholder="gpt-4o-mini" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="saveConfig" :loading="saving">
          {{ $t('admin.save') }}
        </el-button>
        <el-button @click="testConfig" :loading="testing">
          {{ $t('admin.test') }}
        </el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { configApi } from '../../api/client'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const form = ref({
  api_base: '',
  api_key: '',
  model: '',
})

const saving = ref(false)
const testing = ref(false)

const loadConfig = async () => {
  try {
    const { data } = await configApi.get()
    form.value = {
      api_base: data.api_base || '',
      api_key: '',
      model: data.model || '',
    }
  } catch (e) {
    console.error('Failed to load LLM config:', e)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await configApi.update(form.value)
    ElMessage.success(t('admin.llmSaved'))
  } catch (e) {
    ElMessage.error(t('admin.llmSaveFailed'))
  } finally {
    saving.value = false
  }
}

const testConfig = async () => {
  testing.value = true
  try {
    await configApi.test()
    ElMessage.success(t('admin.testSuccess'))
  } catch (e) {
    ElMessage.error(t('admin.testFailed'))
  } finally {
    testing.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.llm-config {
  padding: 20px 0;
}
</style>
