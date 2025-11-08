import React from 'react';
import {
  Search, Bell, MessageCircle, ChevronDown, TrendingUp, Plus, Menu
} from 'lucide-react';
import BrandLogo from '../shared/BrandLogo';
import UserAvatar from '../shared/UserAvatar';

export default function SiteNavbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0F1A1C] border-b border-[#223237] h-14">
      <div className="h-full px-4 flex items-center justify-between max-w-[1400px] mx-auto">
        <div className="flex items-center gap-4">
          <button className="lg:hidden p-2 hover:bg-[#131F23] rounded-lg">
            <Menu className="w-5 h-5 text-[#D7DADC]" />
          </button>
          <div className="flex items-center gap-2">
            <BrandLogo className="w-8 h-8" />
            <span className="hidden sm:block text-[#D7DADC] text-xl font-semibold">SkillXP</span>
          </div>
            <div className="hidden md:flex items-center bg-[#131F23] border border-[#223237] rounded-full px-4 py-2 w-80 lg:w-96">
            <Search className="w-4 h-4 text-[#82959B]" />
            <input 
              type="text"
              placeholder="Search SkillXP"
              className="ml-2 bg-transparent text-sm text-[#D7DADC] placeholder-[#82959B] outline-none w-full"
            />
          </div>
        </div>
          <div className="flex items-center gap-2">
          <button className="hidden lg:flex items-center gap-2 px-4 py-1.5 bg-[#131F23] hover:bg-[#223237] rounded-full">
            <TrendingUp className="w-4 h-4 text-[#B8C5C9]" />
            <span className="text-sm font-medium text-[#D7DADC]">Popular</span>
          </button>
          <button className="p-2 hover:bg-[#131F23] rounded-lg">
            <MessageCircle className="w-5 h-5 text-[#82959B]" />
          </button>
          <button className="p-2 hover:bg-[#131F23] rounded-lg">
            <Bell className="w-5 h-5 text-[#82959B]" />
          </button>
          <button className="p-2 hover:bg-[#131F23] rounded-lg">
            <Plus className="w-5 h-5 text-[#82959B]" />
          </button>
          <button className="flex items-center gap-2 p-1.5 hover:bg-[#131F23] rounded-lg">
            <UserAvatar className="w-8 h-8 rounded-full" />
            <ChevronDown className="w-4 h-4 text-[#82959B] hidden lg:block" />
          </button>
        </div>
      </div>
    </nav>
  );
}