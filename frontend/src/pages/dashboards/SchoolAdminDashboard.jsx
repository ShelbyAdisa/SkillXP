import React, { useState, useEffect } from 'react'
import { useAuth } from '../../context/AuthContext'
import DashboardLayout from '../../components/layout/DashboardLayout'
import StatCard from '../../components/shared/StatCard'
import LoadingSpinner from '../../components/shared/LoadingSpinner'
import Card from '../../components/shared/Card'
import Button from '../../components/shared/Button'
import Badge from '../../components/shared/Badge'

const SchoolAdminDashboard = () => {
  const { user } = useAuth()
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState({
    stats: {},
    classrooms: [],
    recentActivity: []
  })

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      // TODO: Replace with actual API calls
      setTimeout(() => {
        setDashboardData({
          stats: {
            total_students: 1250,
            total_teachers: 85,
            total_classes: 42,
            avg_attendance: 93
          },
          classrooms: [
            {
              id: 1,
              name: 'Mathematics - Grade 10',
              teacher: 'Mr. Johnson',
              students: 32,
              status: 'active'
            },
            {
              id: 2,
              name: 'Physics - Grade 11',
              teacher: 'Dr. Smith',
              students: 28,
              status: 'active'
            },
            {
              id: 3,
              name: 'English Literature - Grade 9',
              teacher: 'Ms. Williams',
              students: 35,
              status: 'active'
            }
          ],
          recentActivity: [
            {
              id: 1,
              type: 'teacher_added',
              description: 'New teacher added: Dr. Sarah Chen (Chemistry)',
              timestamp: '1 hour ago'
            },
            {
              id: 2,
              type: 'class_created',
              description: 'New class created: Biology - Grade 10',
              timestamp: '3 hours ago'
            },
            {
              id: 3,
              type: 'transport_update',
              description: 'Bus Route 5 updated with new stops',
              timestamp: '1 day ago'
            }
          ]
        })
        setLoading(false)
      }, 1000)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <DashboardLayout role="SCHOOL_ADMIN">
        <LoadingSpinner size="xl" text="Loading school dashboard..." />
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout role="SCHOOL_ADMIN">
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              School Administration 🏫
            </h1>
            <p className="text-gray-600 mt-1">
              Manage your school operations and monitor performance
            </p>
          </div>
          <Button variant="primary">School Settings</Button>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Total Students"
            value={dashboardData.stats.total_students}
            icon={<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" /></svg>}
            color="blue"
          />
          
          <StatCard
            title="Total Teachers"
            value={dashboardData.stats.total_teachers}
            icon={<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" /></svg>}
            color="green"
          />
          
          <StatCard
            title="Active Classes"
            value={dashboardData.stats.total_classes}
            icon={<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" /></svg>}
            color="purple"
          />
          
          <StatCard
            title="Avg Attendance"
            value={dashboardData.stats.avg_attendance}
            icon={<svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" /></svg>}
            color="yellow"
            suffix="%"
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - 2/3 width */}
          <div className="lg:col-span-2 space-y-6">
            {/* Classrooms */}
            <Card title="Active Classrooms" subtitle="Manage school classes">
              <div className="space-y-3 mt-4">
                {dashboardData.classrooms.map((classroom) => (
                  <div key={classroom.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div>
                      <h4 className="font-medium text-gray-900">{classroom.name}</h4>
                      <p className="text-sm text-gray-600">Teacher: {classroom.teacher}</p>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="text-right">
                        <p className="text-sm font-semibold text-gray-900">{classroom.students} students</p>
                      </div>
                      <Badge variant="success">{classroom.status}</Badge>
                    </div>
                  </div>
                ))}
              </div>
              <Button variant="primary" size="sm" className="mt-4">
                View All Classes
              </Button>
            </Card>

            {/* Recent Activity */}
            <Card title="Recent Activity" subtitle="Latest school updates">
              <div className="space-y-3 mt-4">
                {dashboardData.recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                    <span className="text-2xl">
                      {activity.type === 'teacher_added' ? '👨‍🏫' :
                       activity.type === 'class_created' ? '📚' : '🚌'}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{activity.description}</p>
                      <p className="text-xs text-gray-500 mt-1">{activity.timestamp}</p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Right Column - 1/3 width */}
          <div className="space-y-6">
            <Card title="Quick Management">
              <div className="space-y-2 mt-4">
                <button className="w-full p-3 text-left bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">👥</span>
                    <div>
                      <p className="font-medium text-gray-900">Manage Users</p>
                      <p className="text-xs text-gray-600">Teachers & Students</p>
                    </div>
                  </div>
                </button>
                
                <button className="w-full p-3 text-left bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">🏫</span>
                    <div>
                      <p className="font-medium text-gray-900">Class Management</p>
                      <p className="text-xs text-gray-600">Create/edit classes</p>
                    </div>
                  </div>
                </button>
                
                <button className="w-full p-3 text-left bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">🚌</span>
                    <div>
                      <p className="font-medium text-gray-900">Transport</p>
                      <p className="text-xs text-gray-600">Manage bus routes</p>
                    </div>
                  </div>
                </button>
                
                <button className="w-full p-3 text-left bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">📖</span>
                    <div>
                      <p className="font-medium text-gray-900">Library</p>
                      <p className="text-xs text-gray-600">School resources</p>
                    </div>
                  </div>
                </button>
                
                <button className="w-full p-3 text-left bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <span className="text-xl">📊</span>
                    <div>
                      <p className="font-medium text-gray-900">Analytics</p>
                      <p className="text-xs text-gray-600">School performance</p>
                    </div>
                  </div>
                </button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default SchoolAdminDashboard

