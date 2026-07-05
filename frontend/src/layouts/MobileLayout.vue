<template>
  <el-config-provider :locale="elLocale">
    <div class="mobile-layout">
      <el-container>
        <el-header class="mobile-header">
          <div class="header-left">
            <h1 class="logo" @click="$router.push('/')">
              <el-icon><Reading /></el-icon>
              LearnFlow
            </h1>
          </div>
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

        <el-main class="mobile-main">
          <router-view />
        </el-main>

        <el-footer class="mobile-footer">
          <div class="bottom-nav">
            <div
              class="nav-item"
              :class="{ active: $route.name === 'Dashboard' }"
              @click="$router.push('/')"
            >
              <el-icon><HomeFilled /></el-icon>
              <span>{{ $t('nav.home') }}</span>
            </div>
            <div
              class="nav-item"
              :class="{ active: $route.name === 'Learn' }"
              @click="goToLearn"
            >
              <el-icon><EditPen /></el-icon>
              <span>{{ $t('nav.learn') }}</span>
            </div>
            <div
              class="nav-item"
              :class="{ active: $route.name === 'Wizard' }"
              @click="$router.push('/wizard')"
            >
              <el-icon><Plus /></el-icon>
              <span>{{ $t('nav.newPlan') }}</span>
            </div>
            <div
              class="nav-item"
              :class="{ active: $route.name === 'Profile' }"
              @click="$router.push('/profile')"
            >
              <el-icon><User /></el-icon>
              <span>{{ $t('nav.profile') }}</span>
            </div>
          </div>
        </el-footer>
      </el-container>
    </div>
  </el-config-provider>
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
.mobile-layout {
  min-height: 100vh;
  max-width: 100%;
  background: #f5f7fa;
}

.mobile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #409eff;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.mobile-main {
  padding: 16px;
  min-height: calc(100vh - 120px);
  padding-bottom: 80px;
  background: #fff;
}

.mobile-footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #ebeef5;
  padding: 8px 0;
  z-index: 100;
}

.bottom-nav {
  display: flex;
  justify-content: space-around;
  align-items: center;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 4px 16px;
  cursor: pointer;
  color: #909399;
  font-size: 12px;
  transition: color 0.2s;
}

.nav-item.active {
  color: #409eff;
}

.nav-item .el-icon {
  font-size: 20px;
}
</style>
