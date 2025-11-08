import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Import your main Layout (This has the site-wide navbar)
import Layout from './components/Layout';

// Import Standalone Pages (like Login, Signup)
import Login from './pages/Login';
import Signup from './pages/Signup';

// Import Your Main Pages (these will be wrapped by the Layout)
import Home from './pages/Home';
import Classroom from './pages/Classroom'; // <-- This is our new refactored page
import AnalyticsDashboard from './pages/AnalyticsDashboard';
import Assignments from './pages/Assignments';
import ELibrary from './pages/ELibrary';
import Forums from './pages/Forums';
import LearningHub from './pages/LearningHub';
import Mentorship from './pages/Mentorship';
import Rewards from './pages/Rewards';
import SchoolGovernance from './pages/SchoolGovernance';
import Transparency from './pages/Transparency';
import Transportation from './pages/Transportation';
import Updates from './pages/Updates';
import Wellbeing from './pages/Wellbeing';

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

// (Note: The old 'Dashboard.jsx' page is no longer imported or used)

function App() {
  return (
    <Router>
      <Routes>
        {/* --- Standalone Routes --- */}
        {/* These routes DO NOT have the site-wide navbar */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* --- Main App Routes --- */}
        {/* These routes are all wrapped by <Layout />, 
            which provides the site-wide navbar and background */}
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          
          {/* This is the new, dynamic route for classrooms */}
          <Route path="/classroom/:classId" element={<Classroom />} />

          {/* Role-Specific Dashboards */}
          <Route path="/student/dashboard" element={<StudentDashboard />} />
          <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
          <Route path="/parent/dashboard" element={<ParentDashboard />} />
          <Route path="/admin/dashboard" element={<AdminDashboard />} />
          <Route path="/school-admin/dashboard" element={<SchoolAdminDashboard />} />

          {/* Parent-Specific Pages */}
          <Route path="/parent/children" element={<ParentChildren />} />
          <Route path="/parent/notifications" element={<ParentNotifications />} />
          <Route path="/parent/progress" element={<ParentProgress />} />

          {/* Other Main App Pages */}
          <Route path="/analytics" element={<AnalyticsDashboard />} />
          <Route path="/assignments" element={<Assignments />} />
          <Route path="/e-library" element={<ELibrary />} />
          <Route path="/forums" element={<Forums />} />
          <Route path="/learning-hub" element={<LearningHub />} />
          <Route path="/mentorship" element={<Mentorship />} />
          <Route path="/rewards" element={<Rewards />} />
          <Route path="/governance" element={<SchoolGovernance />} />
          <Route path="/transparency" element={<Transparency />} />
          <Route path="/transportation" element={<Transportation />} />
          <Route path="/updates" element={<Updates />} />
          <Route path="/wellbeing" element={<Wellbeing />} />

          {/* You can add a 404 "Not Found" page here if you like */}
          {/* <Route path="*" element={<NotFoundPage />} /> */}
        </Route>
      </Routes>
    </Router>
  );
}

export default App;