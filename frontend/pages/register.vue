<template>
  <AuthLayout>
    <div class="es-auth-header">
      <h2>建立企業帳號</h2>
      <p>填寫基本資料，立即啟用全方位 AI 服務</p>
    </div>

    <form @submit.prevent="handleRegister" class="es-auth-form">
      <div class="es-form-row">
        <div class="es-form-group">
          <label for="taxId">統一編號 (Tax ID)</label>
          <input
            v-model="formData.taxId"
            type="text"
            id="taxId"
            placeholder="8碼數字"
            pattern="[0-9]{8}"
            :disabled="isSubmitting"
            required
          >
        </div>

        <div class="es-form-group">
          <label for="companyName">公司名稱</label>
          <input
            v-model="formData.companyName"
            type="text"
            id="companyName"
            placeholder="完整公司登記名稱"
            :disabled="isSubmitting"
            required
          >
        </div>
      </div>

      <div class="es-form-group">
        <label for="contactName">聯絡人姓名</label>
        <input
          v-model="formData.username"
          type="text"
          id="contactName"
          placeholder="請輸入真實姓名"
          :disabled="isSubmitting"
          required
        >
      </div>

      <div class="es-form-group">
        <label for="email">企業電子信箱</label>
        <input
          v-model="formData.email"
          type="email"
          id="email"
          placeholder="name@company.com"
          :disabled="isSubmitting"
          required
        >
      </div>

      <div class="es-form-row">
        <div class="es-form-group">
          <label for="password">設定密碼</label>
          <input
            v-model="formData.password"
            type="password"
            id="password"
            placeholder="6位以上英數"
            minlength="6"
            :disabled="isSubmitting"
            required
          >
        </div>

        <div class="es-form-group">
          <label for="confirmPassword">確認密碼</label>
          <input
            v-model="formData.confirmPassword"
            type="password"
            id="confirmPassword"
            placeholder="再次輸入密碼"
            minlength="6"
            :disabled="isSubmitting"
            required
          >
        </div>
      </div>

      <div class="es-terms-text">
        <label>
          <input type="checkbox" id="terms" v-model="termsAccepted" required>
          我已閱讀並接受 TGSA <a href="#">服務條款</a>、<a href="#">隱私權政策</a> 與 <a href="#">權限政策</a>，並同意 TGSA 蒐集相關企業資訊供 AI 模型優化。
        </label>
      </div>

      <button type="submit" class="es-btn-primary" :disabled="isSubmitting || !isFormValid">
        {{ isSubmitting ? '註冊中...' : '立即註冊並啟用 →' }}
      </button>

      <div class="es-divider">
        <span>或使用社群帳號快速建立</span>
      </div>

      <div class="es-social-login">
        <button type="button" class="es-btn-social" @click="handleSocialLogin('google')">
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Google
        </button>
        <button type="button" class="es-btn-social" @click="handleSocialLogin('facebook')">
          <svg width="20" height="20" viewBox="0 0 24 24">
            <path fill="#1877F2" d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
          Facebook
        </button>
      </div>

      <div class="es-auth-footer">
        已有帳號？<NuxtLink to="/login">前往登入</NuxtLink>
      </div>

      <div class="es-privacy-notice">
        設定用社群帳號快速註冊
      </div>
    </form>
  </AuthLayout>
</template>

<script setup lang="ts">
const router = useRouter()
const toast = useToast()
const api = useApi()

const formData = ref({
  taxId: '',
  companyName: '',
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const isSubmitting = ref(false)
const termsAccepted = ref(false)

const isFormValid = computed(() => {
  return (
    /^\d{8}$/.test(formData.value.taxId) &&
    formData.value.companyName.length > 0 &&
    formData.value.username.length >= 3 &&
    formData.value.email.includes('@') &&
    formData.value.password.length >= 6 &&
    formData.value.password === formData.value.confirmPassword &&
    termsAccepted.value
  )
})

const handleRegister = async () => {
  // Validate Tax ID format
  if (!/^\d{8}$/.test(formData.value.taxId)) {
    toast.add({
      title: '驗證失敗',
      description: '統一編號必須是 8 碼數字',
      color: 'red'
    })
    return
  }

  // Validate password match
  if (formData.value.password !== formData.value.confirmPassword) {
    toast.add({
      title: '密碼不符',
      description: '密碼和確認密碼不相同',
      color: 'red'
    })
    return
  }

  // Validate terms acceptance
  if (!termsAccepted.value) {
    toast.add({
      title: '驗證失敗',
      description: '請閱讀並接受服務條款與隱私權政策',
      color: 'red'
    })
    return
  }

  if (!isFormValid.value) {
    toast.add({
      title: '驗證失敗',
      description: '請確認所有欄位都已正確填寫',
      color: 'red'
    })
    return
  }

  isSubmitting.value = true

  try {
    const { data, error } = await api.register(
      formData.value.username,
      formData.value.email,
      formData.value.password
    )

    if (error) {
      toast.add({
        title: '註冊失敗',
        description: error,
        color: 'red'
      })
      return
    }

    if (data) {
      toast.add({
        title: '註冊成功',
        description: `歡迎加入，${formData.value.companyName}！`,
        color: 'green'
      })

      // Redirect to dashboard
      router.push('/dashboard')
    }
  } catch (err) {
    toast.add({
      title: '錯誤',
      description: '註冊時發生未預期的錯誤',
      color: 'red'
    })
  } finally {
    isSubmitting.value = false
  }
}

const handleSocialLogin = (provider: string) => {
  toast.add({
    title: '開發中',
    description: `${provider} 註冊功能即將推出`,
    color: 'blue'
  })
}
</script>
