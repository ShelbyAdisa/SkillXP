import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Card from '../components/shared/Card';
import Button from '../components/shared/Button';
import { useAuth } from '../context/AuthContext';
import { LogIn } from 'lucide-react';

// --- Dashboard path map based on roles from Sidebar.jsx ---
const ROLE_DASHBOARD_MAP = {
    STUDENT: '/dashboard',
    TEACHER: '/teacher/dashboard',
    PARENT: '/parent/dashboard',
    ADMIN: '/admin/dashboard',
    SCHOOL_ADMIN: '/school-admin/dashboard',
};
// ----------------------------------------------------------

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      
      // --- MODIFICATION: Determine redirect path based on role ---
      // We retrieve the stored user data by email after successful login
      const storedUserString = localStorage.getItem(`user_${email}`);
      const storedUser = JSON.parse(storedUserString);
      
      // Get the correct path, defaulting to '/dashboard' if role is unexpected
      const redirectPath = ROLE_DASHBOARD_MAP[storedUser.role] || '/dashboard';

      navigate(redirectPath); 
      // --------------------------------------------------------------
    } catch (err) {
      console.error('Login error:', err);
      // Local Storage errors
      const errorMessage = err.message || 'Invalid login credentials.';
        
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md p-8 shadow-xl">
        <div className="text-center mb-8">
          <LogIn className="w-8 h-8 text-slate-900 mx-auto mb-2" />
          <h1 className="text-3xl font-bold text-slate-900">Welcome Back</h1>
          <p className="text-slate-600">Sign in to SkillXP Nexus</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-3 text-sm font-medium text-red-700 bg-red-100 border border-red-300 rounded-lg">
              Error: {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="email">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
              placeholder="you@school.edu"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500"
              placeholder="••••••••"
            />
          </div>

          <Button type="submit" variant="primary" color="slate" className="w-full" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-600">
          Don't have an account?{' '}
          <Link to="/signup" className="font-medium text-slate-700 hover:text-slate-900">
            Sign up here
          </Link>
        </div>
      </Card>
    </div>
  );
};

export default Login;