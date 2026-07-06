<template>
  <view class="video-player">
    <!-- Native video for direct URLs -->
    <video
      v-if="isDirectVideo"
      :src="url"
      :poster="poster"
      class="native-video"
      controls
      :show-center-play-btn="true"
      :enable-progress-gesture="true"
      object-fit="contain"
    />

    <!-- B站 video card (opens in browser) -->
    <view v-else class="video-card" @click="openInBrowser">
      <view class="video-cover">
        <view class="play-icon">
          <text class="play-triangle">▶</text>
        </view>
        <text class="platform-badge">{{ platform }}</text>
      </view>
      <view class="video-info">
        <text class="video-title">{{ title }}</text>
        <view class="video-meta">
          <text class="meta-item">{{ platform }}</text>
          <text v-if="duration" class="meta-item">· {{ duration }}</text>
        </view>
        <text class="open-hint">点击在浏览器中播放</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  url: { type: String, default: '' },
  embedUrl: { type: String, default: '' },
  title: { type: String, default: '' },
  platform: { type: String, default: '' },
  duration: { type: String, default: '' },
  poster: { type: String, default: '' },
})

const isDirectVideo = computed(() => {
  return props.url && /\.(mp4|webm|m3u8)(\?|$)/i.test(props.url)
})

function openInBrowser() {
  // #ifdef MP-WEIXIN
  // WeChat mini program: use web-view or copy link
  uni.showModal({
    title: '打开视频',
    content: `将在浏览器中打开「${props.title}」`,
    confirmText: '复制链接',
    success: (res) => {
      if (res.confirm) {
        uni.setClipboardData({
          data: props.url,
          success: () => {
            uni.showToast({ title: '链接已复制', icon: 'success' })
          }
        })
      }
    }
  })
  // #endif

  // #ifdef H5
  window.open(props.url, '_blank')
  // #endif
}
</script>

<style scoped>
.video-player { width: 100%; margin: 16rpx 0; }
.native-video { width: 100%; border-radius: 12rpx; }
.video-card {
  background: #fff; border-radius: 16rpx; overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0,0,0,0.08); margin-bottom: 16rpx;
}
.video-cover {
  position: relative; height: 320rpx; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex; align-items: center; justify-content: center;
}
.play-icon {
  width: 100rpx; height: 100rpx; border-radius: 50%; background: rgba(255,255,255,0.9);
  display: flex; align-items: center; justify-content: center;
}
.play-triangle { font-size: 48rpx; color: #764ba2; margin-left: 8rpx; }
.platform-badge {
  position: absolute; top: 16rpx; left: 16rpx; background: rgba(0,0,0,0.5);
  color: #fff; font-size: 22rpx; padding: 4rpx 16rpx; border-radius: 8rpx;
}
.video-info { padding: 20rpx 24rpx; }
.video-title { font-size: 28rpx; font-weight: 600; color: #303133; display: block; margin-bottom: 8rpx; }
.video-meta { display: flex; gap: 8rpx; margin-bottom: 8rpx; }
.meta-item { font-size: 24rpx; color: #909399; }
.open-hint { font-size: 22rpx; color: #409eff; }
</style>
