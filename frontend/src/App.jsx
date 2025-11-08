import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// --- AUTH PAGES ---
import Login from './pages/Login';
import Signup from './pages/Signup';
import { ThemeProvider } from './context/ThemeContext.jsx';

// --- STUDENT PAGES ---
import Dashboard from './pages/dashboards/StudentDashboard';
import Assignments from './pages/Assignments';
import ELibrary from './pages/ELibrary';
import Wellbeing from './pages/Wellbeing';
import Classroom from './pages/Classroom';
import Forums from './pages/Forums';
import Rewards from './pages/Rewards';
import TestDash from './pages/Dashboard';

// --- TEACHER PAGES ---
import TeacherDashboard from './pages/dashboards/TeacherDashboard';

// --- PARENT PAGES (NEW MAPPINGS) ---
import ParentDashboard from './pages/dashboards/ParentDashboard';
import ParentChildren from './pages/parent/ParentChildren'; // New File
import ParentProgress from './pages/parent/ParentProgress'; // New File
import ParentNotifications from './pages/parent/ParentNotifications'; // New File (for Alerts)
import Transportation from './pages/Transportation'; // New File (for Transport)

// --- ADMIN PAGES ---
import AdminDashboard from './pages/dashboards/AdminDashboard';
import SchoolAdminDashboard from './pages/dashboards/SchoolAdminDashboard';
import SchoolGovernance from './pages/SchoolGovernance';

function App() {
  return (
    <BrowserRouter>
        <Routes>
  {/* PUBLIC ROUTES */}
  <Route path="/" element={<Navigate to="/dashboard" replace />} />
  <Route path="/login" element={<Login />} />
  <Route path="/signup" element={<Signup />} />

  {/* STUDENT ROUTES */}
  <Route path="/dashboard" element={<TestDash />} />
  <Route path="/assignments" element={<Assignments />} />
  <Route path="/elibrary" element={<ELibrary />} />
  <Route path="/wellbeing" element={<Wellbeing />} />
  <Route path="/classroom" element={<Classroom />} />
  <Route path="/forums" element={<Forums />} />
  <Route path="/rewards" element={<Rewards />} />
  
  {/* TEACHER ROUTES */}
  <Route path="/teacher/dashboard" element={<TeacherDashboard />} />
  
  {/* PARENT ROUTES */}
  <Route path="/parent/dashboard" element={<ParentDashboard />} />
  <Route path="/parent/children" element={<ParentChildren />} />
  <Route path="/parent/progress" element={<ParentProgress />} />
  <Route path="/parent/notifications" element={<ParentNotifications />} />
  <Route path="/transportation" element={<Transportation />} />
  
  {/* ADMIN ROUTES */}
  <Route path="/admin/dashboard" element={<AdminDashboard />} />
  <Route path="/school-admin/dashboard" element={<SchoolAdminDashboard />} />
  <Route path="/school-governance" element={<SchoolGovernance />} />

  {/* 404 */}
  <Route path="*" element={<Navigate to="/" replace />} />
</Routes>

    </BrowserRouter>
  );
}

export default App;