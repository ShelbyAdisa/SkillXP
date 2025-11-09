import React from 'react';
import { Award, CheckCircle, MessageSquare, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

// Dummy data for notifications
const notifications = [
  {
    id: 1,
    icon: Award,
    color: 'text-yellow-400',
    text: 'You earned a new badge: "Python Pro"',
    time: '2 hours ago',
  },
  {
    id: 2,
    icon: CheckCircle,
    color: 'text-green-400',
    text: 'Your "Web App" project was graded: 95%',
    time: '4 hours ago',
  },
  {
    id: 3,
    icon: MessageSquare,
    color: 'text-blue-400',
    text: 'New message from Jane Doe',
    time: '1 day ago',
  },
  {
    id: 4,
    icon: Clock,
    color: 'text-red-400',
    text: 'Deadline: "History Essay" is due tomorrow',
    time: '1 day ago',
  },
  {
    id: 5,
    icon: CheckCircle,
    color: 'text-green-400',
    text: 'Assignment "Calculus II" submitted',
    time: '2 days ago',
  },
];

export default function NotificationDropdown({ isOpen }) {
  if (!isOpen) {
    return null;
  }

  return (
    <div className="absolute right-0 mt-2 w-72 md:w-80 bg-[#0F1A1C] border border-[#223237] rounded-md shadow-lg z-20">
      <div className="p-3 flex justify-between items-center border-b border-[#223237]">
        <h3 className="text-sm font-semibold text-[#D7DADC]">Notifications</h3>
        <Link to="/notifications" className="text-xs text-blue-400 hover:underline">
          View All
        </Link>
      </div>
      
      {/* Scrollable list */}
      <div className="max-h-80 overflow-y-auto">
        {notifications.map((notif, index) => (
          <div 
            key={notif.id}
            // --- FIX: Changed border color and removed border from last item ---
            className={`flex items-start gap-3 p-3 hover:bg-[#131F23] ${
              index < notifications.length - 1 ? 'border-b border-[#223237]' : ''
            }`}
          >
            <notif.icon className={`w-5 h-5 mt-0.5 ${notif.color}`} />
            <div className="flex-1">
              <p className="text-sm text-[#D7DADC]">{notif.text}</p>
              <p className="text-xs text-[#82959B]">{notif.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}