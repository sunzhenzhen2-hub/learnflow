<template>
  <view class="settings-page">
    <!-- Plan Management -->
    <view class="section">
      <text class="section-title">学习计划</text>
      <view v-for="plan in plans" :key="plan.id" class="plan-item">
        <view class="plan-info">
          <text class="plan-topic">{{ plan.topic }}</text>
          <text class="plan-meta">{{ plan.total_weeks }}周 · {{ plan.weekly_hours }}h/周 · {{ plan.status }}</text>
        </view>
        <view class="plan-actions">
          <text class="action-link" @click="goToLearn(plan.id)">进入</text>
          <text class="action-link danger" @click="deletePlan(plan.id)">删除</text>
        </view>
      </view>
      <view v-if="plans.length === 0" class="empty">
        <text>暂无学习计划</text>
      </view>
    </view>

    <!-- Notification Settings -->
    <view class="section">
      <text class="section-title">消息提醒</text>
      <view class="setting-item">
        <text class="setting-label">微信订阅消息</text>
        <switch :checked="wxNotify" @change="toggleWxNotify" color="#409eff" />
      </view>
      <view class="setting-item">
        <text class="setting-label">每日学习提醒</text>
        <switch :checked="dailyReminder" @change="toggleReminder" color="#409eff" />
      </view>
      <view class="setting-item" v-if="dailyReminder">
        <text class="setting-label">提醒时间</text>
        <picker mode="time" :value="reminderTime" @change="e => reminderTime = e.detail.value">
          <text class="time-value">{{ reminderTime }}</text>
        </picker>
      </view>
    </view>

    <!-- AI Model Configuration -->
    <view class="section">
      <text class="section-title">AI 模型配置</text>
      <!-- Status indicator -->
      <view class="llm-status" :class="{ configured: llmConfigured }">
        <text class="llm-status-text">{{ llmConfigured ? '已配置 — ' + llmForm.model : '未配置' }}</text>
      </view>
      <!-- API Base -->
      <view class="setting-item">
        <text class="setting-label">API 地址</text>
        <input class="setting-input" v-model="llmForm.api_base" placeholder="https://api.openai.com/v1" />
      </view>
      <!-- Model picker -->
      <view class="setting-item">
        <text class="setting-label">模型</text>
        <picker :range="modelNames" @change="onModelPick">
          <text class="model-pick-value">{{ llmForm.model || '选择模型' }}</text>
        </picker>
      </view>
      <!-- Default model picker -->
      <view class="setting-item">
        <text class="setting-label">默认模型</text>
        <picker :range="modelNames" @change="onDefaultModelPick">
          <text class="model-pick-value">{{ llmForm.default_model || '同上方模型' }}</text>
        </picker>
      </view>
      <!-- Actions -->
      <view class="llm-actions">
        <button class="btn-primary" size="mini" @click="saveLLMConfig" :loading="savingLLM">保存</button>
        <button class="btn-outline" size="mini" @click="testLLMConfig" :loading="testingLLM" :disabled="!llmHasKey">测试</button>
      </view>
    </view>

    <!-- About -->
    <view class="section">
      <text class="section-title">关于</text>
      <view class="about-card">
        <text class="about-name">LearnFlow v0.1.0</text>
        <text class="about-desc">AI 驱动的学习执行系统</text>
        <text class="about-desc">强制输出闭环 · 学习阶梯 · 二八法则</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { planApi, reminderApi, authApi, configApi } from '../../api/client'

const plans = ref([])
const wxNotify = ref(false)
const dailyReminder = ref(true)
const reminderTime = ref('09:00')
const wxTemplateId = 'TEMPLATE_ID_HERE'  // Replace with actual template ID from WeChat MP console

// LLM Config state
const llmForm = ref({ api_base: '', model: '', default_model: '' })
const llmConfigured = ref(false)
const llmHasKey = ref(false)
const savingLLM = ref(false)
const testingLLM = ref(false)
const presetModels = ref([])

const modelNames = computed(() => {
  if (presetModels.value.length === 0) {
    return ['gpt-4o-mini', 'gpt-4o', 'mimo-v2.5', 'deepseek-chat', 'qwen-turbo']
  }
  return presetModels.value.map(m => `${m.name} (${m.id})`)
})

function onModelPick(e) {
  const idx = e.detail.value
  if (presetModels.value.length > 0 && idx < presetModels.value.length) {
    llmForm.value.model = presetModels.value[idx].id
  }
}

function onDefaultModelPick(e) {
  const idx = e.detail.value
  if (presetModels.value.length > 0 && idx < presetModels.value.length) {
    llmForm.value.default_model = presetModels.value[idx].id
  }
}

async function loadLLMConfig() {
  try {
    const { data } = await configApi.get()
    llmForm.value = { api_base: data.api_base, model: data.model, default_model: data.default_model || data.model }
    llmConfigured.value = data.configured
    llmHasKey.value = data.has_key
  } catch (e) { console.error('Failed to load LLM config:', e) }
}

async function loadModels() {
  try {
    const { data } = await configApi.models()
    presetModels.value = data.models || []
  } catch (e) { console.error('Failed to load models:', e) }
}

async function saveLLMConfig() {
  savingLLM.value = true
  try {
    await configApi.update({ ...llmForm.value, api_key: '' })
    llmConfigured.value = true
    llmHasKey.value = true
    uni.showToast({ title: '已保存', icon: 'success' })
  } catch (e) {
    uni.showToast({ title: '保存失败', icon: 'none' })
  } finally {
    savingLLM.value = false
  }
}

async function testLLMConfig() {
  testingLLM.value = true
  try {
    const { data } = await configApi.test()
    uni.showToast({ title: data.success ? '连接成功' : data.message, icon: 'none', duration: 3000 })
  } catch (e) {
    uni.showToast({ title: '测试失败', icon: 'none' })
  } finally {
    testingLLM.value = false
  }
}

function goToLearn(planId) {
  uni.navigateTo({ url: `/pages/learn/index?planId=${planId}` })
}

async function deletePlan(id) {
  uni.showModal({
    title: '确认删除',
    content: '删除后无法恢复，确定要删除吗？',
    success: async (res) => {
      if (res.confirm) {
        try {
          await planApi.delete(id)
          plans.value = plans.value.filter(p => p.id !== id)
          uni.showToast({ title: '已删除', icon: 'success' })
        } catch (e) {
          uni.showToast({ title: '删除失败', icon: 'none' })
        }
      }
    }
  })
}

function toggleWxNotify(e) {
  wxNotify.value = e.detail.value
  if (wxNotify.value) {
    // #ifdef MP-WEIXIN
    uni.requestSubscribeMessage({
      tmplIds: [wxTemplateId],
      success: async (res) => {
        if (res[wxTemplateId] === 'accept') {
          // User granted permission, create reminder on backend
          const openid = uni.getStorageSync('openid') || ''
          const activePlan = plans.value.find(p => p.status === 'active')
          if (activePlan && openid) {
            try {
              await reminderApi.add(activePlan.id, {
                channel: 'wx_subscribe',
                channel_config: {
                  openid: openid,
                  template_id: wxTemplateId
                }
              })
              uni.showToast({ title: '\u5df2\u5f00\u542f\u8ba2\u9605\u6d88\u606f', icon: 'success' })
            } catch (err) {
              console.error('Failed to create wx reminder:', err)
              uni.showToast({ title: '\u5f00\u542f\u5931\u8d25', icon: 'none' })
            }
          } else if (!openid) {
            uni.showToast({ title: '\u8bf7\u5148\u767b\u5f55', icon: 'none' })
            wxNotify.value = false
          }
        } else {
          wxNotify.value = false
          uni.showToast({ title: '\u672a\u6388\u6743', icon: 'none' })
        }
      },
      fail: () => {
        wxNotify.value = false
      }
    })
    // #endif
    // #ifndef MP-WEIXIN
    uni.showToast({ title: '\u4ec5\u5fae\u4fe1\u5c0f\u7a0b\u5e8f\u652f\u6301', icon: 'none' })
    wxNotify.value = false
    // #endif
  }
}

function toggleReminder(e) {
  dailyReminder.value = e.detail.value
}

onMounted(async () => {
  try {
    const { data } = await planApi.list()
    plans.value = data
  } catch (e) {
    console.error('Failed to load plans:', e)
  }
  loadLLMConfig()
  loadModels()
})
</script>

<style scoped>
.settings-page { padding: 24rpx; min-height: 100vh; background: #f5f7fa; }
.section { margin-bottom: 32rpx; }
.section-title { font-size: 28rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 16rpx; }
.plan-item {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 20rpx 24rpx; border-radius: 12rpx; margin-bottom: 12rpx;
}
.plan-topic { font-size: 28rpx; font-weight: 600; color: #303133; display: block; }
.plan-meta { font-size: 22rpx; color: #909399; margin-top: 4rpx; }
.plan-actions { display: flex; gap: 20rpx; }
.action-link { font-size: 26rpx; color: #409eff; }
.action-link.danger { color: #f56c6c; }
.setting-item {
  display: flex; justify-content: space-between; align-items: center;
  background: #fff; padding: 20rpx 24rpx; border-bottom: 1rpx solid #ebeef5;
}
.setting-item:first-of-type { border-radius: 12rpx 12rpx 0 0; }
.setting-item:last-of-type { border-radius: 0 0 12rpx 12rpx; border-bottom: none; }
.setting-label { font-size: 28rpx; color: #303133; }
.time-value { font-size: 28rpx; color: #409eff; }
.about-card { background: #fff; border-radius: 12rpx; padding: 24rpx; text-align: center; }
.about-name { font-size: 30rpx; font-weight: 700; color: #303133; display: block; margin-bottom: 8rpx; }
.about-desc { font-size: 24rpx; color: #909399; display: block; margin-top: 4rpx; }
.empty { text-align: center; padding: 40rpx; color: #909399; font-size: 26rpx; }
.llm-status {
  padding: 16rpx 24rpx; border-radius: 12rpx 12rpx 0 0; background: #fef0f0;
}
.llm-status.configured { background: #f0f9eb; }
.llm-status-text { font-size: 24rpx; color: #f56c6c; }
.llm-status.configured .llm-status-text { color: #67c23a; }
.setting-input {
  font-size: 26rpx; color: #606266; text-align: right; flex: 1; margin-left: 20rpx;
}
.model-pick-value { font-size: 26rpx; color: #409eff; }
.llm-actions {
  display: flex; gap: 16rpx; padding: 16rpx 24rpx; background: #fff;
  border-radius: 0 0 12rpx 12rpx;
}
.btn-primary {
  background: #409eff; color: #fff; border-radius: 8rpx; font-size: 26rpx;
  padding: 12rpx 32rpx; border: none;
}
.btn-outline {
  background: #fff; color: #409eff; border: 1rpx solid #409eff;
  border-radius: 8rpx; font-size: 26rpx; padding: 12rpx 32rpx;
}
</style>
