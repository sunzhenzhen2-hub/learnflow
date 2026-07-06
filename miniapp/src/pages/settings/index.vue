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
import { ref, onMounted } from 'vue'
import { planApi, reminderApi, authApi } from '../../api/client'

const plans = ref([])
const wxNotify = ref(false)
const dailyReminder = ref(true)
const reminderTime = ref('09:00')
const wxTemplateId = 'TEMPLATE_ID_HERE'  // Replace with actual template ID from WeChat MP console

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
</style>
