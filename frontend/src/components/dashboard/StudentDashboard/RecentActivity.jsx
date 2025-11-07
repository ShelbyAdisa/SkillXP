import React from "react";
import { Trophy } from "lucide-react";
import Card from "../../shared/Card";

const RecentActivity = ({ activities = [] }) => {
  const getActivityIcon = (type) => {
    const icons = {
      assignment_submitted: "✅",
      grade_received: "📝",
      course_enrolled: "📚",
      achievement_unlocked: "🏆",
      resource_accessed: "📖",
      post_created: "💬",
    };
    return icons[type] || "📌";
  };

  const formatTimeAgo = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <Card title="Recent Activity" subtitle="Your latest learning activities">
      <div className="space-y-3">
        {activities.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <p>No recent activity</p>
            <p className="text-sm mt-1">Start learning to see your progress!</p>
          </div>
        ) : (
          activities.slice(0, 8).map((activity, index) => (
            <div
              key={index}
              className="flex items-start justify-between space-x-3 p-2 hover:bg-slate-50 rounded-lg"
            >
              <div className="flex items-start gap-2 min-w-0">
                <span className="text-lg">{getActivityIcon(activity.type)}</span>
                <div>
                  <p className="text-sm text-gray-900">{activity.description}</p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    {formatTimeAgo(activity.created_at)}
                  </p>
                </div>
              </div>

              {activity.xp_earned && (
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-yellow-500/20 rounded-md border border-yellow-500/30 whitespace-nowrap">
                  <Trophy className="w-3.5 h-3.5 text-yellow-600 shrink-0" />
                  <span className="text-xs font-semibold text-yellow-700">
                    +{activity.xp_earned} XP
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </Card>
  );
};

export default RecentActivity;
