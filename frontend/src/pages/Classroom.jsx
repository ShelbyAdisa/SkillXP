import React, { useEffect, useState } from 'react'
import DashboardLayout from '../components/layout/DashboardLayout'
import { useAuth } from '../context/AuthContext'
import CourseCard from '../components/CourseCard'
import LoadingSpinner from '../components/shared/LoadingSpinner'
import Card from '../components/shared/Card' // Keep for teacher view and empty state

// --- DUMMY DATA (Ensuring all teacher courses have details) ---
const DUMMY_COURSES = [
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
// --- DUMMY DATA END ---

const Classroom = () => {
    const { user } = useAuth()
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [courses, setCourses] = useState([])
    const isTeacher = user?.role === 'TEACHER'

    useEffect(() => {
        const loadCourses = async () => {
            setLoading(true)
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 500))

            const userCourses = DUMMY_COURSES.filter(c => c.role === (isTeacher ? 'Teacher' : 'Student'))
            setCourses(userCourses)
            setLoading(false)
        }
        loadCourses()
    }, [isTeacher])

    if (loading) {
        return (
            <DashboardLayout role={user?.role}>
                <div className="flex items-center justify-center min-h-[60vh]">
                    <LoadingSpinner text={`Loading ${isTeacher ? 'classes' : 'courses'}...`} />
                </div>
            </DashboardLayout>
        )
    }

    return (
        <DashboardLayout role={user?.role}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-slate-900 mb-2">
                        {isTeacher ? 'My Classes' : 'My Courses'}
                    </h1>
                    <p className="text-slate-600">
                        {isTeacher
                            ? 'View and manage your active teaching classes.'
                            : 'Your personalized learning paths and enrolled courses.'}
                    </p>
                </div>

                {error && (
                    <div className="mb-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
                        <p className="font-medium">Error loading data</p>
                        <p className="text-sm">{error}</p>
                    </div>
                )}

                <div>
                    {courses.length === 0 ? (
                        <Card>
                            <div className="text-center py-12">
                                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-8 h-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                    </svg>
                                </div>
                                <h3 className="text-lg font-medium text-slate-900 mb-2">No {isTeacher ? 'Classes' : 'Courses'} Found</h3>
                                <p className="text-slate-600">
                                    {isTeacher
                                        ? 'Create your first class to begin teaching.'
                                        : 'Enroll in a course or check with your school administrator.'}
                                </p>
                            </div>
                        </Card>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {courses.map(course => (
                                <CourseCard key={course.id} course={course} />
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </DashboardLayout>
    )
}

export default Classroom