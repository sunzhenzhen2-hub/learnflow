import { ref, onMounted, onUnmounted, computed } from 'vue'

// 使用更严格的移动端检测
const isMobile = ref(false)

function checkDevice() {
  const width = window.innerWidth
  const ua = navigator.userAgent.toLowerCase()
  
  // 检测移动设备或小屏幕
  const isMobileUA = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(ua)
  const isSmallScreen = width < 768
  
  isMobile.value = isMobileUA || isSmallScreen
}

export function useDevice() {
  const isDesktop = computed(() => !isMobile.value)

  onMounted(() => {
    checkDevice()
    window.addEventListener('resize', checkDevice)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', checkDevice)
  })

  return {
    isMobile: computed(() => isMobile.value),
    isDesktop,
  }
}
