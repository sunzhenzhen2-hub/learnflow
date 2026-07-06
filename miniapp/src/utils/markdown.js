/**
 * Lightweight Markdown parser for WeChat Mini Program
 * Returns structured blocks for rendering with native components
 */
export function parseMarkdown(md) {
  if (!md) return []

  const blocks = []
  const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g
  const parts = []
  let lastIndex = 0
  let match

  // Extract code blocks first
  while ((match = codeBlockRegex.exec(md)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: md.slice(lastIndex, match.index) })
    }
    parts.push({ type: 'code', lang: match[1] || '', content: match[2].trim() })
    lastIndex = match.index + match[0].length
  }
  if (lastIndex < md.length) {
    parts.push({ type: 'text', content: md.slice(lastIndex) })
  }

  // Parse text parts into blocks
  for (const part of parts) {
    if (part.type === 'code') {
      blocks.push({ type: 'code', lang: part.lang, content: part.content })
      continue
    }

    const lines = part.content.split('\n')
    let currentList = null

    for (const line of lines) {
      const trimmed = line.trim()
      if (!trimmed) {
        if (currentList) {
          blocks.push(currentList)
          currentList = null
        }
        continue
      }

      // Headings
      const h3 = trimmed.match(/^### (.+)$/)
      if (h3) {
        if (currentList) { blocks.push(currentList); currentList = null }
        blocks.push({ type: 'heading', level: 3, content: h3[1] })
        continue
      }
      const h2 = trimmed.match(/^## (.+)$/)
      if (h2) {
        if (currentList) { blocks.push(currentList); currentList = null }
        blocks.push({ type: 'heading', level: 2, content: h2[1] })
        continue
      }
      const h1 = trimmed.match(/^# (.+)$/)
      if (h1) {
        if (currentList) { blocks.push(currentList); currentList = null }
        blocks.push({ type: 'heading', level: 1, content: h1[1] })
        continue
      }

      // Blockquote
      if (trimmed.startsWith('> ')) {
        if (currentList) { blocks.push(currentList); currentList = null }
        blocks.push({ type: 'blockquote', content: trimmed.substring(2) })
        continue
      }

      // List items
      const listMatch = trimmed.match(/^[-*]\s+(.+)$/)
      if (listMatch) {
        if (!currentList) currentList = { type: 'list', items: [] }
        currentList.items.push(listMatch[1])
        continue
      }

      // Regular paragraph
      if (currentList) { blocks.push(currentList); currentList = null }
      blocks.push({ type: 'paragraph', content: trimmed })
    }

    if (currentList) blocks.push(currentList)
  }

  return blocks
}

/**
 * Process inline markdown (bold, italic, inline code) into rich text nodes
 * for use with <rich-text> component
 */
export function inlineMarkdown(text) {
  if (!text) return ''
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code style="background:#f0f2f5;padding:2rpx 8rpx;border-radius:4rpx;font-size:24rpx;color:#e6a23c">$1</code>')
}
