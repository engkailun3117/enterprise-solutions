<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p class="text-gray-600 dark:text-gray-400">正在跳轉...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const api = useApi()

onMounted(() => {
  // Check if user is already authenticated
  if (api.isAuthenticated()) {
    // Redirect to dashboard if logged in
    if (api.isAdmin()) {
      router.push('/admin/review')
    } else {
      router.push('/dashboard')
    }
  } else {
    // Redirect to login if not logged in
    router.push('/login')
  }
})
</script>
