import React from 'react';
import Card from '../../shared/Card';
import UserAvatar from '../../shared/UserAvatar';
import Button from '../../shared/Button';
import { useStudentRewards } from '../../../hooks/useStudentRewards';
import { Link } from 'react-router-dom'; // <-- 1. NEW IMPORT

// 1. Create a dummy user object right here.
const DUMMY_USER = {
  id: 'student-123',
  username: 'test_student',
  avatar_url: null, // or a path to a static image in /public if you have one
};

const StudentProfileCard = () => {
  // 2. Use the dummy user object directly.
  const user = DUMMY_USER;
  
  // Use the hook to get dummy rewards data
  const { xp } = useStudentRewards(); // No userId needed

  return (
    <Card className="p-0"> {/* Remove padding to let image be flush */}
      
      {/* Big profile picture at the top, centered */}
      <div className="flex justify-center -mt-12 mb-4">
        <UserAvatar 
          user={user} 
          /* Updated border/ring colors for dark theme */
          className="w-24 h-24 text-4xl border-4 border-[#0F1A1C] rounded-full ring-2 ring-[#223237]" 
        />
      </div>

      <div className="p-4">
        {/* 3. Use dark theme text color */}
        <h2 className="text-xl font-bold text-center text-[#D7DADC]">{user.username}</h2>
        
        {/* Karma/XP section */}
        <div className="flex flex-col items-center my-4">
          {/* Use a lighter color for the XP */}
          <span className="font-bold text-3xl text-emerald-400">{xp.toLocaleString()}</span>
          {/* Use dark theme text color */}
          <span className="text-[#82959B] font-medium">Karma (XP)</span>
        </div>
        
        {/* --- MODIFICATION START --- */}
        {/* Wrapper for buttons to stack them */}
        <div className="flex flex-col space-y-2">
        
          {/* 2. WRAP THE BUTTON WITH A LINK */}
          <Link to="/student/profile">
            <Button variant="outline" className="w-full">
              View Full Profile
            </Button>
          </Link>

          {/* NEW XP SHOP BUTTON */}
          <Link to="/student/xp-shop">
            <Button variant="primary" className="w-full"> {/* You can change variant="primary" to "outline" if you prefer */}
              XP Shop
            </Button>
          </Link>
        
        </div>
        {/* --- MODIFICATION END --- */}
        
      </div>
    </Card>
  );
};

export default StudentProfileCard;