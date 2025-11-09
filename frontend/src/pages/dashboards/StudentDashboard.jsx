import React, { useState } from 'react';
import {
  Flame, Sparkles, TrendingUp, Clock, Award
} from 'lucide-react';

// Import your components
import SiteNavbar from '../../components/layout/SiteNavbar';
import Feed from '../../components/classroom/Feed';

// --- THIS IS THE FIX ---
// We now import our new, dedicated dashboard sidebar
import StudentDashboardSidebar from '../../components/dashboard/StudentDashboard/StudentDashboardSidebar';
// ----------------------

// Our custom hooks and sidebar widgets
import { useStudentDashboardFeed } from '../../hooks/useStudentDashboardFeed';
// We no longer need to import the widgets here, the new sidebar does it.

// Create the same dummy user here
const DUMMY_USER = {
  id: 'student-123',
  username: 'test_student',
  avatar_url: null,
};

// Define the sortOptions array
const sortOptions = [
  { name: 'Best', icon: Award },
  { name: 'Hot', icon: Flame },
  { name: 'New', icon: Sparkles },
  { name: 'Top', icon: TrendingUp },
  { name: 'Rising', icon: Clock }
];


const StudentDashboard = () => {
  // Use the dummy user object
  const user = DUMMY_USER;
  
  // Fetch the personalized feed data
  const { posts, isLoading } = useStudentDashboardFeed();

  // Add state for sorting
  const [sortBy, setSortBy] = useState('Best');
  const [isSortOpen, setIsSortOpen] = useState(false);

  // Add a placeholder vote handler
  const handleVote = (postId, direction) => {
    console.log(`Vote registered on dashboard: Post ${postId}, Direction ${direction}`);
  };

  // Create the sortedPosts variable
  const sortedPosts = [...(posts || [])].sort((a, b) => {
    switch (sortBy) {
      case 'New':
        return b.id - a.id; 
      case 'Rising':
        return (b.comments || 0) - (a.comments || 0);
      case 'Best':
      case 'Hot':
      case 'Top':
      default:
        return (b.votes || 0) - (a.votes || 0);
    }
  });
  
  // --- THIS IS THE FIX ---
  // The sidebarWidgets array is no longer needed.
  // ----------------------

  return (
    // Removed bg-gray-50 to match the dark theme
    <div className="min-h-screen">
      <SiteNavbar />
      
      {/* --- THIS IS THE LAYOUT FIX ---
        We add 'pt-20' here. The navbar is 'h-14' (56px). 
        pt-20 (80px) gives us space below the navbar.
      */}
      <div className="max-w-7xl mx-auto p-4 pt-25 grid grid-cols-1 md:grid-cols-3 gap-2 md:ml-5">
        
        {/* === MAIN FEED (LEFT) === */}
        <div className="md:col-span-2">
          <Feed
            sortedPosts={sortedPosts}
            handleVote={handleVote}
            sortBy={sortBy}
            setSortBy={setSortBy}
            isSortOpen={isSortOpen}
            setIsSortOpen={setIsSortOpen}
            sortOptions={sortOptions}
          />
        </div>

        {/* === SIDEBAR (RIGHT) === */}
        <div className="md:col-span-1">
          {/* --- THIS IS THE COMPONENT FIX ---
            We render our new sidebar and pass it the 'user' prop
            so it can give it to the StudentProfileCard.
          */}
          <StudentDashboardSidebar user={user} />
        </div>

      </div>
    </div>
  );
};

export default StudentDashboard;