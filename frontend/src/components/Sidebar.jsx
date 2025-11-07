import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, BookOpen, Users, Heart, UserPlus, 
  Scale, MessageSquare, Megaphone, Mail, BarChart3, 
  GraduationCap, Bus, Gift, LogOut, Menu, X, CheckSquare, BarChart, BookOpenText, UsersRound, Zap, BarChart2 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const navigationItems = {
  STUDENT: [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { name: 'Courses', icon: Users, path: '/classroom' },
    { name: 'Library', icon: BookOpen, path: '/elibrary' },
    { name: 'Assignments', icon: CheckSquare, path: '/assignments' },
    { name: 'Rewards', icon: Gift, path: '/rewards' },
    { name: 'Forum', icon: MessageSquare, path: '/forums' },
    { name: 'Wellbeing', icon: Heart, path: '/wellbeing' },
  ],
  TEACHER: [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/teacher/dashboard' },
    { name: 'Classes', icon: Users, path: '/classroom' },
    { name: 'Assignments', icon: CheckSquare, path: '/assignments' },
  
  ],
  PARENT: [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/parent/dashboard' },
    // Removed: { name: 'Children', icon: UsersRound, path: '/parent/children' },
    // Removed: { name: 'Progress', icon: BarChart2, path: '/parent/progress' },
    { name: 'School Governance', icon: Scale, path: '/school-governance' },
    { name: 'Transport', icon: Bus, path: '/transportation' },
    { name: 'Alerts', icon: Megaphone, path: '/parent/notifications' },
  ],
  ADMIN: [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/admin/dashboard' },
    { name: 'Analytics', icon: BarChart3, path: '/analytics' },
    { name: 'Users', icon: Users, path: '/admin/users' },
    { name: 'Schools', icon: GraduationCap, path: '/admin/schools' },
    { name: 'Content', icon: UserPlus, path: '/admin/content' },
    { name: 'Rewards', icon: Gift, path: '/admin/rewards' },
    { name: 'Reports', icon: Scale, path: '/transparency' },
  ],
  SCHOOL_ADMIN: [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/school-admin/dashboard' },
    { name: 'School Governance', icon: Scale, path: '/school-governance' },
    { name: 'Analytics', icon: BarChart3, path: '/analytics' },
    { name: 'Users', icon: Users, path: '/school-admin/users' },
    { name: 'Classes', icon: GraduationCap, path: '/classroom' },
    { name: 'Transport', icon: Bus, path: '/transportation' },
    { name: 'Library', icon: BookOpen, path: '/elibrary' },
    { name: 'Settings', icon: Scale, path: '/school-admin/settings' },
  ],
};

const Sidebar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);

  const navItems = user ? navigationItems[user.role] || [] : [];

  const isActive = (path) => location.pathname === path;

  const handleLinkClick = () => setIsOpen(false);

  return (
    <>
      {/* Mobile Header */}
      <div className="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-slate-200 z-50 px-4 py-3 flex items-center justify-between">
        <Link to="/dashboard" className="flex items-center gap-2">
          <div className="bg-slate-900 p-2 rounded-lg">
            <GraduationCap className="w-5 h-5 text-white" />
          </div>
          <span className="text-lg font-bold text-slate-900">SkillXP Nexus</span>
        </Link>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 rounded-lg hover:bg-slate-100 transition-colors"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Backdrop */}
      {isOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black/50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:sticky top-0 left-0 w-64 bg-white border-r border-slate-200 h-screen z-40 flex flex-col transition-transform duration-300 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-slate-200">
          <Link to="/dashboard" className="flex items-center gap-2">
            <div className="bg-slate-900 p-2 rounded-lg">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <span className="text-lg font-bold text-slate-900">SkillXP Nexus</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.path);
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    onClick={handleLinkClick}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      active ? 'bg-slate-900 text-white' : 'text-slate-700 hover:bg-slate-100'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{item.name}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-slate-200 relative">
          <button
            onClick={() => setProfileMenuOpen(!profileMenuOpen)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <div className="w-10 h-10 rounded-full bg-slate-900 flex items-center justify-center">
              <span className="text-white font-semibold">
                {user?.first_name?.[0] || user?.email?.[0]?.toUpperCase() || 'U'}
                {user?.last_name?.[0] || 'N'}
              </span>
            </div>
            <div className="flex-1 min-w-0 text-left">
              <p className="font-medium text-slate-900 truncate">
                {user?.first_name} {user?.last_name || 'User'}
              </p>
              <p className="text-xs text-slate-600 truncate">{user?.role || 'Guest'}</p>
            </div>
          </button>

          {/* Dropdown menu */}
          {profileMenuOpen && (
            <div className="absolute left-0 bottom-full mb-2 w-full bg-gray-100 rounded-lg shadow-xl shadow-gray-400/30 border border-gray-200 z-50">
              <button
                onClick={() => {
                  navigate('/dashboard'); 
                  setProfileMenuOpen(false);
                }}
                className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                Profile Settings
              </button>
              <button
                onClick={() => {
                  logout();
                  setProfileMenuOpen(false);
                  navigate('/login');
                }}
                className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </aside>
    </>
  );
};

export default Sidebar;