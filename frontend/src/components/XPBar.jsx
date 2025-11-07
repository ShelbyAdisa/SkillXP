import { Award } from "lucide-react";

export default function XPBar({ level, currentXP, nextLevelXP }) {
  const safeLevel = Number.isFinite(level) && level > 0 ? level : 1;
  const safeCurrent = Number.isFinite(currentXP) && currentXP >= 0 ? currentXP : 0;
  // Fallback: simple progression target if not provided
  const fallbackNext = safeLevel * 100;
  const safeNext = Number.isFinite(nextLevelXP) && nextLevelXP > 0 ? nextLevelXP : fallbackNext;

  const remaining = Math.max(safeNext - safeCurrent, 0);
  const rawPct = (safeCurrent / (safeNext || 1)) * 100;
  const xpPercentage = Math.max(0, Math.min(100, rawPct));

  const formatNum = (n) => {
    const num = Number.isFinite(n) ? n : 0;
    try {
      return num.toLocaleString();
    } catch {
      return String(num);
    }
  };

  return (
    <div className="mb-8 p-6 rounded-xl bg-white border border-slate-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-lg bg-slate-100 flex items-center justify-center">
            <Award className="w-7 h-7 text-slate-700" />
          </div>
          <div>
            <h3 className="font-semibold text-lg text-slate-900">Level {safeLevel}</h3>
            <p className="text-slate-600 text-sm">
              {formatNum(safeCurrent)} / {formatNum(safeNext)} XP
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-slate-600">Next level</p>
          <p className="font-semibold text-slate-900">{formatNum(remaining)} XP</p>
        </div>
      </div>
      <div className="relative w-full h-3 rounded-full bg-slate-100 overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 bg-slate-900 rounded-full transition-all duration-500"
          style={{ width: `${xpPercentage}%` }}
        />
      </div>
    </div>
  );
}
