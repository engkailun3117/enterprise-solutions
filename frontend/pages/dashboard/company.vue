<template>
  <NuxtLayout name="dashboard">
    <div class="company-page">
      <div class="page-header">
        <h1 class="page-title">📋 公司資料維護</h1>
        <p class="page-subtitle">上次更新：{{ lastUpdated }}</p>
      </div>

      <!-- Company Identity Section -->
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">🏢 企業識別資訊 (Identity)</h2>
          <button class="btn-link" disabled>儲存目前的此狀態</button>
        </div>

        <div class="company-identity">
          <!-- Logo Upload -->
          <div class="logo-upload-section">
            <div class="logo-preview">
              {{ companyInitials }}
            </div>
            <div class="logo-upload-info">
              <p class="upload-label">企業 Logo</p>
              <p class="upload-specs">建議尺寸 512x512px<br>PNG 或 JPG</p>
            </div>
          </div>

          <!-- Company Information Form -->
          <div class="company-form">
            <div class="form-row-2">
              <div class="form-field">
                <label for="companyNameCN">公司全名 (中文) <span class="required">*</span></label>
                <input
                  type="text"
                  id="companyNameCN"
                  v-model="companyData.nameCN"
                  placeholder="全球策略顧問股份有限公司"
                >
              </div>

              <div class="form-field">
                <label for="taxId">統一編號 (Tax ID) <span class="required">*</span></label>
                <input
                  type="text"
                  id="taxId"
                  v-model="companyData.taxId"
                  placeholder="82918455"
                  pattern="[0-9]{8}"
                  @blur="validateTaxId"
                >
                <span v-if="taxIdValid" class="validation-icon">✓</span>
                <p v-if="companyData.taxId" class="field-hint">若需變更統一編號請聯繫客服</p>
              </div>
            </div>

            <div class="form-field">
              <label for="companyNameEN">公司英文名稱</label>
              <input
                type="text"
                id="companyNameEN"
                v-model="companyData.nameEN"
                placeholder="Global Strategy Advisors Inc."
              >
            </div>

            <div class="form-field">
              <label for="website">公司網站</label>
              <div class="input-with-prefix">
                <span class="input-prefix">https://</span>
                <input
                  type="text"
                  id="website"
                  v-model="companyData.website"
                  placeholder="www.gsa-consulting.ai"
                >
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- AI Strategy Settings Section -->
      <div class="section-card">
        <div class="section-header">
          <h2 class="section-title">⚙️ AI 戰略參數設定</h2>
          <button class="btn-link" disabled>影響分析準確度</button>
        </div>

        <div class="ai-settings-placeholder">
          <p class="placeholder-text">AI 戰略參數設定選項將在此顯示</p>
          <p class="placeholder-hint">此區域用於設定 AI 模型的戰略參數</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="action-buttons">
        <button class="btn-secondary" @click="handleCancel">取消</button>
        <button class="btn-primary" @click="handleSave">儲存變更</button>
      </div>
    </div>
  </NuxtLayout>
</template>

<script setup lang="ts">
const toast = useToast()

const lastUpdated = ref('2023/12/20 由 Alex Chen')

const companyData = ref({
  nameCN: '全球策略顧問股份有限公司',
  nameEN: 'Global Strategy Advisors Inc.',
  taxId: '82918455',
  website: 'www.gsa-consulting.ai'
})

const taxIdValid = computed(() => {
  return /^\d{8}$/.test(companyData.value.taxId)
})

const companyInitials = computed(() => {
  if (companyData.value.nameEN) {
    return companyData.value.nameEN
      .split(' ')
      .map(word => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }
  return 'GS'
})

const validateTaxId = () => {
  if (companyData.value.taxId && !taxIdValid.value) {
    toast.add({
      title: '格式錯誤',
      description: '統一編號必須是 8 碼數字',
      color: 'red'
    })
  }
}

const handleSave = () => {
  if (!taxIdValid.value) {
    toast.add({
      title: '驗證失敗',
      description: '請確認統一編號格式正確',
      color: 'red'
    })
    return
  }

  toast.add({
    title: '儲存成功',
    description: '公司資料已更新',
    color: 'green'
  })
}

const handleCancel = () => {
  toast.add({
    title: '已取消',
    description: '變更已取消',
    color: 'blue'
  })
}
</script>

<style scoped>
.company-page {
  max-width: 1000px;
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

.section-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e0e0e0;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
}

.btn-link {
  font-size: 14px;
  color: #d14d41;
  background: none;
  border: none;
  cursor: not-allowed;
  opacity: 0.6;
}

.company-identity {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 40px;
}

.logo-upload-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  font-weight: bold;
  color: white;
  margin-bottom: 12px;
}

.logo-upload-info {
  text-align: center;
}

.upload-label {
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 4px;
}

.upload-specs {
  font-size: 12px;
  color: #999;
  line-height: 1.5;
}

.company-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-field {
  position: relative;
}

.form-field label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.required {
  color: #d14d41;
}

.form-field input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  transition: all 0.3s;
}

.form-field input:focus {
  outline: none;
  border-color: #d14d41;
  box-shadow: 0 0 0 3px rgba(209, 77, 65, 0.1);
}

.validation-icon {
  position: absolute;
  right: 16px;
  top: 42px;
  color: #10b981;
  font-size: 18px;
}

.field-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.input-with-prefix {
  display: flex;
  align-items: center;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.input-prefix {
  padding: 12px 12px;
  background-color: #f5f5f5;
  border-right: 1px solid #e0e0e0;
  font-size: 14px;
  color: #666;
}

.input-with-prefix input {
  border: none;
  flex: 1;
}

.ai-settings-placeholder {
  padding: 60px 24px;
  text-align: center;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.placeholder-text {
  font-size: 16px;
  color: #666;
  margin-bottom: 8px;
}

.placeholder-hint {
  font-size: 14px;
  color: #999;
}

.action-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-secondary,
.btn-primary {
  padding: 12px 32px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary {
  background: white;
  border: 1px solid #e0e0e0;
  color: #666;
}

.btn-secondary:hover {
  background: #f5f5f5;
}

.btn-primary {
  background: #d14d41;
  border: none;
  color: white;
}

.btn-primary:hover {
  background: #b93d33;
}

@media (max-width: 768px) {
  .company-identity {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .form-row-2 {
    grid-template-columns: 1fr;
  }
}
</style>
