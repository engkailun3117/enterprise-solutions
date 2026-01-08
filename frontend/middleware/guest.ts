export default defineNuxtRouteMiddleware((to, from) => {
  const api = useApi()

  // If user is already authenticated, redirect to dashboard
  if (api.isAuthenticated()) {
    if (api.isAdmin()) {
      return navigateTo('/admin/review')
    } else {
      return navigateTo('/dashboard')
    }
  }
})
