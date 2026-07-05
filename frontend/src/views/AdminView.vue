<template>
  <div class="admin-view">
    <h2>{{ $t('admin.title') }}</h2>
    <el-tabs v-model="activeTab" type="border-card" @tab-click="handleTabClick">
      <el-tab-pane :label="$t('admin.llmConfig')" name="llm">
        <router-view v-if="activeTab === 'llm'" />
        <LLMConfig v-else />
      </el-tab-pane>
      <el-tab-pane :label="$t('admin.dingtalk')" name="dingtalk">
        <router-view v-if="activeTab === 'dingtalk'" />
        <DingTalkConfig v-else />
      </el-tab-pane>
      <el-tab-pane :label="$t('admin.feishu')" name="feishu">
        <router-view v-if="activeTab === 'feishu'" />
        <FeishuConfig v-else />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LLMConfig from './admin/LLMConfig.vue'
import DingTalkConfig from './admin/DingTalkConfig.vue'
import FeishuConfig from './admin/FeishuConfig.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const activeTab = ref('llm')

const handleTabClick = (tab) => {
  router.push(`/admin/${tab.props.name}`)
}

onMounted(() => {
  if (route.path.includes('/admin/')) {
    activeTab.value = route.path.split('/admin/')[1] || 'llm'
  }
})
</script>

<style scoped>
.admin-view {
  max-width: 800px;
  margin: 0 auto;
}

.admin-view h2 {
  margin-bottom: 20px;
  color: #303133;
}
</style>
