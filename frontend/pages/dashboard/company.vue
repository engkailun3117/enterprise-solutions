<template>
  <NuxtLayout name="dashboard">
    <div class="company-page">
      <div class="page-header">
        <h1 class="page-title">📋 公司資料維護</h1>
        <p class="page-subtitle">上次更新：{{ lastUpdated }}</p>
      </div>

      <!-- AI Onboarding Chatbot Section -->
      <div class="section-card chatbot-section">
        <div class="section-header">
          <h2 class="section-title">🤖 企業導入 AI 助理</h2>
          <button class="btn-link" @click="toggleChatbot">
            {{ showChatbot ? '收起' : '展開' }}
          </button>
        </div>

        <div v-if="showChatbot" class="chatbot-container">
          <div class="chat-messages" ref="chatMessages">
            <div
              v-for="message in messages"
              :key="message.id"
              :class="['message', message.role]"
            >
              <div class="message-content">
                <div class="message-text">{{ message.content }}</div>
                <div class="message-time">{{ formatTime(message.created_at) }}</div>
              </div>
            </div>
            <div v-if="isLoading" class="message assistant">
              <div class="message-content">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <div v-if="progress" class="progress-bar">
            <div class="progress-info">
              <span>資料收集進度：{{ progress.fields_completed }}/{{ progress.total_fields }} 欄位</span>
              <span v-if="progress.products_count > 0">・{{ progress.products_count }} 個產品</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-fill"
                :style="{ width: `${(progress.fields_completed / progress.total_fields) * 100}%` }"
              ></div>
            </div>
          </div>

          <div class="chat-actions">
            <button
              v-if="sessionId && !chatCompleted"
              class="btn-secondary btn-sm"
              @click="exportData"
              :disabled="!progress?.company_info_complete"
            >
              匯出 JSON
            </button>
            <button
              v-if="sessionId"
              class="btn-secondary btn-sm"
              @click="startNewSession"
            >
              新對話
            </button>
          </div>

          <div class="chat-input-container">
            <textarea
              v-model="userMessage"
              class="chat-input"
              placeholder="在此輸入訊息... (Enter 發送，Shift+Enter 換行)"
              @keydown="handleKeydown"
              :disabled="isLoading || chatCompleted"
              rows="1"
            ></textarea>
            <button
              class="btn-send"
              @click="sendMessage"
              :disabled="!userMessage.trim() || isLoading || chatCompleted"
            >
              發送
            </button>
          </div>
        </div>
      </div>

      <!-- Company Application Status Section -->
      <div v-if="sessionId && progress?.company_info_complete" class="section-card application-section">
        <div class="section-header">
          <h2 class="section-title">📨 提交公司申請</h2>
          <span v-if="companyApplication" :class="['status-badge', companyApplication.status]">
            {{ getStatusText(companyApplication.status) }}
          </span>
        </div>

        <div class="application-content">
          <div v-if="!companyApplication" class="application-prompt">
            <p>您已完成所有資料填寫！點擊下方按鈕提交正式申請。</p>
            <button class="btn-primary" @click="submitApplication" :disabled="isSubmitting">
              {{ isSubmitting ? '提交中...' : '提交申請' }}
            </button>
          </div>

          <div v-else class="application-details">
            <div class="detail-grid">
              <div class="detail-item">
                <label>公司名稱</label>
                <p>{{ companyApplication.company_name }}</p>
              </div>
              <div class="detail-item">
                <label>公司ID</label>
                <p>{{ companyApplication.company_id }}</p>
              </div>
              <div class="detail-item">
                <label>負責人</label>
                <p>{{ companyApplication.company_head }}</p>
              </div>
              <div class="detail-item">
                <label>聯絡 Email</label>
                <p>{{ companyApplication.company_email }}</p>
              </div>
              <div class="detail-item">
                <label>公司網址</label>
                <p>{{ companyApplication.company_link || '未提供' }}</p>
              </div>
              <div class="detail-item">
                <label>申請狀態</label>
                <p :class="['status-text', companyApplication.status]">
                  {{ getStatusText(companyApplication.status) }}
                </p>
              </div>
              <div v-if="companyApplication.created_at" class="detail-item">
                <label>提交時間</label>
                <p>{{ formatDateTime(companyApplication.created_at) }}</p>
              </div>
              <div v-if="companyApplication.reviewed_at" class="detail-item">
                <label>審核時間</label>
                <p>{{ formatDateTime(companyApplication.reviewed_at) }}</p>
              </div>
            </div>

            <div v-if="companyApplication.status === 'rejected' && companyApplication.rejection_reason" class="rejection-reason">
              <label>拒絕原因</label>
              <p>{{ companyApplication.rejection_reason }}</p>
            </div>

            <div class="application-actions">
              <button v-if="companyApplication.status !== 'approved'" class="btn-secondary" @click="submitApplication" :disabled="isSubmitting">
                {{ isSubmitting ? '更新中...' : '重新提交申請' }}
              </button>
              <button class="btn-link" @click="refreshApplicationStatus">
                刷新狀態
              </button>
            </div>
          </div>
        </div>
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
const api = useApi()

const lastUpdated = ref('2023/12/20 由 Alex Chen')

const companyData = ref({
  nameCN: '全球策略顧問股份有限公司',
  nameEN: 'Global Strategy Advisors Inc.',
  taxId: '82918455',
  website: 'www.gsa-consulting.ai'
})

// Chatbot state
const showChatbot = ref(true)
const sessionId = ref<number | null>(null)
const messages = ref<any[]>([])
const userMessage = ref('')
const isLoading = ref(false)
const chatCompleted = ref(false)
const progress = ref<any>(null)
const chatMessages = ref<HTMLElement | null>(null)

// Company application state
const companyApplication = ref<any>(null)
const isSubmitting = ref(false)

// Session persistence functions
const loadSavedSession = () => {
  if (typeof window === 'undefined') return null
  const saved = localStorage.getItem('chatbot_session_id')
  return saved ? parseInt(saved) : null
}

const saveSessionId = (id: number) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('chatbot_session_id', id.toString())
  }
}

const clearSavedSession = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('chatbot_session_id')
  }
}

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

// Chatbot functions
const toggleChatbot = () => {
  showChatbot.value = !showChatbot.value
}

const formatTime = (timestamp: string) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessages.value) {
      chatMessages.value.scrollTop = chatMessages.value.scrollHeight
    }
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  // Enter without Shift = send message
  // Shift+Enter = line break (default textarea behavior)
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault() // Prevent default line break
    sendMessage()
  } else {
    // Auto-grow textarea on input
    nextTick(() => {
      const textarea = event.target as HTMLTextAreaElement
      textarea.style.height = 'auto'
      textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px'
    })
  }
}

const sendMessage = async () => {
  if (!userMessage.value.trim() || isLoading.value || chatCompleted.value) return

  const messageText = userMessage.value.trim()
  userMessage.value = ''
  isLoading.value = true

  // Reset textarea height
  nextTick(() => {
    const textarea = document.querySelector('.chat-input') as HTMLTextAreaElement
    if (textarea) {
      textarea.style.height = 'auto'
    }
  })

  try {
    const response = await api.post('/api/chatbot/message', {
      message: messageText,
      session_id: sessionId.value
    })

    // Store session ID if new session
    if (!sessionId.value) {
      sessionId.value = response.session_id
      saveSessionId(response.session_id) // Persist to localStorage
    }

    // Add user message
    messages.value.push({
      id: Date.now(),
      role: 'user',
      content: messageText,
      created_at: new Date().toISOString()
    })

    // Add bot response
    messages.value.push({
      id: Date.now() + 1,
      role: 'assistant',
      content: response.message,
      created_at: new Date().toISOString()
    })

    // Update progress and completion status
    progress.value = response.progress
    chatCompleted.value = response.completed

    if (response.completed) {
      toast.add({
        title: '完成',
        description: '公司資料收集已完成！',
        color: 'green'
      })
    }

    scrollToBottom()
  } catch (error: any) {
    console.error('Error sending message:', error)
    toast.add({
      title: '錯誤',
      description: error.message || '發送訊息失敗',
      color: 'red'
    })
  } finally {
    isLoading.value = false
  }
}

const startNewSession = async () => {
  sessionId.value = null
  messages.value = []
  chatCompleted.value = false
  progress.value = null
  clearSavedSession()

  // Initialize new session with context from previous session
  try {
    // Use smart session creation that copies company info from latest session
    const response = await api.createNewSessionWithContext()

    sessionId.value = response.session_id
    saveSessionId(response.session_id)

    messages.value.push({
      id: Date.now(),
      role: 'assistant',
      content: response.message,
      created_at: new Date().toISOString()
    })

    progress.value = response.progress
    chatCompleted.value = response.completed

    // Show notification if company info was copied
    if (response.company_info_copied) {
      toast.add({
        title: '已載入公司資料',
        description: '上次的公司資訊已自動載入，您可以直接更新或確認',
        color: 'green'
      })
    }

    scrollToBottom()
  } catch (error: any) {
    console.error('Error starting new session:', error)
    toast.add({
      title: '錯誤',
      description: '無法啟動新對話',
      color: 'red'
    })
  }
}

const exportData = async () => {
  if (!sessionId.value) return

  try {
    const data = await api.get(`/api/chatbot/export/${sessionId.value}`)

    // Download as JSON file
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `company-data-${sessionId.value}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.add({
      title: '匯出成功',
      description: 'JSON 檔案已下載',
      color: 'green'
    })
  } catch (error: any) {
    console.error('Error exporting data:', error)
    toast.add({
      title: '錯誤',
      description: '匯出資料失敗',
      color: 'red'
    })
  }
}

// Company application functions
const submitApplication = async () => {
  if (!sessionId.value) return

  isSubmitting.value = true
  try {
    const result = await api.submitChatbotApplication({
      session_id: sessionId.value
    })

    companyApplication.value = result

    toast.add({
      title: '提交成功',
      description: '您的公司申請已提交，請等待審核',
      color: 'green'
    })
  } catch (error: any) {
    console.error('Error submitting application:', error)
    toast.add({
      title: '提交失敗',
      description: error.data?.detail || error.message || '無法提交申請',
      color: 'red'
    })
  } finally {
    isSubmitting.value = false
  }
}

const refreshApplicationStatus = async () => {
  try {
    const result = await api.getMyApplication()
    companyApplication.value = result.data

    toast.add({
      title: '已刷新',
      description: '申請狀態已更新',
      color: 'blue'
    })
  } catch (error: any) {
    // If 404, it means no application exists yet
    if (error.status === 404 || error.statusCode === 404) {
      companyApplication.value = null
    } else {
      console.error('Error refreshing application:', error)
      toast.add({
        title: '刷新失敗',
        description: error.data?.detail || error.message || '無法取得申請狀態',
        color: 'red'
      })
    }
  }
}

const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    pending: '審核中',
    approved: '已核准',
    rejected: '已拒絕'
  }
  return statusMap[status] || status
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Auto-start chatbot on mount
onMounted(async () => {
  try {
    // Helper function to load session by ID
    const loadSessionById = async (id: number) => {
      // Load session messages
      const sessionMessages = await api.getChatMessages(id)

      // Load session data to check if completed
      const sessionData = await api.getOnboardingData(id)

      // Restore session state
      sessionId.value = id
      messages.value = sessionMessages.map((msg: any) => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        created_at: msg.created_at
      }))

      // Calculate progress
      const onboardingData = sessionData.onboarding_data
      let fieldsCompleted = 0
      const totalFields = 10

      if (onboardingData.company_id) fieldsCompleted++
      if (onboardingData.company_name) fieldsCompleted++
      if (onboardingData.industry) fieldsCompleted++
      if (onboardingData.country) fieldsCompleted++
      if (onboardingData.address) fieldsCompleted++
      if (onboardingData.capital_amount !== null) fieldsCompleted++
      if (onboardingData.invention_patent_count !== null) fieldsCompleted++
      if (onboardingData.utility_patent_count !== null) fieldsCompleted++
      if (onboardingData.certification_count !== null) fieldsCompleted++
      if (onboardingData.esg_certification !== null) fieldsCompleted++

      progress.value = {
        company_info_complete: fieldsCompleted === totalFields,
        fields_completed: fieldsCompleted,
        total_fields: totalFields,
        products_count: onboardingData.products?.length || 0
      }

      chatCompleted.value = sessionData.status === 'completed'

      scrollToBottom()

      console.log('Session restored:', id)
    }

    // Check for saved session in localStorage
    const savedSessionId = loadSavedSession()

    if (savedSessionId) {
      // Try to load existing session from localStorage
      try {
        await loadSessionById(savedSessionId)
      } catch (error: any) {
        // If localStorage session doesn't exist or error loading, try backend
        console.log('Could not restore localStorage session:', error.message)
        clearSavedSession()

        // Try to get latest active session from backend
        try {
          const latestSessionResponse = await api.getLatestActiveSession()

          if (latestSessionResponse.session_id) {
            // Found an active session on backend, restore it
            console.log('Found latest active session from backend:', latestSessionResponse.session_id)
            await loadSessionById(latestSessionResponse.session_id)
            saveSessionId(latestSessionResponse.session_id)
          } else {
            // No active session found, start new one
            console.log('No active session found, starting new session')
            const response = await api.post('/api/chatbot/message', {
              message: '',
              session_id: null
            })

            sessionId.value = response.session_id
            saveSessionId(response.session_id)

            messages.value.push({
              id: Date.now(),
              role: 'assistant',
              content: response.message,
              created_at: new Date().toISOString()
            })

            progress.value = response.progress
            chatCompleted.value = response.completed

            scrollToBottom()
          }
        } catch (backendError: any) {
          console.error('Error getting latest session from backend:', backendError)
          // Fall back to creating new session
          const response = await api.post('/api/chatbot/message', {
            message: '',
            session_id: null
          })

          sessionId.value = response.session_id
          saveSessionId(response.session_id)

          messages.value.push({
            id: Date.now(),
            role: 'assistant',
            content: response.message,
            created_at: new Date().toISOString()
          })

          progress.value = response.progress
          chatCompleted.value = response.completed

          scrollToBottom()
        }
      }
    } else {
      // No saved session in localStorage, check backend for latest active session
      try {
        const latestSessionResponse = await api.getLatestActiveSession()

        if (latestSessionResponse.session_id) {
          // Found an active session on backend, restore it
          console.log('Found latest active session from backend:', latestSessionResponse.session_id)
          await loadSessionById(latestSessionResponse.session_id)
          saveSessionId(latestSessionResponse.session_id)
        } else {
          // No active session found, start new one
          console.log('No active session found, starting new session')
          const response = await api.post('/api/chatbot/message', {
            message: '',
            session_id: null
          })

          sessionId.value = response.session_id
          saveSessionId(response.session_id)

          messages.value.push({
            id: Date.now(),
            role: 'assistant',
            content: response.message,
            created_at: new Date().toISOString()
          })

          progress.value = response.progress
          chatCompleted.value = response.completed

          scrollToBottom()
        }
      } catch (backendError: any) {
        console.error('Error getting latest session from backend:', backendError)
        // Fall back to creating new session
        const response = await api.post('/api/chatbot/message', {
          message: '',
          session_id: null
        })

        sessionId.value = response.session_id
        saveSessionId(response.session_id)

        messages.value.push({
          id: Date.now(),
          role: 'assistant',
          content: response.message,
          created_at: new Date().toISOString()
        })

        progress.value = response.progress
        chatCompleted.value = response.completed

        scrollToBottom()
      }
    }

    // Load company application status
    try {
      const result = await api.getMyApplication()
      if (result.data) {
        companyApplication.value = result.data
      }
    } catch (error: any) {
      // If 404, user hasn't submitted an application yet - this is normal
      if (error.status !== 404 && error.statusCode !== 404) {
        console.error('Error loading application status:', error)
      }
    }
  } catch (error: any) {
    // Silently fail if user is not logged in
    console.log('Chatbot initialization skipped:', error.message)
  }
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

/* Chatbot Styles */
.chatbot-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.chatbot-section .section-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.chatbot-section .section-title {
  color: white;
}

.chatbot-section .btn-link {
  color: white;
  opacity: 1;
  cursor: pointer;
}

.chatbot-container {
  margin-top: 20px;
}

.chat-messages {
  background: white;
  border-radius: 12px;
  padding: 20px;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.message {
  display: flex;
  margin-bottom: 16px;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.message-content {
  max-width: 70%;
}

.message.user .message-content {
  background: #d14d41;
  color: white;
  border-radius: 18px 18px 4px 18px;
  padding: 12px 16px;
}

.message.assistant .message-content {
  background: #f5f5f5;
  color: #1a1a2e;
  border-radius: 18px 18px 18px 4px;
  padding: 12px 16px;
}

.message-text {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  margin-top: 4px;
  text-align: right;
}

.message.assistant .message-time {
  text-align: left;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.progress-bar {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 16px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  margin-bottom: 8px;
  color: white;
}

.progress-track {
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: white;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.chat-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

.chat-input-container {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.9);
  color: #1a1a2e;
  transition: all 0.3s;
  font-family: inherit;
  line-height: 1.5;
  min-height: 44px;
  max-height: 150px;
  resize: none;
  overflow-y: auto;
}

.chat-input:focus {
  outline: none;
  background: white;
  border-color: white;
}

.chat-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-send {
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  border-radius: 24px;
  background: white;
  color: #667eea;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  white-space: nowrap;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .message-content {
    max-width: 85%;
  }

  .chat-messages {
    max-height: 400px;
  }
}

/* Application Section Styles */
.application-section {
  background: linear-gradient(135deg, #43cea2 0%, #185a9d 100%);
  color: white;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: rgba(255, 193, 7, 0.9);
  color: #1a1a2e;
}

.status-badge.approved {
  background: rgba(76, 175, 80, 0.9);
  color: white;
}

.status-badge.rejected {
  background: rgba(244, 67, 54, 0.9);
  color: white;
}

.application-content {
  padding: 16px 0;
}

.application-prompt {
  text-align: center;
  padding: 24px;
}

.application-prompt p {
  font-size: 16px;
  margin-bottom: 20px;
  opacity: 0.95;
}

.application-prompt .btn-primary {
  background: white;
  color: #185a9d;
  padding: 12px 32px;
  border-radius: 24px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.application-prompt .btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

.application-prompt .btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.application-details {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 24px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.detail-item label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-item p {
  font-size: 15px;
  font-weight: 500;
  margin: 0;
}

.status-text {
  padding: 4px 12px;
  border-radius: 12px;
  display: inline-block;
  font-size: 14px;
}

.status-text.pending {
  background: rgba(255, 193, 7, 0.2);
  color: #ffc107;
}

.status-text.approved {
  background: rgba(76, 175, 80, 0.2);
  color: #4caf50;
}

.status-text.rejected {
  background: rgba(244, 67, 54, 0.2);
  color: #f44336;
}

.rejection-reason {
  background: rgba(244, 67, 54, 0.2);
  border-left: 4px solid #f44336;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 20px;
}

.rejection-reason label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #f44336;
}

.rejection-reason p {
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  color: white;
}

.application-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.application-actions .btn-secondary {
  background: white;
  color: #185a9d;
  padding: 10px 24px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
}

.application-actions .btn-secondary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.application-actions .btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.application-actions .btn-link {
  background: transparent;
  color: white;
  padding: 10px 16px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.application-actions .btn-link:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.5);
}
</style>
