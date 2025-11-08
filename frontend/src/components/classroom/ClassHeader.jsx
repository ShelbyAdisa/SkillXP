import React from 'react';

export default function ClassHeader({ joined, setJoined }) {
  // In the future, you'll pass down classroomName, icon, etc. as props
  // and fetch them based on the URL's :classId
  return (
    <div className="bg-[#0F1A1C] border-b border-[#223237]">
      <div className="max-w-[1400px] mx-auto px-4">
        <div className="flex items-end -mt-3 pb-4">
          <div className="w-20 h-20 bg-[#0079d3] border-4 border-[#0F1A1C] rounded-full flex items-center justify-center text-4xl shrink-0">
            📚
          </div>
          <div className="ml-4 flex-1 min-w-0">
            <h1 className="text-[#D7DADC] text-2xl font-bold">LearnProgramming</h1>
            <p className="text-[#82959B] text-sm">Class: LearnProgramming</p>
          </div>
          <button 
            onClick={() => setJoined(!joined)}
            className={`px-6 py-1.5 rounded-full font-bold text-sm shrink-0 ${
              joined 
                ? 'bg-[#223237] text-[#D7DADC] hover:bg-[#2d3f45] border border-[#2d3f45]'
                : 'bg-[#D7DADC] text-[#0F1A1C] hover:bg-white'
            }`}
          >
            {joined ? 'Joined' : 'Join'}
          </button>
        </div>
      </div>
    </div>
  );
}