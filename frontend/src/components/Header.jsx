import { Trophy, LogOut, User } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Header({ userName, showLeaderboard, setShowLeaderboard, variant = 'dashboard' }) {
  const { user, logout } = useAuth();

  if (variant === 'public') {
    return (
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-[1200px] mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/home" className="text-xl font-semibold text-slate-900">SkillXP Nexus</Link>
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <Link to="/dashboard" className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-2">
                  <User className="w-4 h-4" />
                  Dashboard
                </Link>
                <button
                  onClick={logout}
                  className="px-4 py-2 rounded-lg bg-slate-700 text-white hover:bg-slate-600 transition-colors flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors">Log in</Link>
                <Link to="/signup" className="px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors">Sign up</Link>
              </>
            )}
          </div>
        </div>
      </header>
    );
  }

  return (
    <header className="bg-white border-b border-slate-200">
      <div className="max-w-[1400px] mx-auto px-8 py-5">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
            <p className="text-slate-600 text-sm mt-0.5">Welcome back, {userName}</p>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/home"
              className="px-4 py-2 rounded-lg border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors font-medium text-sm"
            >
              Home
            </Link>
            <button
              onClick={() => setShowLeaderboard(!showLeaderboard)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors font-medium text-sm"
            >
              <Trophy className="w-4 h-4" />
              Leaderboard
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
