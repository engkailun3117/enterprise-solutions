<template>
  <NuxtLayout name="dashboard">
    <div class="dashboard-home">
      <!-- Welcome Section -->
      <div class="welcome-card">
        <h1 class="welcome-title">AI 戰情室平台</h1>
        <p class="welcome-subtitle">企業智能服務平台 - 啟動三大智能引擎</p>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">企業帳號數</div>
          <div class="stat-value">3 <span class="stat-unit">個</span></div>
        </div>

        <div class="stat-card">
          <div class="stat-label">代辦事項</div>
          <div class="stat-value">1,240 <span class="stat-unit">件</span></div>
        </div>

        <div class="stat-card">
          <div class="stat-label">即將截止</div>
          <div class="stat-value">3 <span class="stat-unit">筆</span></div>
        </div>

        <div class="stat-card">
          <div class="stat-label">專利審核進度</div>
          <div class="stat-value">12 <span class="stat-unit">件</span></div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="activity-section">
        <h2 class="section-title">📋 最新動態紀錄</h2>
        <div class="activity-card">
          <p class="activity-placeholder">目前沒有最新動態</p>
        </div>
      </div>

      <!-- AI Engines Info -->
      <div class="engines-section">
        <div class="engine-card">
          <div class="engine-icon">📋</div>
          <h3 class="engine-title">AI 企劃引擎</h3>
          <p class="engine-desc">30秒生成專業補助計畫書，結合歷年過案大數據，精準修飾文案邏輯，提升申請成功率。</p>
        </div>

        <div class="engine-card">
          <div class="engine-icon">🔍</div>
          <h3 class="engine-title">AI 採購引擎</h3>
          <p class="engine-desc">智能分析廠本結構，一鍵媒合全球優質供應商，提供自動比價與規格檢核。</p>
        </div>

        <div class="engine-card">
          <div class="engine-icon">🛡️</div>
          <h3 class="engine-title">專利雲端服務</h3>
          <p class="engine-desc">追蹤與專利間圖資料庫，申請簡傳、專利保護方案，包含侵權防護與無形資產備份。</p>
        </div>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
const router = useRouter()

// Check authentication on mount
onMounted(() => {
  // TODO: Add proper authentication check
  // For now, just a placeholder
})
</script>

<style scoped>
.dashboard-home {
  max-width: 1200px;
}

.welcome-card {
  background: white;
  padding: 32px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.welcome-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.welcome-subtitle {
  font-size: 16px;
  color: #666;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1a1a2e;
}

.stat-unit {
  font-size: 16px;
  font-weight: 400;
  color: #999;
}

.activity-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 16px;
}

.activity-card {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.activity-placeholder {
  color: #999;
  font-size: 14px;
}

.engines-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.engine-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.engine-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.engine-title {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.engine-desc {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
}
</style>