import React from 'react';
// 1. We no longer need useAuth here
// import { useAuth } from '../../context/AuthContext';
import SiteNavbar from '../../components/layout/SiteNavbar';
import ClassHeader from '../../components/classroom/ClassHeader';
import Feed from '../../components/classroom/Feed';
import Sidebar from '../../components/classroom/Sidebar';

// Our custom hooks and sidebar widgets
import { useStudentDashboardFeed } from '../../hooks/useStudentDashboardFeed';
import StudentProfileCard from '../../components/dashboard/StudentDashboard/StudentProfileCard';
import MySkillSpacesCard from '../../components/dashboard/StudentDashboard/MySkillSpacesCard';
import LeaderboardCard from '../../components/dashboard/StudentDashboard/LeaderboardCard';

// 2. Create the same dummy user here
const DUMMY_USER = {
  id: 'student-123',
  username: 'test_student',
  avatar_url: null,
};

const StudentDashboard = () => {
  // 3. Use the dummy user object
  const user = DUMMY_USER;
  
  // 4. Fetch the personalized feed data (hook no longer needs userId)
  const { posts, isLoading } = useStudentDashboardFeed();

  // 5. Create the array of widgets for the sidebar
  //    These components no longer need the user prop
  const sidebarWidgets = [
    <StudentProfileCard />,
    <MySkillSpacesCard />,
    <LeaderboardCard />
  ];

  return (
    <div className="bg-gray-50 min-h-screen">
      {/* This component might rely on AuthContext. 
          If it crashes, you may need to wrap it in <AuthProvider> in main.jsx
          or modify it to also use a dummy user.
          For now, we'll assume it's okay.
      */}
      <SiteNavbar />
      
      {/* 6. Use the dummy user's username in the header */}
      <ClassHeader
        title="My Dashboard"
        description={`Welcome back, ${user.username}! Here's what's new.`}
      />

      {/* 2-Column "Subreddit" Layout */}
      <div className="max-w-7xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* === MAIN FEED (LEFT) === */}
        <div className="md:col-span-2">
          <Feed posts={posts} isLoading={isLoading} />
        </div>

        {/* === SIDEBAR (RIGHT) === */}
        <div className="md:col-span-1">
          <Sidebar widgets={sidebarWidgets} />
        </div>

      </div>
    </div>
  );
};

export default StudentDashboard;