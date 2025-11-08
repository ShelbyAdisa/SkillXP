import React from 'react';

// Sub-component: AboutWidget
const AboutWidget = () => (
  <div className="bg-[#0F1A1C] border border-[#223237] rounded-xl overflow-hidden">
    <div className="h-10 bg-gradient-to-r from-[#0079d3] to-[#00a8cc]"></div>
    <div className="p-4">
      <h3 className="text-[#D7DADC] text-sm font-semibold mb-3">About Class</h3>
      <p className="text-[#B8C5C9] text-sm leading-relaxed mb-4">
        A place for students and instructors to discuss coursework, share resources, and collaborate on class projects.
      </p>
      <div className="flex gap-4 mb-4">
        <div>
          <div className="text-[#D7DADC] text-base font-semibold">124</div>
          <div className="text-[#82959B] text-xs">Members</div>
        </div>
        <div>
          <div className="text-[#D7DADC] text-base font-semibold">2</div>
          <div className="text-[#82959B] text-xs">Online</div>
        </div>
      </div>
      <div className="border-t border-[#223237] pt-3 mb-4">
        <div className="text-[#82959B] text-xs">Created Jan 15, 2024</div>
      </div>
      <button className="w-full bg-[#D7DADC] hover:bg-white text-[#0F1A1C] font-bold text-sm py-2 rounded-full transition-colors">
        Create Post
      </button>
    </div>
  </div>
);

// Sub-component: RulesWidget
const RulesWidget = () => (
  <div className="bg-[#0F1A1C] border border-[#223237] rounded-xl p-4 text-sm">
    <h3 className="text-[#D7DADC] text-sm font-semibold mb-3">Classroom Rules</h3>
    <div className="space-y-3">
      {[
        'Be respectful and civil to peers and instructors.',
        'No plagiarism or cheating — cite sources and submit original work.',
        'Keep posts related to course topics and assignments.',
        'No spam, advertising, or off-topic self-promotion.',
        'Use appropriate tags (Question, Assignment, Resource) and include context.'
      ].map((rule, idx) => (
        <div key={idx} className="text-[#B8C5C9] pb-3 border-b border-[#223237] last:border-0">
          <span className="text-[#D7DADC] font-medium">{idx + 1}.</span> {rule}
        </div>
      ))}
    </div>
  </div>
);

// Sub-component: ModeratorsWidget
const ModeratorsWidget = () => (
  <div className="bg-[#0F1A1C] border border-[#223237] rounded-xl p-4">
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-[#D7DADC] text-sm font-semibold">Instructors</h3>
      <button className="text-[#0079d3] hover:underline text-xs font-bold">View all</button>
    </div>
    <div className="space-y-3">
      {['ProfessorSmith', 'TeachingAssistant', 'CourseAdmin'].map((mod, idx) => (
        <div key={idx} className="flex items-center gap-2">
          <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${mod}`} className="w-8 h-8 rounded-full" alt={`${mod} avatar`} />
          <span className="text-[#B8C5C9] text-sm hover:underline cursor-pointer">{mod}</span>
        </div>
      ))}
    </div>
    <button className="w-full mt-4 border border-[#223237] hover:bg-[#131F23] text-[#D7DADC] font-bold text-sm py-2 rounded-full transition-colors">
      Message the instructors
    </button>
  </div>
);


// Main Sidebar Component
export default function Sidebar() {
  return (
    <div className="hidden lg:block w-80 shrink-0 space-y-4">
      <AboutWidget />
      <RulesWidget />
      <ModeratorsWidget />
    </div>
  );
}