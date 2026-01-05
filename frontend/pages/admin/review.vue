<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div class="flex justify-between items-center">
          <div>
            <h1 class="text-3xl font-bold">管理員審核中心</h1>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-400" v-if="user">
              管理員：{{ user.username }}
            </p>
          </div>
          <div class="flex gap-3">
            <UButton variant="soft" to="/">
              返回首頁
            </UButton>
            <UButton color="red" variant="soft" @click="handleLogout">
              登出
            </UButton>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8" v-if="stats">
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-gray-900 dark:text-white">{{ stats.total_applications }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">總申請數</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-blue-600">{{ stats.pending }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">待審核</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-green-600">{{ stats.approved }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">已批准</div>
          </div>
        </UCard>
        <UCard>
          <div class="text-center">
            <div class="text-3xl font-bold text-red-600">{{ stats.rejected }}</div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mt-1">已拒絕</div>
          </div>
        </UCard>
      </div>

      <!-- Filter Tabs -->
      <div class="mb-6">
        <div class="flex gap-2">
          <UButton
            :variant="statusFilter === null ? 'solid' : 'soft'"
            @click="setFilter(null)"
          >
            全部
          </UButton>
          <UButton
            color="blue"
            :variant="statusFilter === 'pending' ? 'solid' : 'soft'"
            @click="setFilter('pending')"
          >
            待審核
          </UButton>
          <UButton
            color="green"
            :variant="statusFilter === 'approved' ? 'solid' : 'soft'"
            @click="setFilter('approved')"
          >
            已批准
          </UButton>
          <UButton
            color="red"
            :variant="statusFilter === 'rejected' ? 'solid' : 'soft'"
            @click="setFilter('rejected')"
          >
            已拒絕
          </UButton>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="text-center py-12">
        <div class="text-gray-500">載入中...</div>
      </div>

      <!-- Applications List -->
      <div v-else-if="applications.length > 0" class="space-y-4">
        <UCard v-for="app in applications" :key="app.company_id">
          <div class="space-y-4">
            <!-- Header Row -->
            <div class="flex justify-between items-start">
              <div>
                <h3 class="text-lg font-semibold">{{ app.company_name }}</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">統一編號：{{ app.company_id }}</p>
              </div>
              <UBadge
                :color="getStatusColor(app.status)"
                size="lg"
              >
                {{ getStatusText(app.status) }}
              </UBadge>
            </div>

            <!-- Application Details -->
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-600 dark:text-gray-400">負責人：</span>
                <span class="font-medium">{{ app.company_head }}</span>
              </div>
              <div>
                <span class="text-gray-600 dark:text-gray-400">Email：</span>
                <span class="font-medium">{{ app.company_email }}</span>
              </div>
              <div v-if="app.company_link" class="col-span-2">
                <span class="text-gray-600 dark:text-gray-400">網址：</span>
                <a :href="app.company_link" target="_blank" class="font-medium text-blue-600 hover:underline">
                  {{ app.company_link }}
                </a>
              </div>
              <div class="col-span-2">
                <span class="text-gray-600 dark:text-gray-400">提交時間：</span>
                <span class="font-medium">{{ formatDate(app.created_at) }}</span>
              </div>
            </div>

            <!-- Rejection Reason (if rejected) -->
            <div v-if="app.status === 'rejected' && app.rejection_reason" class="bg-red-50 dark:bg-red-900/20 p-3 rounded">
              <p class="text-sm text-red-800 dark:text-red-200">
                <strong>拒絕原因：</strong>{{ app.rejection_reason }}
              </p>
            </div>

            <!-- Review Info (if reviewed) -->
            <div v-if="app.reviewed_at" class="text-xs text-gray-500 dark:text-gray-400">
              審核時間：{{ formatDate(app.reviewed_at) }}
            </div>

            <!-- Action Buttons (for pending applications) -->
            <div v-if="app.status === 'pending'" class="flex gap-3 pt-3 border-t dark:border-gray-700">
              <UButton
                color="green"
                @click="approveApplication(app.company_id)"
                :loading="processingId === app.company_id"
              >
                批准
              </UButton>
              <UButton
                color="red"
                variant="soft"
                @click="openRejectModal(app.company_id)"
                :disabled="processingId === app.company_id"
              >
                拒絕
              </UButton>
            </div>
          </div>
        </UCard>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <UCard>
          <div class="py-8">
            <p class="text-gray-600 dark:text-gray-400">目前沒有{{ getFilterText() }}的申請</p>
          </div>
        </UCard>
      </div>
    </div>

    <!-- Reject Modal -->
    <UModal v-model="showRejectModal">
      <UCard>
        <template #header>
          <h3 class="text-lg font-semibold">拒絕申請</h3>
        </template>

        <div class="space-y-4">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            請提供拒絕原因：
          </p>
          <UTextarea
            v-model="rejectionReason"
            placeholder="請輸入拒絕原因..."
            :rows="4"
          />
        </div>

        <template #footer>
          <div class="flex justify-end gap-3">
            <UButton variant="soft" @click="closeRejectModal">
              取消
            </UButton>
            <UButton
              color="red"
              @click="confirmReject"
              :disabled="!rejectionReason.trim()"
              :loading="processingId !== null"
            >
              確認拒絕
            </UButton>
          </div>
        </template>
      </UCard>
    </UModal>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const toast = useToast()
const api = useApi()

const user = ref(api.getStoredUser())
const applications = ref<any[]>([])
const stats = ref<any>(null)
const loading = ref(true)
const statusFilter = ref<string | null>(null)
const processingId = ref<string | null>(null)
const showRejectModal = ref(false)
const rejectionReason = ref('')
const rejectingCompanyId = ref<string | null>(null)

// Check admin access
onMounted(async () => {
  if (!api.isAuthenticated()) {
    toast.add({
      title: '請先登入',
      description: '您需要登入才能訪問管理後台',
      color: 'yellow'
    })
    router.push('/login')
    return
  }

  if (!api.isAdmin()) {
    toast.add({
      title: '權限不足',
      description: '您沒有管理員權限',
      color: 'red'
    })
    router.push('/dashboard')
    return
  }

  await loadData()
})

const loadData = async () => {
  loading.value = true
  await Promise.all([loadApplications(), loadStats()])
  loading.value = false
}

const loadApplications = async () => {
  const { data, error } = await api.getAllApplications(statusFilter.value || undefined)

  if (error) {
    toast.add({
      title: '載入失敗',
      description: error,
      color: 'red'
    })
  } else {
    applications.value = data || []
  }
}

const loadStats = async () => {
  const { data, error } = await api.getAdminStats()

  if (error) {
    console.error('Failed to load stats:', error)
  } else {
    stats.value = data
  }
}

const setFilter = async (filter: string | null) => {
  statusFilter.value = filter
  await loadApplications()
}

const approveApplication = async (companyId: string) => {
  processingId.value = companyId

  const { data, error } = await api.reviewApplication(companyId, { action: 'approve' })

  if (error) {
    toast.add({
      title: '批准失敗',
      description: error,
      color: 'red'
    })
  } else {
    toast.add({
      title: '批准成功',
      description: '申請已成功批准',
      color: 'green'
    })
    await loadData()
  }

  processingId.value = null
}

const openRejectModal = (companyId: string) => {
  rejectingCompanyId.value = companyId
  rejectionReason.value = ''
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  rejectingCompanyId.value = null
  rejectionReason.value = ''
}

const confirmReject = async () => {
  if (!rejectingCompanyId.value || !rejectionReason.value.trim()) return

  processingId.value = rejectingCompanyId.value

  const { data, error } = await api.reviewApplication(rejectingCompanyId.value, {
    action: 'reject',
    rejection_reason: rejectionReason.value
  })

  if (error) {
    toast.add({
      title: '拒絕失敗',
      description: error,
      color: 'red'
    })
  } else {
    toast.add({
      title: '已拒絕',
      description: '申請已被拒絕',
      color: 'green'
    })
    closeRejectModal()
    await loadData()
  }

  processingId.value = null
}

const handleLogout = () => {
  api.logout()
  toast.add({
    title: '已登出',
    description: '您已成功登出',
    color: 'green'
  })
  router.push('/login')
}

const getStatusColor = (status: string) => {
  switch (status) {
    case 'pending': return 'blue'
    case 'approved': return 'green'
    case 'rejected': return 'red'
    default: return 'gray'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'pending': return '待審核'
    case 'approved': return '已批准'
    case 'rejected': return '已拒絕'
    default: return status
  }
}

const getFilterText = () => {
  if (!statusFilter.value) return ''
  return getStatusText(statusFilter.value)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-TW')
}
</script>
