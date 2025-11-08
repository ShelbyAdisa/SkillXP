import React from 'react';
import Card from '../../shared/Card';
import UserAvatar from '../../shared/UserAvatar';
import Button from '../../shared/Button';
import { useStudentRewards } from '../../../hooks/useStudentRewards';

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
          className="w-24 h-24 text-4xl border-4 border-white rounded-full ring-2 ring-gray-200" 
        />
      </div>

      <div className="p-4">
        {/* 3. Use the dummy user's username */}
        <h2 className="text-xl font-bold text-center text-gray-900">{user.username}</h2>
        
        {/* Karma/XP section */}
        <div className="flex flex-col items-center my-4">
          <span className="font-bold text-3xl text-primary">{xp.toLocaleString()}</span>
          <span className="text-gray-500 font-medium">Karma (XP)</span>
        </div>
        
        <Button variant="outline" className="w-full">
          View Full Profile
        </Button>
      </div>
    </Card>
  );
};

export default StudentProfileCard;