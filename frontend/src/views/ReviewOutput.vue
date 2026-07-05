<template>
  <div class="review-view">
    <h2>{{ $t('review.title') }}</h2>
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading" :size="48"><Loading /></el-icon>
      <p>{{ $t('review.reviewing') }}</p>
    </div>
    <div v-else-if="reviewResult">
      <el-result
        :icon="reviewResult.passed ? 'success' : 'warning'"
        :title="reviewResult.passed ? $t('review.passed') : $t('review.needsImprovement')"
        :sub-title="`${$t('review.score')}: ${reviewResult.score}/100`"
      />
      <div class="feedback-card">
        <h4>{{ $t('review.feedback') }}</h4>
        <p>{{ reviewResult.feedback }}</p>
      </div>
      <div v-if="reviewResult.suggestions?.length" class="suggestions-card">
        <h4>{{ $t('review.suggestions') }}</h4>
        <ul>
          <li v-for="(s, i) in reviewResult.suggestions" :key="i">{{ s }}</li>
        </ul>
      </div>
      <div class="actions">
        <el-button v-if="!reviewResult.passed" type="primary" @click="$router.back()">
          {{ $t('review.revise') }}
        </el-button>
        <el-button v-else type="success" @click="$router.push('/')">
          {{ $t('review.backDashboard') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { reviewApi } from '../api/client'

const route = useRoute()
const stepId = parseInt(route.params.stepId)
const loading = ref(true)
const reviewResult = ref(null)

onMounted(async () => {
  try {
    const { data } = await reviewApi.review(stepId)
    reviewResult.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.review-view { max-width: 600px; margin: 0 auto; }
.loading-state { text-align: center; padding: 48px; }
.feedback-card, .suggestions-card { background: #f9f9f9; padding: 16px; border-radius: 8px; margin: 16px 0; }
.actions { display: flex; justify-content: center; gap: 16px; margin-top: 24px; }
</style>
