import React from 'react'
import DashboardLayout from '../components/layout/DashboardLayout'
import LearningHub from '../components/LearningHub'
import { useAuth } from '../context/AuthContext'

const LearningHubPage = () => {
  const { user } = useAuth()

  return (
    <DashboardLayout role={user?.role}>
      <LearningHub />
    </DashboardLayout>
  )
}

export default LearningHubPage


