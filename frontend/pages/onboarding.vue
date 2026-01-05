<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold">供應商入駐申請</h1>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400" v-if="user">
              {{ user.username }}
            </p>
          </div>
          <UButton variant="soft" @click="goToDashboard">
            返回儀表板
          </UButton>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Progress Steps -->
      <div class="mb-8">
        <div class="flex items-center justify-center">
          <div class="flex items-center space-x-4">
            <div class="flex items-center">
              <div class="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white font-semibold">
                1
              </div>
              <span class="ml-2 text-sm font-medium text-blue-600">基本資料</span>
            </div>
            <div class="w-16 h-1 bg-gray-300 dark:bg-gray-600"></div>
            <div class="flex items-center">
              <div class="flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400 font-semibold">
                2
              </div>
              <span class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">AI 資料整合</span>
            </div>
            <div class="w-16 h-1 bg-gray-300 dark:bg-gray-600"></div>
            <div class="flex items-center">
              <div class="flex items-center justify-center w-10 h-10 rounded-full bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400 font-semibold">
                3
              </div>
              <span class="ml-2 text-sm font-medium text-gray-500 dark:text-gray-400">審核</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Form Card -->
      <UCard>
        <template #header>
          <h2 class="text-xl font-semibold">
            企業基本資料
          </h2>
        </template>

        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- Company Name -->
          <UFormGroup label="企業名稱" name="company_name" required>
            <UInput
              v-model="formData.company_name"
              placeholder="例：智群科技股份有限公司"
              size="lg"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <!-- Company ID (統一編號) -->
          <UFormGroup label="統一編號" name="company_id" required hint="請輸入8位數統一編號">
            <UInput
              v-model="formData.company_id"
              placeholder="例：23456789"
              size="lg"
              :disabled="isSubmitting"
              maxlength="8"
            />
          </UFormGroup>

          <!-- Company Head -->
          <UFormGroup label="負責人" name="company_head" required>
            <UInput
              v-model="formData.company_head"
              placeholder="例：林小明"
              size="lg"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <!-- Company Email -->
          <UFormGroup label="聯絡 EMAIL" name="company_email" required>
            <UInput
              v-model="formData.company_email"
              type="email"
              placeholder="例：sales@accton.com"
              size="lg"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <!-- Company Link -->
          <UFormGroup label="公司網址" name="company_link" hint="選填，請輸入完整網址 (包含 https://)">
            <UInput
              v-model="formData.company_link"
              type="url"
              placeholder="例：https://www.accton.com"
              size="lg"
              :disabled="isSubmitting"
            />
          </UFormGroup>

          <!-- Info Alert -->
          <UAlert
            icon="i-heroicons-information-circle"
            color="blue"
            variant="soft"
            title="重要提示"
            description="提交後，您的申請將進入審核流程。每個帳號只能提交一次申請。審核通過後會以 email 通知您。"
          />

          <!-- Submit Button -->
          <div class="flex justify-end space-x-4">
            <UButton
              type="button"
              color="gray"
              variant="soft"
              size="lg"
              :disabled="isSubmitting"
              @click="goToDashboard"
            >
              取消
            </UButton>
            <UButton
              type="submit"
              color="primary"
              size="lg"
              :loading="isSubmitting"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? '提交中...' : '提交申請' }}
            </UButton>
          </div>
        </form>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const toast = useToast()
const api = useApi()

const user = ref(api.getStoredUser())

const formData = ref({
  company_id: '',
  company_name: '',
  company_head: '',
  company_email: '',
  company_link: ''
})

const isSubmitting = ref(false)

// Check authentication and existing application
onMounted(async () => {
  if (!api.isAuthenticated()) {
    toast.add({
      title: '請先登入',
      description: '您需要登入才能提交供應商申請',
      color: 'yellow'
    })
    router.push('/login')
    return
  }

  // Check if user already has an application
  const { data, error } = await api.getMyApplication()
  if (data) {
    toast.add({
      title: '已提交申請',
      description: '您已經提交過供應商申請，每個帳號只能提交一次',
      color: 'yellow'
    })
    router.push('/dashboard')
  }
})

const handleSubmit = async () => {
  isSubmitting.value = true

  try {
    const payload = {
      company_id: formData.value.company_id,
      company_name: formData.value.company_name,
      company_head: formData.value.company_head,
      company_email: formData.value.company_email,
      company_link: formData.value.company_link || undefined
    }

    const { data, error } = await api.createCompany(payload)

    if (error) {
      toast.add({
        title: '提交失敗',
        description: error,
        color: 'red'
      })
    } else {
      toast.add({
        title: '提交成功',
        description: '您的供應商申請已成功提交，將在3-5個工作天內完成審核',
        color: 'green'
      })
      router.push('/dashboard')
    }
  } catch (error: any) {
    toast.add({
      title: '錯誤',
      description: '提交時發生未預期的錯誤',
      color: 'red'
    })
  } finally {
    isSubmitting.value = false
  }
}

const goToDashboard = () => {
  router.push('/dashboard')
}
</script>
