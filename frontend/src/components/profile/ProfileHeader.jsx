import React from 'react';
import { Mail, Briefcase, Star } from 'lucide-react';

function ProfileHeader({ studentInfo, onEditClick }) {
  const { name, email, avatarUrl, studentId, school, xp } = studentInfo;

  return (
    <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
      <div className="h-32 bg-indigo-600 dark:bg-indigo-800"></div>
      <div className="p-6 -mt-16 flex flex-col sm:flex-row items-center sm:items-end sm:justify-between">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <img
            src={avatarUrl}
            alt={`${name}'s profile`}
            className="h-32 w-32 rounded-full border-4 border-white dark:border-gray-800 object-cover bg-gray-200"
          />
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mt-4 sm:mt-0">{name}</h1>
            <p className="text-sm text-gray-600 dark:text-gray-400">{studentId}</p>
          </div>
        </div>
        {/* Button is now active and calls the onEditClick prop */}
        <button 
          onClick={onEditClick}
          className="mt-4 sm:mt-0 px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 dark:bg-indigo-700 dark:hover:bg-indigo-600"
        >
          Edit Picture
        </button>
      </div>
      
      <div className="p-6 border-t dark:border-gray-700 grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
          <Mail className="h-5 w-5 text-gray-400" />
          <span>{email}</span>
        </div>
        <div className="flex items-center gap-2 text-gray-700 dark:text-gray-300">
          <Briefcase className="h-5 w-5 text-gray-400" />
          <span>{school}</span>
        </div>
        {/* Total XP display, no levels */}
        <div className="flex items-center justify-start md:justify-end gap-2 text-gray-700 dark:text-gray-300">
          <Star className="h-5 w-5 text-yellow-500" />
          <span className="text-lg font-bold">{xp.toLocaleString()}</span>
          <span className="text-sm">Total XP</span>
        </div>
      </div>
    </div>
  );
}

export default ProfileHeader;