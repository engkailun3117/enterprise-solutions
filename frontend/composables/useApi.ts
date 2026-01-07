interface User {
  id: number
  username: string
  email: string
  role: string
  created_at: string
}

interface CompanyData {
  company_id: string
  company_name: string
  company_head: string
  company_email: string
  company_link?: string
}

interface ReviewAction {
  action: 'approve' | 'reject'
  rejection_reason?: string
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl

  // Helper function to get auth headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token')
    return {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` })
    }
  }

  // ============== Authentication ==============

  const register = async (username: string, email: string, password: string) => {
    try {
      const response = await $fetch('/api/auth/register', {
        method: 'POST',
        baseURL,
        body: { username, email, password },
        headers: {
          'Content-Type': 'application/json'
        }
      }) as { access_token: string, user: User }

      // Store token
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
      }

      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Registration failed'
      }
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await $fetch('/api/auth/login', {
        method: 'POST',
        baseURL,
        body: { username, password },
        headers: {
          'Content-Type': 'application/json'
        }
      }) as { access_token: string, user: User }

      // Store token
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('user', JSON.stringify(response.user))
      }

      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Login failed'
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  const getCurrentUser = async () => {
    try {
      const response = await $fetch('/api/auth/me', {
        method: 'GET',
        baseURL,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Failed to get user info'
      }
    }
  }

  const getStoredUser = (): User | null => {
    if (typeof window === 'undefined') return null
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }

  const isAuthenticated = (): boolean => {
    if (typeof window === 'undefined') return false
    return !!localStorage.getItem('access_token')
  }

  const isAdmin = (): boolean => {
    const user = getStoredUser()
    return user?.role === 'admin'
  }

  // ============== Company/Application ==============

  const createCompany = async (companyData: CompanyData) => {
    try {
      const response = await $fetch('/api/companies', {
        method: 'POST',
        baseURL,
        body: companyData,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'An error occurred'
      }
    }
  }

  const getMyApplication = async () => {
    try {
      const response = await $fetch('/api/companies/my-application', {
        method: 'GET',
        baseURL,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Failed to get application'
      }
    }
  }

  const getCompany = async (companyId: string) => {
    try {
      const response = await $fetch(`/api/companies/${companyId}`, {
        method: 'GET',
        baseURL,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'An error occurred'
      }
    }
  }

  // ============== Admin ==============

  const getAllApplications = async (statusFilter?: string) => {
    try {
      const url = statusFilter
        ? `/api/admin/applications?status_filter=${statusFilter}`
        : '/api/admin/applications'

      const response = await $fetch(url, {
        method: 'GET',
        baseURL,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Failed to get applications'
      }
    }
  }

  const reviewApplication = async (companyId: string, review: ReviewAction) => {
    try {
      const response = await $fetch(`/api/admin/applications/${companyId}/review`, {
        method: 'PUT',
        baseURL,
        body: review,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Failed to review application'
      }
    }
  }

  const getAdminStats = async () => {
    try {
      const response = await $fetch('/api/admin/stats', {
        method: 'GET',
        baseURL,
        headers: getAuthHeaders()
      })
      return { data: response, error: null }
    } catch (error: any) {
      return {
        data: null,
        error: error.data?.detail || error.message || 'Failed to get stats'
      }
    }
  }

  // ============== Chatbot ==============

  const sendChatMessage = async (message: string, sessionId: number | null = null) => {
    const response = await $fetch('/api/chatbot/message', {
      method: 'POST',
      baseURL,
      body: { message, session_id: sessionId },
      headers: getAuthHeaders()
    })
    return response
  }

  const getChatSessions = async () => {
    const response = await $fetch('/api/chatbot/sessions', {
      method: 'GET',
      baseURL,
      headers: getAuthHeaders()
    })
    return response
  }

  const getChatMessages = async (sessionId: number) => {
    const response = await $fetch(`/api/chatbot/sessions/${sessionId}/messages`, {
      method: 'GET',
      baseURL,
      headers: getAuthHeaders()
    })
    return response
  }

  const getOnboardingData = async (sessionId: number) => {
    const response = await $fetch(`/api/chatbot/data/${sessionId}`, {
      method: 'GET',
      baseURL,
      headers: getAuthHeaders()
    })
    return response
  }

  const exportOnboardingData = async (sessionId: number) => {
    const response = await $fetch(`/api/chatbot/export/${sessionId}`, {
      method: 'GET',
      baseURL,
      headers: getAuthHeaders()
    })
    return response
  }

  const exportAllOnboardingData = async () => {
    const response = await $fetch('/api/chatbot/export/all', {
      method: 'GET',
      baseURL,
      headers: getAuthHeaders()
    })
    return response
  }

  // Generic methods for backward compatibility
  const post = async (url: string, body: any) => {
    const response = await $fetch(url, {
      method: 'POST',
      baseURL,
      body,
      headers: getAuthHeaders()
    })
    return response
  }

  const get = async (url: string) => {
    const response = await $fetch(url, {
      method: 'GET',
      baseURL,
      headers: getAuthHeaders()
    })
    return response
  }

  return {
    // Auth
    register,
    login,
    logout,
    getCurrentUser,
    getStoredUser,
    isAuthenticated,
    isAdmin,
    // Company
    createCompany,
    getMyApplication,
    getCompany,
    // Admin
    getAllApplications,
    reviewApplication,
    getAdminStats,
    // Chatbot
    sendChatMessage,
    getChatSessions,
    getChatMessages,
    getOnboardingData,
    exportOnboardingData,
    exportAllOnboardingData,
    // Generic
    post,
    get
  }
}
