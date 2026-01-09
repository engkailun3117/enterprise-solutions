<template>
  <div class="dashboard-layout">
    <!-- Left Sidebar -->
    <aside class="dashboard-sidebar">
      <!-- Logo/Brand -->
      <div class="dashboard-brand">
        <div class="brand-logo">GSA</div>
        <div class="brand-text">企業通</div>
      </div>

      <!-- Navigation Menu -->
      <nav class="dashboard-nav">
        <NuxtLink to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
          <span class="nav-icon">📊</span>
          <span class="nav-text">戰情首頁</span>
        </NuxtLink>

        <NuxtLink to="/dashboard/company" class="nav-item" :class="{ active: $route.path === '/dashboard/company' }">
          <span class="nav-icon">📋</span>
          <span class="nav-text">公司資料</span>
        </NuxtLink>

        <NuxtLink to="/dashboard/settings" class="nav-item" :class="{ active: $route.path === '/dashboard/settings' }">
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">全域設定</span>
        </NuxtLink>

        <NuxtLink to="/dashboard/notifications" class="nav-item" :class="{ active: $route.path === '/dashboard/notifications' }">
          <span class="nav-icon">🔔</span>
          <span class="nav-text">通知中心</span>
        </NuxtLink>
      </nav>

      <!-- User Profile Section -->
      <div class="dashboard-user">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-info">
          <div class="user-name">{{ userName }}</div>
          <button @click="handleLogout" class="btn-logout">退出</button>
        </div>
      </div>
    </aside>

    <!-- Main Content Area -->
    <div class="dashboard-main">
      <!-- Top Header -->
      <header class="dashboard-header">
        <div class="search-bar">
          <input type="text" placeholder="輸入人名 / 關鍵字搜尋..." disabled>
          <button class="btn-search" disabled>🔍</button>
        </div>

        <div class="header-actions">
          <button class="btn-icon" disabled>💬</button>
          <button class="btn-icon" disabled>🔔</button>
        </div>
      </header>

      <!-- Page Content -->
      <main class="dashboard-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const api = useApi()

// Get actual user data from auth
const storedUser = api.getStoredUser()
const userName = ref(storedUser?.username || 'User')
const userInitials = computed(() => {
  return userName.value
    .split(' ')
    .map(n => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const handleLogout = () => {
  // Clear auth token and user data using api.logout()
  api.logout()
  // Clear any chatbot session data
  localStorage.removeItem('chatbot_session_id')
  // Redirect to login page
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* Sidebar Styles */
.dashboard-sidebar {
  width: 240px;
  background-color: #1a1a2e;
  color: white;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
}

.dashboard-brand {
  padding: 24px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-logo {
  width: 40px;
  height: 40px;
  background-color: #d14d41;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.brand-text {
  font-size: 18px;
  font-weight: 600;
}

.dashboard-nav {
  flex: 1;
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav-item.active {
  background-color: rgba(209, 77, 65, 0.1);
  color: white;
  border-left-color: #d14d41;
}

.nav-icon {
  font-size: 20px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.dashboard-user {
  padding: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #d14d41;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
}

.btn-logout {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
}

.btn-logout:hover {
  color: white;
}

/* Main Content Styles */
.dashboard-main {
  flex: 1;
  margin-left: 240px;
  display: flex;
  flex-direction: column;
}

.dashboard-header {
  background-color: white;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.search-bar {
  flex: 1;
  max-width: 500px;
  display: flex;
  align-items: center;
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 8px 16px;
}

.search-bar input {
  flex: 1;
  border: none;
  background: none;
  outline: none;
  font-size: 14px;
  color: #999;
}

.btn-search {
  background: none;
  border: none;
  cursor: not-allowed;
  font-size: 18px;
  opacity: 0.5;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background-color: #f5f5f5;
  cursor: not-allowed;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.5;
}

.dashboard-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-sidebar {
    width: 60px;
  }

  .brand-text,
  .nav-text,
  .user-info {
    display: none;
  }

  .dashboard-main {
    margin-left: 60px;
  }
}
</style>
