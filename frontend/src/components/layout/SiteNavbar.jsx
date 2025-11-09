import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Search, Bell, MessageCircle, ChevronDown, TrendingUp, Plus, Menu
} from 'lucide-react';
import BrandLogo from '../shared/BrandLogo';
import UserAvatar from '../shared/UserAvatar';

import NotificationDropdown from '../chat/NotificationDropdown';
import { useChat } from '../../context/ChatContext';

export default function SiteNavbar() {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);
  const { toggleChat } = useChat();

  const handleLogout = () => {
    console.log('User logged out');
    setIsProfileOpen(false);
  };
  
  const toggleProfile = () => {
    setIsProfileOpen(prev => !prev);
    setIsAlertsOpen(false);
  }
  
  const toggleAlerts = () => {
    setIsAlertsOpen(prev => !prev);
    setIsProfileOpen(false);
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0F1A1C] border-b border-[#223237] h-14">
      <div className="h-full px-4 flex items-center justify-between max-w-[1400px] mx-auto">
        {/* Left Side */}
        <div className="flex items-center gap-4">
          <button className="lg:hidden p-2 hover:bg-[#131F23] rounded-lg">
            <Menu className="w-5 h-5 text-[#D7DADC]" />
          </button>
          
          <Link to="/studentdashboard" className="flex items-center gap-2">
            <BrandLogo className="w-8 h-8" />
            <span className="hidden sm:block text-[#D7DADC] text-xl font-semibold">SkillXP</span>
          </Link>

          <div className="hidden md:flex items-center bg-[#131F23] border border-[#223237] rounded-full px-4 py-2 w-80 lg:w-96">
            <Search className="w-4 h-4 text-[#82959B]" />
            <input 
              type="text"
              placeholder="Search SkillXP"
              className="ml-2 bg-transparent text-sm text-[#D7DADC] placeholder-[#82959B] outline-none w-full"
            />
          </div>
        </div>
        
        {/* Right Side */}
        <div className="flex items-center gap-2">
          
          <a
            href="https://www.khanacademy.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden lg:flex items-center gap-2 px-4 py-1.5 bg-[#131F23] hover:bg-[#223237] rounded-full"
          >
            <TrendingUp className="w-4 h-4 text-[#B8C5C9]" />
            <span className="text-sm font-medium text-[#D7DADC]">Popular</span>
          </a>
          
          {/* --- FIX: Added cursor-pointer --- */}
          <button 
            onClick={toggleChat} 
            className="p-2 hover:bg-[#131F23] rounded-lg cursor-pointer"
          >
            <MessageCircle className="w-5 h-5 text-[#82959B]" />
          </button>
          
          <div className="relative">
            {/* --- FIX: Added cursor-pointer --- */}
            <button 
              onClick={toggleAlerts} 
              className="p-2 hover:bg-[#131F23] rounded-lg cursor-pointer"
            >
              <Bell className="w-5 h-5 text-[#82959B]" />
            </button>
            <NotificationDropdown isOpen={isAlertsOpen} />
          </div>
          
          <button className="p-2 hover:bg-[#131F23] rounded-lg">
            <Plus className="w-5 h-5 text-[#82959B]" />
          </button>
          
          <div className="relative">
            {/* --- FIX: Added cursor-pointer --- */}
            <button
              onClick={toggleProfile}
              className="flex items-center gap-2 p-1.5 hover:bg-[#131F23] rounded-lg cursor-pointer"
            >
              <UserAvatar className="w-8 h-8 rounded-full" />
              <ChevronDown className="w-4 h-4 text-[#82959B] hidden lg:block" />
            </button>

            {isProfileOpen && (
              <div 
                className="absolute right-0 mt-2 w-48 bg-[#0F1A1C] border border-[#223237] rounded-md shadow-lg py-1 z-20"
                onClick={() => setIsProfileOpen(false)}
              >
                <Link
                  to="/profile"
                  className="block px-4 py-2 text-sm text-[#D7DADC] hover:bg-[#223237] cursor-pointer"
                >
                  View Profile
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full text-left block px-4 py-2 text-sm text-[#D7DADC] hover:bg-[#223237] cursor-pointer"
                >
                  Log Out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}