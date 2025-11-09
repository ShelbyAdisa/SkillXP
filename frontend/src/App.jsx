import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import your main Layout (This has the site-wide navbar)
import Layout from './components/Layout';

// Import Standalone Pages (like Login, Signup)
import Login from './pages/Login';
import Signup from './pages/Signup';

// Import Your Main Pages (these will be wrapped by the Layout)
import Home from './pages/Home';
import Classroom from './pages/Classroom'; 


// Import Role-Specific Dashboards
import AdminDashboard from './pages/dashboards/AdminDashboard';
import ParentDashboard from './pages/dashboards/ParentDashboard';
import SchoolAdminDashboard from './pages/dashboards/SchoolAdminDashboard';
import StudentDashboard from './pages/dashboards/StudentDashboard';
import TeacherDashboard from './pages/dashboards/TeacherDashboard';

// Import Specific Parent Pages
import ParentChildren from './pages/parent/ParentChildren';
import ParentNotifications from './pages/parent/ParentNotifications';
import ParentProgress from './pages/parent/ParentProgress';

// Import the new Student Profile Page
import StudentProfile from './pages/student/StudentProfile'; // <-- 1. NEW IMPORT

// (Note: The old 'Dashboard.jsx' page is no longer imported or used)

function App() {
  return (
    <Router>
      <Routes>
        {/* --- Standalone Routes --- */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* --- Main App Routes --- */}
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          
          <Route path="/classroom/:classId" element={<Classroom />} />

          {/* === YOUR NEW TEST ROUTE === */}
          <Route path="/StudentDashboard" element={<StudentDashboard />} />

          {/* Role-Specific Dashboards */}
          <Route path="/student/dashboard" element={<StudentDashboard />} />
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/parent/dashboard" element={<ParentDashboard />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/school-admin/dashboard" element={<SchoolAdminDashboard />} />

          {/* New Student Profile Route */}
          <Route path="/student/profile" element={<StudentProfile />} /> {/* <-- 2. NEW ROUTE */}


          {/* Parent-Specific Pages */}
          <Route path="/parent/children" element={<ParentChildren />} />
          <Route path="/parent/notifications" element={<ParentNotifications />} />
          <Route path="/parent/progress" element={<ParentProgress />} />


          {/* <Route path="*" element={<NotFoundPage />} /> */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;