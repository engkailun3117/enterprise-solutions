<template>
  <div class="es-auth-container">
    <!-- Left Section - Features -->
    <div class="es-left-section">
      <div class="es-logo-section">
        <div class="es-logo">TGSA</div>
        <div class="es-brand-name">
          <h1>企業通</h1>
          <p>ENTERPRISE SOLUTIONS</p>
        </div>
      </div>

      <div class="es-hero">
        <h2>一組帳號，<br><span class="highlight">啟動三大智能引擎</span></h2>
      </div>

      <div class="es-features">
        <div class="es-feature-card">
          <div class="es-feature-icon">📋</div>
          <div class="es-feature-content">
            <h3>AI 企劃引擎 <span class="es-feature-badge">PLANNING</span></h3>
            <p><span class="es-highlight-text">30秒</span> 生成專業補助計畫書，結合歷年過案大數據，精準修飾文案邏輯，提升申請成功率。</p>
          </div>
        </div>

        <div class="es-feature-card">
          <div class="es-feature-icon">🔍</div>
          <div class="es-feature-content">
            <h3>AI 採購引擎 <span class="es-feature-badge">SOURCING</span></h3>
            <p>智能分析廠本結構，一鍵媒合全球優質供應商。提供<span class="es-highlight-text">自動比價</span>與規格檢核，優化供應鏈管理。</p>
          </div>
        </div>

        <div class="es-feature-card">
          <div class="es-feature-icon">🛡️</div>
          <div class="es-feature-content">
            <h3>專利雲端服務 <span class="es-feature-badge">IP CLOUD</span></h3>
            <p>追蹤與專利間圖資料庫，申請簡傳、專利保護方案，包含<span class="es-highlight-text">侵權防護</span>與<span class="es-highlight-text">無形資產鑑價</span>，把關您的無形資產。</p>
          </div>
        </div>
      </div>

      <div class="es-footer">
        <p>© 2025 TGSA Inc. All rights reserved.</p>
        <div class="es-footer-links">
          <a href="#">服務條款</a>
          <a href="#">隱私權政策</a>
        </div>
      </div>
    </div>

    <!-- Right Section - Auth Form (Slot for different auth forms) -->
    <div class="es-right-section">
      <div class="es-auth-box">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// This component provides the layout for all authentication pages
</script>
