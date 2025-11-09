import React from 'react';
import { X } from 'lucide-react';
import BoxAndWhiskerPlot from './BoxAndWhiskerPlot';

function GradeDetailModal({ skillSpace, onClose }) {
  const totalScore = skillSpace.grades.reduce((acc, grade) => acc + grade.score, 0);
  const totalMax = skillSpace.grades.reduce((acc, grade) => acc + grade.max, 0);
  const studentOverall = totalMax > 0 ? (totalScore / totalMax) * 100 : 0;

  return (
    // Backdrop (dimmed and blurred)
    <div 
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50 p-4 backdrop-blur-sm"
    >
      {/* Modal Content */}
      <div
        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking inside
        className="relative w-full max-w-2xl bg-white dark:bg-gray-800 rounded-lg shadow-xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            {skillSpace.name} - Grade Details
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
          {/* Section 1: Detailed Scores */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-3">Assessments</h4>
            <ul className="divide-y dark:divide-gray-700 border rounded-md dark:border-gray-700">
              {skillSpace.grades.map((grade) => (
                <li key={grade.id} className="flex justify-between items-center p-3">
                  <span className="text-gray-700 dark:text-gray-300">{grade.title}</span>
                  <span className="font-semibold text-gray-900 dark:text-white">
                    {grade.score} / {grade.max}
                  </span>
                </li>
              ))}
              <li className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700/50">
                <span className="font-bold text-gray-900 dark:text-white">Overall</span>
                <span className="font-bold text-lg text-indigo-600 dark:text-indigo-400">
                  {studentOverall.toFixed(1)}% ({skillSpace.overallGrade})
                </span>
              </li>
            </ul>
          </div>

          {/* Section 2: Class Comparison Plot */}
          <div>
            <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Class Comparison</h4>
            <BoxAndWhiskerPlot 
              stats={skillSpace.classStats} 
              studentScore={skillSpace.studentOverall}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default GradeDetailModal;