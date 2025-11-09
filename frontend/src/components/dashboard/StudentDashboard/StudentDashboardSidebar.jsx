import React from 'react';
import StudentProfileCard from './StudentProfileCard';
import MySkillSpacesCard from './MySkillSpacesCard';
// 1. Removed LeaderboardCard import

/**
 * This is a dedicated sidebar for the Student Dashboard.
 * It directly renders the widgets we need (Profile, SkillSpaces, etc.)
 * and passes them the props they require.
 */
export default function StudentDashboardSidebar({ user, studentData }) {
  // We can add more props like 'studentData' for XP and courses later
  
  return (
    <div className="space-y-6">
      {/* We pass the 'user' prop to the profile card, 
        but it's also now using a DUMMY_USER internally,
        so this prop is redundant but good practice.
      */}
      <StudentProfileCard user={user} />
      
      <MySkillSpacesCard />
      
      {/* 2. Removed the <LeaderboardCard /> component */}
    </div>
  );
}