<template>
  <div class="dingtalk-config">
    <el-form :model="form" label-width="120px" style="max-width: 600px;">
      <el-form-item :label="$t('admin.dingtalkAppKey')">
        <el-input v-model="form.app_key" placeholder="钉钉应用 AppKey" />
      </el-form-item>
      <el-form-item :label="$t('admin.dingtalkAppSecret')">
        <el-input v-model="form.app_secret" type="password" show-password placeholder="钉钉应用 AppSecret" />
      </el-form-item>
      <el-form-item :label="$t('admin.dingtalkAgentId')">
        <el-input v-model="form.agent_id" placeholder="钉钉应用 AgentId" />
      </el-form-item>
      <el-form-item :label="$t('admin.dingtalkRobotCode')">
        <el-input v-model="form.robot_code" placeholder="机器人代码（可选）" />
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
  app_key: '',
  app_secret: '',
  agent_id: '',
  robot_code: '',
})

const saving = ref(false)
const testing = ref(false)

const loadConfig = async () => {
  try {
    const { data } = await reminderApi.getConfig('dingtalk')
    if (data) {
      form.value = {
        app_key: data.app_key || '',
        app_secret: '',
        agent_id: data.agent_id || '',
        robot_code: data.robot_code || '',
      }
    }
  } catch (e) {
    console.error('Failed to load DingTalk config:', e)
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await reminderApi.saveConfig('dingtalk', form.value)
    ElMessage.success(t('admin.dingtalkSaved'))
  } catch (e) {
    ElMessage.error(t('admin.dingtalkSaveFailed'))
  } finally {
    saving.value = false
  }
}

const testConfig = async () => {
  testing.value = true
  try {
    await reminderApi.test('dingtalk')
    ElMessage.success(t('admin.testSuccess', { name: t('admin.dingtalk') }))
  } catch (e) {
    ElMessage.error(t('admin.testFailed', { name: t('admin.dingtalk') }))
  } finally {
    testing.value = false
  }
}

onMounted(loadConfig)
</script>

<style scoped>
.dingtalk-config {
  padding: 20px 0;
}
</style>
