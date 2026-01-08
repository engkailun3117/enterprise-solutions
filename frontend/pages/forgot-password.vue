<template>
  <AuthLayout>
    <div class="es-auth-header">
      <h2>忘記密碼？</h2>
      <p>別擔心，請輸入您的企業信箱，我們將發送密碼重設郵件。</p>
    </div>

    <form @submit.prevent="handleForgotPassword" class="es-auth-form">
      <div class="es-form-group">
        <label for="email">企業電子信箱</label>
        <input
          v-model="email"
          type="email"
          id="email"
          placeholder="請輸入註冊時使用的電子信箱"
          :disabled="isSubmitting"
          required
        >
      </div>

      <button type="submit" class="es-btn-primary" :disabled="isSubmitting || !email">
        {{ isSubmitting ? '發送中...' : '寄送重設連結' }}
      </button>

      <NuxtLink to="/login" class="es-back-link">
        ← 返回登入
      </NuxtLink>

      <div class="es-privacy-notice">
        Protected by reCAPTCHA and subject to the Privacy Policy and Terms of Service.
      </div>
    </form>
  </AuthLayout>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'guest'
})

const router = useRouter()
const toast = useToast()

const email = ref('')
const isSubmitting = ref(false)

const handleForgotPassword = async () => {
  if (!email.value) {
    toast.add({
      title: '驗證失敗',
      description: '請輸入電子信箱',
      color: 'red'
    })
    return
  }

  isSubmitting.value = true

  try {
    // TODO: Call backend API for password reset
    // For now, simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500))

    toast.add({
      title: '重設連結已發送',
      description: `密碼重設連結已發送至 ${email.value}，請檢查您的信箱`,
      color: 'green'
    })

    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    toast.add({
      title: '錯誤',
      description: '發送重設連結時發生錯誤，請稍後再試',
      color: 'red'
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>
