import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "./../Sidebar";
import Avatar from "../shared/Avatar";

const DashboardLayout = ({ children, user }) => {
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    // your logout logic
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="flex-1 flex flex-col">


        {/* Main page content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 bg-gray-100">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
