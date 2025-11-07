import { useState, useMemo } from "react";
import { Trophy, X } from "lucide-react";

export default function Leaderboard({ leaderboard = [], showLeaderboard, setShowLeaderboard }) {
  const items = Array.isArray(leaderboard) ? leaderboard : [];
  const [internalShow, setInternalShow] = useState(showLeaderboard ?? true);
  const isOpen = useMemo(() => (typeof showLeaderboard === 'boolean' ? showLeaderboard : internalShow), [showLeaderboard, internalShow]);

  const onClose = () => {
    if (typeof setShowLeaderboard === 'function') {
      setShowLeaderboard(false);
    } else {
      setInternalShow(false);
    }
  };
  return (
    <div
      className={`fixed top-0 right-0 h-full w-96 bg-white border-l border-slate-200 transition-transform duration-300 z-50 ${
        isOpen ? "translate-x-0" : "translate-x-full"
      }`}
    >
      <div className="p-6 h-full flex flex-col">
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-xl font-semibold text-slate-900">Leaderboard</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-slate-100 flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5 text-slate-600" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2">
          {items.length === 0 && (
            <div className="p-4 rounded-lg bg-slate-50 text-slate-600 text-sm">
              No leaderboard data yet.
            </div>
          )}
          {items.map((user) => (
            <div
              key={user.rank}
              className={`p-4 rounded-lg transition-all ${
                user.isCurrentUser
                  ? "bg-slate-100 border border-slate-300"
                  : "hover:bg-slate-50"
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm ${
                    user.rank === 1
                      ? "bg-yellow-400 text-yellow-900"
                      : user.rank === 2
                      ? "bg-slate-300 text-slate-700"
                      : user.rank === 3
                      ? "bg-orange-400 text-orange-900"
                      : "bg-slate-200 text-slate-600"
                  }`}
                >
                  {user.rank}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <p className="font-medium text-slate-900 truncate">{user.name}</p>
                    {user.isCurrentUser && (
                      <span className="px-2 py-0.5 rounded bg-slate-900 text-white text-xs font-medium">
                        You
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-slate-600">
                    {(Number.isFinite(user?.xp) ? user.xp : 0).toLocaleString()} XP
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
