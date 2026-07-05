<template>
  <el-container class="pc-layout">
    <!-- Sidebar -->
    <el-aside width="220px" class="sidebar">
      <div class="sidebar-header">
        <h1 class="logo" @click="$router.push('/')">
          <el-icon><Reading /></el-icon>
          LearnFlow
        </h1>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>{{ $t('nav.home') }}</span>
        </el-menu-item>
        <el-menu-item index="/learn-active" @click="goToLearn">
          <el-icon><EditPen /></el-icon>
          <span>{{ $t('nav.learn') }}</span>
        </el-menu-item>
        <el-menu-item index="/wizard">
          <el-icon><Plus /></el-icon>
          <span>{{ $t('nav.newPlan') }}</span>
        </el-menu-item>
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>{{ $t('nav.profile') }}</span>
        </el-menu-item>
        <el-menu-item index="/admin">
          <el-icon><Setting /></el-icon>
          <span>{{ $t('nav.admin') }}</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Main Content -->
    <el-container>
      <el-header class="pc-header">
        <div class="header-right">
          <el-dropdown trigger="click" @command="switchLang">
            <el-button text size="small">
              <el-icon><Flag /></el-icon>
              {{ $t('lang.' + currentLangShort) }}
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="zh-CN" :disabled="locale === 'zh-CN'">中文</el-dropdown-item>
                <el-dropdown-item command="en-US" :disabled="locale === 'en-US'">English</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="pc-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { usePlanStore } from '../stores/plan'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import enUs from 'element-plus/es/locale/lang/en'

const router = useRouter()
const route = useRoute()
const planStore = usePlanStore()
const { locale } = useI18n()

const elLocale = computed(() => locale.value === 'zh-CN' ? zhCn : enUs)
const currentLangShort = computed(() => locale.value === 'zh-CN' ? 'zh' : 'en')

const switchLang = (lang) => {
  locale.value = lang
}

const goToLearn = () => {
  if (planStore.activePlan) {
    router.push(`/learn/${planStore.activePlan.id}`)
  } else {
    router.push('/wizard')
  }
}
</script>

<style scoped>
.pc-layout {
  min-height: 100vh;
}

.sidebar {
  background: #fff;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #ebeef5;
}

.logo {
  font-size: 22px;
  font-weight: 700;
  color: #409eff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

.sidebar-menu {
  border-right: none;
  flex: 1;
}

.pc-header {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  height: 60px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.pc-main {
  padding: 24px;
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
