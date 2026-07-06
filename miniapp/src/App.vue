<script>
import { authApi } from './api/client'

export default {
  globalData: {
    apiUrl: 'http://localhost:8001/api',
    userInfo: null,
  },
  onLaunch() {
    console.log('[LearnFlow] App launched')
    const token = uni.getStorageSync('token')
    if (token) {
      this.globalData.userInfo = { token }
    } else {
      this.autoLogin()
    }
  },
  methods: {
    async autoLogin() {
      // #ifdef MP-WEIXIN
      try {
        const [err, res] = await uni.login({ provider: 'weixin' })
        if (res && res.code) {
          const { data } = await authApi.wxLogin(res.code)
          uni.setStorageSync('token', data.token)
          uni.setStorageSync('openid', data.user_id)
          this.globalData.userInfo = { token: data.token }
          console.log('[LearnFlow] WeChat login success')
        }
      } catch (e) {
        console.warn('[LearnFlow] WeChat login failed:', e)
      }
      // #endif
      // #ifndef MP-WEIXIN
      // Dev mode: auto dev-login
      try {
        const { data } = await authApi.devLogin()
        uni.setStorageSync('token', data.token)
        uni.setStorageSync('openid', data.user_id)
        this.globalData.userInfo = { token: data.token }
        console.log('[LearnFlow] Dev login success')
      } catch (e) {
        console.warn('[LearnFlow] Dev login failed:', e)
      }
      // #endif
    }
  },
  onShow() {
    console.log('[LearnFlow] App shown')
  },
  onHide() {
    console.log('[LearnFlow] App hidden')
  }
}
</script>

<style>
page {
  background-color: #f5f7fa;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #303133;
}
</style>
