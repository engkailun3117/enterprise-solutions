export default defineNuxtRouteMiddleware((to, from) => {
  const api = useApi()

  // Check if user is authenticated
  if (!api.isAuthenticated()) {
    // Redirect to login page
    return navigateTo('/login')
  }

  // Check if user is admin
  if (!api.isAdmin()) {
    // Redirect to dashboard if not admin
    return navigateTo('/dashboard')
  }
})
