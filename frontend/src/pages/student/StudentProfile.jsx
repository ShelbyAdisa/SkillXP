import React, { useState } from 'react';
import { User, Mail, Phone, Home, Book, Award, Clock, CheckCircle, BarChart2 } from 'lucide-react';

// Import components
import ProfileHeader from '../../components/profile/ProfileHeader';
import SkillSpaceList from '../../components/profile/SkillSpaceList';
import RecentActivity from '../../components/profile/RecentActivity';
import AchievementsList from '../../components/profile/AchievementsList';
import UpcomingDeadlines from '../../components/profile/UpcomingDeadlines';
import PersonalDetails from '../../components/profile/PersonalDetails';
import EditProfilePicModal from '../../components/profile/EditProfilePicModal'; // <-- NEW IMPORT

// --- Revamped Dummy Data ---
const dummyStudentData = {
  personalInfo: {
    name: 'Alex Johnson',
    email: 'alex.johnson@skillxp.edu',
    avatarUrl: 'https://ui-avatars.com/api/?name=Alex+Johnson&background=4F46E5&color=FFFFFF&size=128',
    studentId: 'SXP-10234',
    school: 'Innovate Academy',
    year: 'Grade 10',
    xp: 8500, // Removed level/next-level data
    phone: '+254 712 345 678', // Kenyan phone
    address: '123 Gitanga Road, Lavington, Nairobi, Kenya' // Kenyan address
  },
  skillSpaces: [
    { 
      id: 1, 
      name: 'Creative Coding with p5.js', 
      overallGrade: 'A-',
      icon: Book,
      grades: [
        { id: 't1', title: 'Assignment 1: Shapes', score: 18, max: 20 },
        { id: 'q1', title: 'Quiz 1: Variables', score: 9, max: 10 },
        { id: 't2', title: 'Assignment 2: Interaction', score: 16, max: 20 },
        { id: 'p1', title: 'Mid-term Project', score: 45, max: 50 },
      ],
      classStats: { min: 40, q1: 65, median: 78, q3: 88, max: 98 },
      studentOverall: 88
    },
    { 
      id: 2, 
      name: 'Web Development Fundamentals', 
      overallGrade: 'B+', 
      icon: BarChart2,
      grades: [
        { id: 't1', title: 'HTML Structure Challenge', score: 8, max: 10 },
        { id: 't2', title: 'CSS Layouts Test', score: 13, max: 20 },
        { id: 'p1', title: 'Portfolio Page Project', score: 38, max: 50 },
      ],
      classStats: { min: 30, q1: 55, median: 72, q3: 81, max: 95 },
      studentOverall: 79
    },
    { 
      id: 3, 
      name: 'Introduction to AI Ethics', 
      overallGrade: 'A', 
      icon: CheckCircle,
      grades: [
        { id: 'e1', title: 'Essay: Bias in Algorithms', score: 28, max: 30 },
        { id: 'd1', title: 'Debate Participation', score: 10, max: 10 },
        { id: 'e2', title: 'Final Paper: AI Governance', score: 48, max: 50 },
      ],
      classStats: { min: 50, q1: 75, median: 85, q3: 92, max: 100 },
      studentOverall: 94
    },
  ],
  recentActivity: [
    { id: 1, type: 'submission', description: 'Submitted "Final Paper: AI Governance" to Introduction to AI Ethics.', date: '2 hours ago' },
    { id: 2, type: 'badge', description: 'Earned "Code Connoisseur" badge.', date: '1 day ago' },
  ],
  achievements: [
    { id: 1, name: 'Creative Coder', description: 'Completed all projects in the Creative Coding SkillSpace.', icon: Award, xp: 50 },
    { id: 2, name: 'Community Helper', description: 'Made 10 helpful forum posts across all SkillSpaces.', icon: Award, xp: 10 },
    { id: 3, name: 'Perfect Start', description: 'Got 100% on the first 3 quizzes of the term.', icon: Award, xp: 25 },
  ],
  upcomingDeadlines: [
    { id: 1, title: 'Final p5.js Animation', skillSpace: 'Creative Coding', dueDate: '2025-11-15T23:59:00' },
    { id: 2, title: 'Peer Review: Portfolio Page', skillSpace: 'Web Development', dueDate: '2025-11-18T23:59:00' },
  ]
};
// --- End Dummy Data ---

// Reusable card wrapper
const ProfileCard = ({ title, icon, children }) => (
  <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
    <div className="px-6 py-4 border-b dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center">
        {icon && React.createElement(icon, { className: "mr-2 h-5 w-5 text-indigo-500" })}
        {title}
      </h3>
    </div>
    <div className="p-6">
      {children}
    </div>
  </div>
);


function StudentProfile() {
  const [studentData, setStudentData] = useState(dummyStudentData);
  const [isEditPicModalOpen, setIsEditPicModalOpen] = useState(false);

  // This function would handle the actual API call
  const handlePictureSave = (newAvatarUrl) => {
    // In a real app, you'd send this to a backend.
    // For now, we just update our dummy state.
    setStudentData(prevData => ({
      ...prevData,
      personalInfo: {
        ...prevData.personalInfo,
        avatarUrl: newAvatarUrl
      }
    }));
    setIsEditPicModalOpen(false);
  };

  if (!studentData) {
    return <div>Loading...</div>;
  }

  return (
    <>
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-4 sm:p-8">
        <div className="max-w-7xl mx-auto">
          
          <ProfileHeader 
            studentInfo={studentData.personalInfo} 
            onEditClick={() => setIsEditPicModalOpen(true)} // <-- WIRED UP
          />

          <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <div className="lg:col-span-1 flex flex-col gap-8">
              <ProfileCard title="Contact Information" icon={User}>
                <PersonalDetails 
                  info={studentData.personalInfo} 
                />
              </ProfileCard>

              <ProfileCard title="Recent Activity" icon={CheckCircle}>
                <RecentActivity 
                  activity={studentData.recentActivity} 
                />
              </ProfileCard>
              
              <ProfileCard title="Upcoming Deadlines" icon={Clock}>
                <UpcomingDeadlines 
                  deadlines={studentData.upcomingDeadlines} 
                />
              </ProfileCard>
            </div>

            <div className="lg:col-span-2 flex flex-col gap-8">
              <ProfileCard title="My SkillSpaces" icon={Book}>
                <SkillSpaceList
                  skillSpaces={studentData.skillSpaces} 
                />
              </ProfileCard>

              <ProfileCard title="Achievements" icon={Award}>
                <AchievementsList
                  achievements={studentData.achievements} 
                />
              </ProfileCard>
            </div>
          </div>
        </div>
      </div>

      {/* Render the new modal */}
      {isEditPicModalOpen && (
        <EditProfilePicModal
          currentAvatar={studentData.personalInfo.avatarUrl}
          onClose={() => setIsEditPicModalOpen(false)}
          onSave={handlePictureSave}
        />
      )}
    </>
  );
}

export default StudentProfile;