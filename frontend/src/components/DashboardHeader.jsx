import React, { useState } from 'react';
import { Bell, Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const DashboardHeader = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([
    { id: 1, title: 'New assignment posted', time: '5m ago', unread: true },
    { id: 2, title: 'Grade received for Math Quiz', time: '1h ago', unread: true },
    { id: 3, title: 'New course material available', time: '3h ago', unread: false }
  ]);
  const [showNotifications, setShowNotifications] = useState(false);

  const unreadCount = notifications.filter(n => n.unread).length;

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, unread: false })));
  };

  return (
    <header className="bg-white border-b border-slate-200 px-4 sm:px-6 lg:px-8 h-16 sticky top-0 z-40">
      <div className="flex items-center justify-between h-full">
        
        {/* Left: Search Bar */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input
              type="text"
              placeholder="Search courses, assignments, resources..."
              className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent"
            />
          </div>
        </div>

        {/* Right: XP Display + Notifications */}
        <div className="flex items-center gap-4 ml-4">
          
          {/* XP Display - Only for Students */}
          {user?.role === 'STUDENT' && (
            <div className="hidden sm:flex items-center gap-2 bg-slate-900 text-white px-4 py-2 rounded-lg">
              <span className="text-sm font-semibold">{user.xp_points || 0} XP</span>
              <span className="text-slate-400">·</span>
              <span className="text-xs text-slate-300">Lvl {user.level || 1}</span>
            </div>
          )}

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            >
              <Bell className="w-5 h-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 flex items-center justify-center h-4 w-4 bg-red-500 text-white text-xs font-bold rounded-full">
                  {unreadCount}
                </span>
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <>
                <div 
                  className="fixed inset-0 z-40" 
                  onClick={() => setShowNotifications(false)}
                />
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-slate-200 z-50">
                  <div className="p-4 border-b border-slate-200 flex items-center justify-between">
                    <h3 className="font-semibold text-slate-900">Notifications</h3>
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllAsRead}
                        className="text-xs text-slate-600 hover:text-slate-900"
                      >
                        Mark all as read
                      </button>
                    )}
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <div className="p-8 text-center text-slate-500 text-sm">
                        No notifications yet
                      </div>
                    ) : (
                      notifications.map((notif) => (
                        <div
                          key={notif.id}
                          className={`p-4 border-b border-slate-100 hover:bg-slate-50 cursor-pointer ${
                            notif.unread ? 'bg-slate-50' : ''
                          }`}
                        >
                          <div className="flex items-start gap-3">
                            {notif.unread && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                            )}
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-slate-900">
                                {notif.title}
                              </p>
                              <p className="text-xs text-slate-500 mt-1">
                                {notif.time}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                  <div className="p-3 border-t border-slate-200">
                    <button className="w-full text-center text-sm text-slate-600 hover:text-slate-900 font-medium">
                      View all notifications
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader