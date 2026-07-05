import { ref, onMounted, onUnmounted, computed } from 'vue'

const MOBILE_BREAKPOINT = 768

const isMobile = ref(false)

function checkDevice() {
  isMobile.value = window.innerWidth < MOBILE_BREAKPOINT
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
