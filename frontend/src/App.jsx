import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoadingSpinner from './components/shared/LoadingSpinner';

// --- AUTH PAGES ---
import Login from './pages/Login';
import Signup from './pages/Signup';

// --- STUDENT PAGES ---
import Dashboard from './pages/dashboards/StudentDashboard';
import Assignments from './pages/Assignments';
import ELibrary from './pages/ELibrary';
import Wellbeing from './pages/Wellbeing';
import Classroom from './pages/Classroom';
import Forums from './pages/Forums';
import Rewards from './pages/Rewards';

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

// Custom PrivateRoute component
const PrivateRoute = ({ children, role }) => {
  const { user, isAuthReady } = useAuth();

  if (!isAuthReady) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner text="Initializing..." />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Handle single role or array of roles
  const allowedRoles = Array.isArray(role) ? role : [role];
  if (role && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />; // Redirect unauthorized users
  }

  return children;
};

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* PUBLIC ROUTES */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* BASE DASHBOARD REDIRECT */}
          {/* <Route 
            path="/" 
            element={<Navigate to="/dashboard" replace />} 
          /> */}

          {/* STUDENT ROUTES */}
          <Route path="/dashboard" element={<PrivateRoute role="STUDENT"><Dashboard /></PrivateRoute>} />
          <Route path="/assignments" element={<PrivateRoute><Assignments /></PrivateRoute>} />
          <Route path="/elibrary" element={<PrivateRoute><ELibrary /></PrivateRoute>} />
          <Route path="/wellbeing" element={<PrivateRoute><Wellbeing /></PrivateRoute>} />
          <Route path="/classroom" element={<PrivateRoute><Classroom /></PrivateRoute>} />
          <Route path="/forums" element={<PrivateRoute><Forums /></PrivateRoute>} />
          <Route path="/rewards" element={<PrivateRoute><Rewards /></PrivateRoute>} />
          
          {/* TEACHER ROUTES */}
          <Route path="/teacher/dashboard" element={<PrivateRoute role="TEACHER"><TeacherDashboard /></PrivateRoute>} />
          
          {/* -------------------------------------------------------- */}
          {/* PARENT ROUTES: MAPPED TO UNIQUE COMPONENTS */}
          {/* -------------------------------------------------------- */}
          <Route path="/parent/dashboard" element={<PrivateRoute role="PARENT"><ParentDashboard /></PrivateRoute>} />
          
          {/* Route for Children link */}
          <Route path="/parent/children" element={<PrivateRoute role="PARENT"><ParentChildren /></PrivateRoute>} />
          
          {/* Route for Progress link */}
          <Route path="/parent/progress" element={<PrivateRoute role="PARENT"><ParentProgress /></PrivateRoute>} />
          
          {/* Route for Alerts link (mapped to ParentNotifications) */}
          <Route path="/parent/notifications" element={<PrivateRoute role="PARENT"><ParentNotifications /></PrivateRoute>} />
          
          {/* Route for Transport link (shared with School Admin) */}
          <Route path="/transportation" element={<PrivateRoute role="PARENT"><Transportation /></PrivateRoute>} />
          
          {/* -------------------------------------------------------- */}
          
          {/* ADMIN/SCHOOL ADMIN ROUTES */}
          <Route path="/admin/dashboard" element={<PrivateRoute role="ADMIN"><AdminDashboard /></PrivateRoute>} />
          <Route path="/school-admin/dashboard" element={<PrivateRoute role="SCHOOL_ADMIN"><SchoolAdminDashboard /></PrivateRoute>} />
          <Route path="/school-governance" element={<PrivateRoute role={['PARENT', 'SCHOOL_ADMIN']}><SchoolGovernance /></PrivateRoute>} />

          {/* 404 CATCH-ALL */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;