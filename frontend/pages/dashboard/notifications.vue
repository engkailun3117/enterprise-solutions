<template>
  <NuxtLayout name="dashboard">
    <div class="notifications-page">
      <div class="page-header">
        <h1 class="page-title">🔔 通知中心</h1>
        <p class="page-subtitle">查看所有系統通知與訊息</p>
      </div>

      <div class="placeholder-card">
        <div class="placeholder-icon">🔔</div>
        <h2 class="placeholder-title">通知中心</h2>
        <p class="placeholder-text">目前沒有新通知</p>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
// Placeholder page for notifications
</script>

<style scoped>
.notifications-page {
  max-width: 1200px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.page-subtitle {
  font-size: 14px;
  color: #999;
}

.placeholder-card {
  background: white;
  border-radius: 12px;
  padding: 80px 40px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.placeholder-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 12px;
}

.placeholder-text {
  font-size: 16px;
  color: #999;
}
</style>
