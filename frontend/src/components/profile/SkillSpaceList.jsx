import React, { useState } from 'react';
import GradeDetailModal from './GradeDetailModal'; // Import the new modal

function SkillSpaceList({ skillSpaces }) {
  const [selectedSkillSpace, setSelectedSkillSpace] = useState(null);

  if (!skillSpaces || skillSpaces.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No SkillSpaces enrolled yet.</p>;
  }

  const handleOpenModal = (space) => {
    setSelectedSkillSpace(space);
  };

  const handleCloseModal = () => {
    setSelectedSkillSpace(null);
  };

  return (
    <>
      <ul className="space-y-4">
        {skillSpaces.map((space) => (
          <li 
            key={space.id} 
            className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
          >
            <div className="flex items-center gap-3">
              <span className="flex items-center justify-center h-10 w-10 rounded-full bg-indigo-100 dark:bg-indigo-900">
                {React.createElement(space.icon, { className: "h-5 w-5 text-indigo-600 dark:text-indigo-400" })}
              </span>
              <div>
                <span className="font-medium text-gray-900 dark:text-white">{space.name}</span>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Overall Grade: <span className="font-semibold">{space.overallGrade}</span>
                </p>
              </div>
            </div>
            
            {/* The new "View Grades" button */}
            <button
              onClick={() => handleOpenModal(space)}
              className="px-3 py-1.5 text-sm font-medium text-indigo-700 bg-indigo-100 rounded-md hover:bg-indigo-200 dark:bg-indigo-900 dark:text-indigo-300 dark:hover:bg-indigo-800"
            >
              View Grades
            </button>
          </li>
        ))}
      </ul>

      {/* Render the modal if a skillspace is selected */}
      {selectedSkillSpace && (
        <GradeDetailModal
          skillSpace={selectedSkillSpace}
          onClose={handleCloseModal}
        />
      )}
    </>
  );
}

export default SkillSpaceList;