<template>
  <view class="markdown-viewer">
    <view v-for="(block, i) in blocks" :key="i">
      <!-- Headings -->
      <text v-if="block.type === 'heading'" :class="'md-h' + block.level">
        {{ block.content }}
      </text>

      <!-- Paragraphs with inline markdown -->
      <rich-text v-else-if="block.type === 'paragraph'" class="md-p" :nodes="formatInline(block.content)" />

      <!-- Code blocks -->
      <view v-else-if="block.type === 'code'" class="md-code">
        <text v-if="block.lang" class="md-code-lang">{{ block.lang }}</text>
        <text class="md-code-text">{{ block.content }}</text>
      </view>

      <!-- Blockquotes -->
      <view v-else-if="block.type === 'blockquote'" class="md-quote">
        <rich-text :nodes="formatInline(block.content)" />
      </view>

      <!-- Lists -->
      <view v-else-if="block.type === 'list'" class="md-list">
        <view v-for="(item, j) in block.items" :key="j" class="md-list-item">
          <text class="md-bullet">•</text>
          <rich-text class="md-list-text" :nodes="formatInline(item)" />
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { computed } from 'vue'
import { parseMarkdown, inlineMarkdown } from '../utils/markdown'

const props = defineProps({
  content: { type: String, default: '' }
})

const blocks = computed(() => parseMarkdown(props.content))

function formatInline(text) {
  return inlineMarkdown(text)
}
</script>

<style scoped>
.markdown-viewer { padding: 0 8rpx; }
.md-h1 { font-size: 36rpx; font-weight: 700; margin: 24rpx 0 12rpx; color: #303133; }
.md-h2 { font-size: 32rpx; font-weight: 600; margin: 20rpx 0 10rpx; color: #303133; border-bottom: 1rpx solid #ebeef5; padding-bottom: 8rpx; }
.md-h3 { font-size: 28rpx; font-weight: 600; margin: 16rpx 0 8rpx; color: #606266; }
.md-p { margin: 8rpx 0; line-height: 1.8; font-size: 28rpx; color: #303133; }
.md-code { background: #282c34; border-radius: 12rpx; padding: 20rpx; margin: 16rpx 0; overflow-x: auto; }
.md-code-lang { font-size: 22rpx; color: #8b949e; display: block; margin-bottom: 8rpx; }
.md-code-text { font-size: 24rpx; color: #abb2bf; font-family: 'Menlo', 'Consolas', monospace; white-space: pre-wrap; word-break: break-all; }
.md-quote { border-left: 6rpx solid #409eff; background: #ecf5ff; padding: 16rpx 20rpx; margin: 16rpx 0; border-radius: 0 8rpx 8rpx 0; }
.md-quote text { color: #606266; font-size: 26rpx; }
.md-list { padding-left: 16rpx; margin: 8rpx 0; }
.md-list-item { display: flex; align-items: flex-start; margin: 6rpx 0; }
.md-bullet { color: #409eff; margin-right: 12rpx; font-size: 28rpx; line-height: 1.8; }
.md-list-text { flex: 1; font-size: 28rpx; line-height: 1.8; color: #303133; }
</style>
