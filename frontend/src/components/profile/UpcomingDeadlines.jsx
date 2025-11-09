import React from 'react';
import { format, formatDistanceToNow } from 'date-fns';
import { Calendar } from 'lucide-react';

function UpcomingDeadlines({ deadlines }) {
  if (!deadlines || deadlines.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No upcoming deadlines. You're all caught up!</p>;
  }

  const now = new Date();

  return (
    <ul className="space-y-4">
      {deadlines.map((item) => {
        const dueDate = new Date(item.dueDate);
        const isPast = dueDate < now;
        const relativeDate = formatDistanceToNow(dueDate, { addSuffix: true });
        
        return (
          <li key={item.id} className="flex items-center gap-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-md">
            <div className="flex-shrink-0 flex flex-col items-center justify-center w-12 h-12 bg-red-100 dark:bg-red-900 rounded-md">
              <span className="text-xs font-bold text-red-700 dark:text-red-300">
                {format(dueDate, 'MMM')}
              </span>
              <span className="text-lg font-bold text-red-700 dark:text-red-300">
                {format(dueDate, 'dd')}
              </span>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 dark:text-white">{item.title}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-400">{item.skillSpace}</p>
            </div>
            <div className="text-right">
              <span className={`text-xs font-medium ${isPast ? 'text-red-500' : 'text-gray-600 dark:text-gray-300'}`}>
                {isPast ? `Due ${relativeDate}` : `Due in ${relativeDate.replace('in ', '')}`}
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export default UpcomingDeadlines;