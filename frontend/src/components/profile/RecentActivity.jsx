import React from 'react';
import { FileText, Award, MessageSquare, Check } from 'lucide-react';

const iconMap = {
  submission: FileText,
  badge: Award,
  comment: MessageSquare,
  completion: Check,
};

function RecentActivity({ activity }) {
  if (!activity || activity.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No recent activity.</p>;
  }

  return (
    <ul className="space-y-4">
      {activity.map((item) => {
        const Icon = iconMap[item.type] || Check;
        return (
          <li key={item.id} className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <span className="flex items-center justify-center h-8 w-8 rounded-full bg-indigo-100 dark:bg-indigo-900">
                <Icon className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
              </span>
            </div>
            <div className="flex-1">
              <p className="text-sm text-gray-800 dark:text-gray-200">{item.description}</p>
              <span className="text-xs text-gray-500 dark:text-gray-400">{item.date}</span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export default RecentActivity;