import React from 'react';
import { Award } from 'lucide-react'; // Default icon

function AchievementsList({ achievements }) {
  if (!achievements || achievements.length === 0) {
    return <p className="text-gray-500 dark:text-gray-400">No achievements earned yet. Keep learning!</p>;
  }

  return (
    <ul className="space-y-4">
      {achievements.map((badge) => {
        const Icon = badge.icon || Award;
        return (
          <li 
            key={badge.id} 
            className="flex items-start gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg"
          >
            <div className="flex-shrink-0">
              <span className="flex items-center justify-center h-10 w-10 rounded-full bg-emerald-100 dark:bg-emerald-900">
                <Icon className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
              </span>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-gray-900 dark:text-white">{badge.name}</h4>
              <p className="text-sm text-gray-600 dark:text-gray-300">{badge.description}</p>
            </div>
            <div className="flex-shrink-0">
              <span className="font-bold text-emerald-600 dark:text-emerald-400">
                +{badge.xp} XP
              </span>
            </div>
          </li>
        );
      })}
    </ul>
  );
}

export default AchievementsList;