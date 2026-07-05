<template>
  <div class="feishu-config">
    <el-form :model="form" label-width="120px" style="max-width: 600px;">
      <el-form-item :label="$t('admin.feishuAppId')">
        <el-input v-model="form.app_id" placeholder="飞书应用 App ID" />
      </el-form-item>
      <el-form-item :label="$t('admin.feishuAppSecret')">
        <el-input v-model="form.app_secret" type="password" show-password placeholder="飞书应用 App Secret" />
      </el-form-item>
      <el-form-item :label="$t('admin.feishuVerificationToken')">
        <el-input v-model="form.verification_token" placeholder="事件订阅 Verification Token" />
      </el-form-item>
      <el-form-item :label="$t('admin.feishuEncryptKey')">
        <el-input v-model="form.encrypt_key" placeholder="事件订阅 Encrypt Key（可选）" />
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
import { reminderApi } from '../../api/client'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const form = ref({
  app_id: '',
  app_secret: '',
  verification_token: '',
  encrypt_key: '',
})

const saving = ref(false)
const testing = ref(false)

const loadConfig = async () => {
  try {
    const { data } = await reminderApi.getConfig('feishu')
    if (data) {
      form.value = {
        app_id: data.app_id || '',
        app_secret: '',
        verification_token: data.verification_token || '',
        encrypt_key: data.encrypt_key || '',
      }
    }
  } catch (e) {
    console.error('Failed to load Feishu config:', e)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await reminderApi.saveConfig('feishu', form.value)
    ElMessage.success(t('admin.feishuSaved'))
  } catch (e) {
    ElMessage.error(t('admin.feishuSaveFailed'))
  } finally {
    saving.value = false
  }
}

const testConfig = async () => {
  testing.value = true
  try {
    await reminderApi.test('feishu')
    ElMessage.success(t('admin.testSuccess', { name: t('admin.feishu') }))
  } catch (e) {
    ElMessage.error(t('admin.testFailed', { name: t('admin.feishu') }))
  } finally {
    testing.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.feishu-config {
  padding: 20px 0;
}
</style>
