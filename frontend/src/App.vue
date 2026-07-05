<template>
  <el-config-provider :locale="elLocale">
    <component :is="currentLayout" />
  </el-config-provider>
</template>

<script setup>
import { computed, defineAsyncComponent } from 'vue'
import { useI18n } from 'vue-i18n'
import { useDevice } from './composables/useDevice'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enUs from 'element-plus/es/locale/lang/en'

const { isMobile } = useDevice()
const { locale } = useI18n()

const elLocale = computed(() => locale.value === 'zh-CN' ? zhCn : enUs)

const MobileLayout = defineAsyncComponent(() => import('./layouts/MobileLayout.vue'))
const PcLayout = defineAsyncComponent(() => import('./layouts/PcLayout.vue'))

const currentLayout = computed(() => isMobile.value ? MobileLayout : PcLayout)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fa;
  color: #303133;
}
</style>
