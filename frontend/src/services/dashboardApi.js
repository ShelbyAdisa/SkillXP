import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// ============================================
// STUDENT DASHBOARD API
// ============================================

export const studentDashboardApi = {
  // Get student dashboard overview
  getDashboardData: async () => {
    try {
      const response = await apiClient.get('/student/dashboard/')
      return response.data
    } catch (error) {
      console.error('Error fetching student dashboard:', error)
      throw error
    }
  },

  // Get upcoming assignments
  getUpcomingAssignments: async () => {
    try {
      const response = await apiClient.get('/classroom/assignments/upcoming/')
      return response.data
    } catch (error) {
      console.error('Error fetching assignments:', error)
      throw error
    }
  },

  // Get enrolled courses
  getEnrolledCourses: async () => {
    try {
      const response = await apiClient.get('/classroom/enrollments/')
      return response.data
    } catch (error) {
      console.error('Error fetching courses:', error)
      throw error
    }
  },

  // Get XP progress
  getXPProgress: async (days = 7) => {
    try {
      const response = await apiClient.get(`/rewards/xp-progress/?days=${days}`)
      return response.data
    } catch (error) {
      console.error('Error fetching XP progress:', error)
      throw error
    }
  },

  // Get recent activity
  getRecentActivity: async () => {
    try {
      const response = await apiClient.get('/analytics/student-activity/')
      return response.data
    } catch (error) {
      console.error('Error fetching activity:', error)
      throw error
    }
  },
}

// ============================================
// TEACHER DASHBOARD API
// ============================================

export const teacherDashboardApi = {
  // Get teacher dashboard overview
  getDashboardData: async () => {
    try {
      const response = await apiClient.get('/teacher/dashboard/')
      return response.data
    } catch (error) {
      console.error('Error fetching teacher dashboard:', error)
      throw error
    }
  },

  // Get teacher's classes
  getClasses: async () => {
    try {
      const response = await apiClient.get('/classroom/my-classes/')
      return response.data
    } catch (error) {
      console.error('Error fetching classes:', error)
      throw error
    }
  },

  // Get pending submissions for grading
  getPendingGrading: async () => {
    try {
      const response = await apiClient.get('/classroom/submissions/pending/')
      return response.data
    } catch (error) {
      console.error('Error fetching pending grading:', error)
      throw error
    }
  },

  // Get student performance data
  getStudentPerformance: async (classId = null) => {
    try {
      const url = classId
        ? `/analytics/student-performance/?class_id=${classId}`
        : '/analytics/student-performance/'
      const response = await apiClient.get(url)
      return response.data
    } catch (error) {
      console.error('Error fetching student performance:', error)
      throw error
    }
  },

  // Get class analytics
  getClassAnalytics: async (classId) => {
    try {
      const response = await apiClient.get(`/analytics/classroom/${classId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching class analytics:', error)
      throw error
    }
  },
}

// ============================================
// PARENT DASHBOARD API
// ============================================

export const parentDashboardApi = {
  // Get parent dashboard overview
  getDashboardData: async () => {
    try {
      const response = await apiClient.get('/parent/dashboard/')
      return response.data
    } catch (error) {
      console.error('Error fetching parent dashboard:', error)
      throw error
    }
  },

  // Get children information
  getChildren: async () => {
    try {
      const response = await apiClient.get('/parent/children/')
      return response.data
    } catch (error) {
      console.error('Error fetching children:', error)
      throw error
    }
  },

  // Get specific child's progress
  getChildProgress: async (childId) => {
    try {
      const response = await apiClient.get(`/parent/child/${childId}/progress/`)
      return response.data
    } catch (error) {
      console.error('Error fetching child progress:', error)
      throw error
    }
  },

  // Get alerts for children
  getAlerts: async () => {
    try {
      const response = await apiClient.get('/parent/alerts/')
      return response.data
    } catch (error) {
      console.error('Error fetching alerts:', error)
      throw error
    }
  },

  // Get transport information
  getTransportInfo: async (childId) => {
    try {
      const response = await apiClient.get(`/transport/student/${childId}/`)
      return response.data
    } catch (error) {
      console.error('Error fetching transport info:', error)
      throw error
    }
  },
}

// ============================================
// ADMIN DASHBOARD API
// ============================================

export const adminDashboardApi = {
  // Get admin dashboard overview
  getDashboardData: async () => {
    try {
      const response = await apiClient.get('/admin/dashboard/')
      return response.data
    } catch (error) {
      console.error('Error fetching admin dashboard:', error)
      throw error
    }
  },

  // Get platform statistics
  getPlatformStats: async () => {
    try {
      const response = await apiClient.get('/analytics/platform-stats/')
      return response.data
    } catch (error) {
      console.error('Error fetching platform stats:', error)
      throw error
    }
  },

  // Get user distribution
  getUserDistribution: async () => {
    try {
      const response = await apiClient.get('/analytics/user-distribution/')
      return response.data
    } catch (error) {
      console.error('Error fetching user distribution:', error)
      throw error
    }
  },

  // Get system health metrics
  getSystemHealth: async () => {
    try {
      const response = await apiClient.get('/admin/system-health/')
      return response.data
    } catch (error) {
      console.error('Error fetching system health:', error)
      throw error
    }
  },

  // Get school performance data
  getSchoolPerformance: async () => {
    try {
      const response = await apiClient.get('/analytics/school-performance/')
      return response.data
    } catch (error) {
      console.error('Error fetching school performance:', error)
      throw error
    }
  },
}

// ============================================
// SCHOOL ADMIN DASHBOARD API
// ============================================

export const schoolAdminDashboardApi = {
  // Get school admin dashboard overview
  getDashboardData: async () => {
    try {
      const response = await apiClient.get('/school-admin/dashboard/')
      return response.data
    } catch (error) {
      console.error('Error fetching school admin dashboard:', error)
      throw error
    }
  },

  // Get school statistics
  getSchoolStats: async () => {
    try {
      const response = await apiClient.get('/analytics/school-stats/')
      return response.data
    } catch (error) {
      console.error('Error fetching school stats:', error)
      throw error
    }
  },

  // Get school classrooms
  getClassrooms: async () => {
    try {
      const response = await apiClient.get('/classroom/school-classrooms/')
      return response.data
    } catch (error) {
      console.error('Error fetching classrooms:', error)
      throw error
    }
  },

  // Get school users
  getSchoolUsers: async (role = null) => {
    try {
      const url = role ? `/users/school-users/?role=${role}` : '/users/school-users/'
      const response = await apiClient.get(url)
      return response.data
    } catch (error) {
      console.error('Error fetching school users:', error)
      throw error
    }
  },

  // Get transport management
  getTransportData: async () => {
    try {
      const response = await apiClient.get('/transport/school-transport/')
      return response.data
    } catch (error) {
      console.error('Error fetching transport data:', error)
      throw error
    }
  },
}

// ============================================
// COMMON ANALYTICS API
// ============================================

export const analyticsApi = {
  // Get leaderboard
  getLeaderboard: async (scope = 'school', limit = 10) => {
    try {
      const response = await apiClient.get(`/rewards/leaderboard/?scope=${scope}&limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
      throw error
    }
  },

  // Get notifications
  getNotifications: async (limit = 20) => {
    try {
      const response = await apiClient.get(`/notifications/?limit=${limit}`)
      return response.data
    } catch (error) {
      console.error('Error fetching notifications:', error)
      throw error
    }
  },

  // Mark notification as read
  markNotificationRead: async (notificationId) => {
    try {
      const response = await apiClient.patch(`/notifications/${notificationId}/read/`)
      return response.data
    } catch (error) {
      console.error('Error marking notification as read:', error)
      throw error
    }
  },
}

export default apiClient

// ============================================
// ELIBRARY API
// ============================================

export const elibraryApi = {
  getFeaturedResources: async () => {
    const res = await apiClient.get('/elibrary/resources/featured/')
    return res.data
  },
  getRecentResources: async () => {
    const res = await apiClient.get('/elibrary/resources/recent/')
    return res.data
  },
  search: async (q) => {
    const res = await apiClient.get('/elibrary/search/', { params: { q } })
    return res.data
  },
}

