import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Trophy, TrendingUp, BookOpen, CheckCircle, ChevronRight } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import DashboardLayout from '../../components/layout/DashboardLayout'
import UpcomingTasks from '../../components/dashboard/StudentDashboard/UpcomingTasks'
import RecentActivity from '../../components/dashboard/StudentDashboard/RecentActivity'
import ProgressChart from '../../components/dashboard/StudentDashboard/ProgressChart'
import DashboardHeader from '../../components/DashboardHeader'
import XPBar from '../../components/XPBar'
import Leaderboard from '../../components/Leaderboard'
import CourseCard from '../../components/CourseCard'
import LoadingSpinner from '../../components/shared/LoadingSpinner'
import Card from '../../components/shared/Card'
import Button from '../../components/shared/Button'


const StudentDashboard = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [showLeaderboard, setShowLeaderboard] = useState(false)
  const [leaderboard, setLeaderboard] = useState([]);
  const [dashboardData, setDashboardData] = useState({  
    stats: {},
    upcomingAssignments: [],
    recentActivity: [],
    progressData: [],
    enrolledCourses: []
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
            xp_points: user?.xp_points || 1250,
            level: user?.level || 5,
            enrolled_courses: 4,
            completion_rate: 78,
            xp_trend: 12,
            completion_trend: 5,
            streak: 7
          },
          upcomingAssignments: [
            {
              id: 1,
              title: 'Math Homework - Chapter 5',
              classroom_name: 'Mathematics Grade 10',
              due_date: new Date(Date.now() + 86400000).toISOString(),
              points: 50
            },
            {
              id: 2,
              title: 'Science Lab Report',
              classroom_name: 'Physics',
              due_date: new Date(Date.now() + 172800000).toISOString(),
              points: 100
            },
            {
              id: 3,
              title: 'Essay on Climate Change',
              classroom_name: 'Environmental Science',
              due_date: new Date(Date.now() + 259200000).toISOString(),
              points: 75
            }
          ],
          recentActivity: [
            {
              type: 'assignment_submitted',
              description: 'Submitted "History Essay - World War II"',
              created_at: new Date(Date.now() - 3600000).toISOString(),
              xp_earned: 50
            },
            {
              type: 'achievement_unlocked',
              description: 'Unlocked "Scholar" badge for 10 consecutive days of learning',
              created_at: new Date(Date.now() - 7200000).toISOString(),
              xp_earned: 100
            },
            {
              type: 'resource_accessed',
              description: 'Viewed "Introduction to Calculus" video',
              created_at: new Date(Date.now() - 10800000).toISOString()
            },
            {
              type: 'grade_received',
              description: 'Received grade for "Biology Quiz 3" - 92%',
              created_at: new Date(Date.now() - 86400000).toISOString(),
              xp_earned: 75
            }
          ],
          progressData: [
            { label: 'Mon', xp: 120 },
            { label: 'Tue', xp: 180 },
            { label: 'Wed', xp: 150 },
            { label: 'Thu', xp: 200 },
            { label: 'Fri', xp: 170 },
            { label: 'Sat', xp: 90 },
            { label: 'Sun', xp: 140 }
          ],
          enrolledCourses: [
    {
        id: 1,
        name: 'Mathematics Grade 10',
        description: 'Advanced algebra and geometry',
        xp: 65,
        instructor: 'Mr. Johnson',
        thumbnail: 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&h=250&fit=crop',
        progress: 82,
        role: 'Student',
        status: 'In Progress',
        dueDate: 'Nov 10',
        accentColor: '#4f46e5'
    },
    {
        id: 2,
        name: 'Physics',
        description: 'Mechanics and thermodynamics',
        xp: 45,
        instructor: 'Dr. Smith',
        thumbnail: 'https://images.unsplash.com/photo-1636466497217-26a8cbeaf0aa?w=400&h=250&fit=crop',
        progress: 65,
        role: 'Student',
        status: 'In Progress',
        dueDate: 'Oct 28',
        accentColor: '#db2777'
    },
    {
        id: 3,
        name: 'Environmental Science',
        description: 'Climate change and sustainability',
        xp: 80,
        instructor: 'Ms. Williams',
        thumbnail: 'https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=400&h=250&fit=crop',
        progress: 95,
        role: 'Student',
        status: 'Completed',
        dueDate: 'Sep 15',
        accentColor: '#10b981'
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

  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  if (loading) {
    return (
      <DashboardLayout role="STUDENT">
        <LoadingSpinner size="xl" text="Loading your dashboard..." />
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout role="STUDENT">
      <DashboardHeader />
      <div className="pt-16 lg:pt-0">
        <div className="space-y-6">
          {/* Hero Section with Gradient Background */}
          <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6 md:p-8">
            {/* Decorative elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />

            <div className="relative z-10">
              <div className="flex flex-col lg:flex-row items-start justify-between gap-6">
                <div className="flex-1">
                  <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">
                    {getGreeting()}, {user?.first_name}
                  </h1>
                  <p className="text-slate-300 text-lg mb-6">
                    Ready to continue your learning journey?
                  </p>

                  <div className="flex flex-wrap gap-6">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center">
                        <TrendingUp className="w-6 h-6 text-blue-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">{dashboardData.stats.streak}</p>
                        <p className="text-slate-400 text-sm">Day Streak</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center">
                        <BookOpen className="w-6 h-6 text-purple-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">{dashboardData.stats.enrolled_courses}</p>
                        <p className="text-slate-400 text-sm">Active Courses</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center">
                        <CheckCircle className="w-6 h-6 text-green-400" />
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-white">{dashboardData.stats.completion_rate}%</p>
                        <p className="text-slate-400 text-sm">Completion Rate</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex flex-col gap-3">
                  <Button 
                    variant="slate" 
                    onClick={() => navigate('/learning-hub')}
                    className="bg-white/10 backdrop-blur-sm text-white border-white/20 hover:bg-white/20"
                  >
                    View Learning Path
                    <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                  
                  {/* 🔹 Hero Section Leaderboard Button */}
                  <button
                    onClick={() => setShowLeaderboard(!showLeaderboard)}
                    className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-yellow-500/20 text-yellow-300 border border-yellow-500/30 hover:bg-yellow-500/30 transition-colors"
                  >
                    <Trophy className="w-4 h-4" />
                    {showLeaderboard ? 'Hide' : 'View'} Leaderboard
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* XP Progress Bar */}
          <XPBar currentXP={user?.xp_points || 0} level={user?.level || 1} />

          {/* 🔹 Slide-in Leaderboard (no modal) */}
          <Leaderboard
            leaderboard={leaderboard}
            showLeaderboard={showLeaderboard}
            setShowLeaderboard={setShowLeaderboard}
          />

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column - 2/3 width */}
            <div className="lg:col-span-2 space-y-6">
              <UpcomingTasks assignments={dashboardData.upcomingAssignments} />

              {/* Enrolled Courses */}
              <Card title="My Courses" subtitle="Continue where you left off">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                  {dashboardData.enrolledCourses.map(course => (
                    <CourseCard key={course.id} course={course} />
                  ))}
                </div>
              </Card>

              <ProgressChart progressData={dashboardData.progressData} />
            </div>

            {/* Right Column - 1/3 width */}
            <div className="space-y-6">
              <RecentActivity activities={dashboardData.recentActivity} />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

export default StudentDashboard