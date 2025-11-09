import React from 'react';
import { Outlet } from 'react-router-dom';
import SiteNavbar from './layout/SiteNavbar';
import  ChatBox  from './chat/ChatBox'; // Import the new navbar

export default function Layout() {
  return (
    // This div provides the site-wide background
    <div className="min-h-screen bg-[#0B1416]"> 
      <SiteNavbar />
      <main>
        {/* Outlet renders the current page (e.g., /classroom/learnprogramming) */}
        <Outlet /> 
      </main>
      <ChatBox />
    </div>
  );
}