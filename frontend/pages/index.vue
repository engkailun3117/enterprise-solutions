<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
    <div class="container mx-auto px-4 py-16">
      <div class="max-w-4xl mx-auto text-center">
        <!-- Hero Section -->
        <div class="mb-12">
          <h1 class="text-5xl font-bold text-gray-900 dark:text-white mb-4">
            供應商入駐平台
          </h1>
          <p class="text-xl text-gray-600 dark:text-gray-300 mb-8">
            Supplier Onboarding Platform
          </p>
          <p class="text-lg text-gray-700 dark:text-gray-400 max-w-2xl mx-auto">
            歡迎使用智能供應商入駐管理系統。我們提供簡便的註冊流程和專業的審核服務，幫助您快速成為我們的合作夥伴。
          </p>
        </div>

        <!-- Feature Cards -->
        <div class="grid md:grid-cols-3 gap-6 mb-12">
          <UCard>
            <div class="text-center p-4">
              <div class="text-4xl mb-3">📝</div>
              <h3 class="text-lg font-semibold mb-2">簡單註冊</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                快速註冊帳號，填寫企業基本資料
              </p>
            </div>
          </UCard>

          <UCard>
            <div class="text-center p-4">
              <div class="text-4xl mb-3">🔍</div>
              <h3 class="text-lg font-semibold mb-2">專業審核</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                管理員仔細審核，確保合作品質
              </p>
            </div>
          </UCard>

          <UCard>
            <div class="text-center p-4">
              <div class="text-4xl mb-3">✅</div>
              <h3 class="text-lg font-semibold mb-2">即時追蹤</h3>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                隨時查看申請狀態和審核結果
              </p>
            </div>
          </UCard>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <UButton size="xl" to="/register" v-if="!isAuthenticated">
            立即註冊
          </UButton>
          <UButton size="xl" variant="soft" to="/login" v-if="!isAuthenticated">
            登入系統
          </UButton>
          <UButton size="xl" to="/dashboard" v-if="isAuthenticated && !isAdmin">
            進入儀表板
          </UButton>
          <UButton size="xl" to="/admin/review" v-if="isAuthenticated && isAdmin">
            管理後台
          </UButton>
          <UButton size="xl" variant="soft" color="red" @click="handleLogout" v-if="isAuthenticated">
            登出
          </UButton>
        </div>

        <!-- Info Section -->
        <div class="mt-16">
          <UCard>
            <div class="text-left space-y-4">
              <h3 class="text-xl font-semibold">申請流程</h3>
              <ol class="list-decimal list-inside space-y-2 text-gray-700 dark:text-gray-300">
                <li>註冊個人帳號</li>
                <li>填寫企業基本資料（統一編號、公司名稱、負責人等）</li>
                <li>提交申請，等待審核</li>
                <li>管理員審核通過後，收到 Email 通知</li>
                <li>開始合作</li>
              </ol>
            </div>
          </UCard>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const toast = useToast()
const api = useApi()

const isAuthenticated = ref(false)
const isAdmin = ref(false)

onMounted(() => {
  isAuthenticated.value = api.isAuthenticated()
  isAdmin.value = api.isAdmin()
})

const handleLogout = () => {
  api.logout()
  toast.add({
    title: '已登出',
    description: '您已成功登出',
    color: 'green'
  })
  isAuthenticated.value = false
  isAdmin.value = false
}
</script>