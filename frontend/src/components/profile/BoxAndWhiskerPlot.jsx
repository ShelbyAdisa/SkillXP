import React from 'react';

// This component assumes all values (stats and studentScore) are percentages (0-100)
function BoxAndWhiskerPlot({ stats, studentScore }) {
  const { min, q1, median, q3, max } = stats;

  // Function to calculate left percentage
  const percent = (val) => `${Math.max(0, Math.min(100, val))}%`;

  return (
    <div className="w-full py-8 px-2">
      <div className="relative h-12">
        
        {/* Plot Area */}
        <div className="absolute top-4 left-0 w-full h-8">
          {/* Main Line (Whisker to Whisker) */}
          <div 
            className="absolute top-1/2 -translate-y-1/2 h-0.5 bg-gray-400 dark:bg-gray-500"
            style={{ left: percent(min), width: percent(max - min) }}
          ></div>

          {/* Box (Q1 to Q3) */}
          <div 
            className="absolute top-0 h-8 bg-indigo-200 dark:bg-indigo-900 border-y border-indigo-500"
            style={{ left: percent(q1), width: percent(q3 - q1) }}
          ></div>

          {/* Median Line */}
          <div 
            className="absolute top-0 h-8 w-0.5 bg-indigo-700 dark:bg-indigo-300" 
            style={{ left: percent(median) }}
          ></div>
        </div>
        
        {/* Student Score Dot */}
        <div 
          className="absolute z-20 top-0 flex flex-col items-center" 
          style={{ left: percent(studentScore), transform: 'translateX(-50%)' }}
        >
          <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
            YOU ({studentScore}%)
          </span>
          <div className="h-3 w-3 mt-1 rounded-full bg-indigo-600 dark:bg-indigo-400 ring-2 ring-white dark:ring-gray-800"></div>
        </div>

        {/* Axis Labels */}
        <div className="absolute top-12 left-0 w-full h-8">
          {[min, q1, median, q3, max].map((val, idx) => (
            <div 
              key={idx}
              className="absolute top-0 flex flex-col items-center"
              style={{ left: percent(val), transform: 'translateX(-50%)' }}
            >
              <div className="h-2 w-0.5 bg-gray-400 dark:bg-gray-500"></div>
              <span className="mt-1 text-xs text-gray-500 dark:text-gray-400">{val}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default BoxAndWhiskerPlot;