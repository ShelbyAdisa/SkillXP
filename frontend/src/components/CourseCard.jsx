import { Calendar, TrendingUp } from "lucide-react";

export default function CourseCard({ course }) {
  return (
    <div className="group rounded-xl bg-white border border-slate-200 overflow-hidden hover:border-slate-300 transition-all cursor-pointer">
      {/* Thumbnail */}
      <div className="relative h-40 overflow-hidden bg-slate-100">
        <img
          src={course.thumbnail}
          alt={course.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute top-3 right-3 px-3 py-1 rounded-md bg-white border border-slate-200">
          <p className="text-xs font-semibold text-slate-900">{course.xp} XP</p>
        </div>
      </div>

      {/* Content */}
      <div className="p-5">
        <h3 className="font-semibold text-lg text-slate-900 mb-0.5">{course.name}</h3>
        <p className="text-slate-600 text-sm mb-4">{course.instructor}</p>

        <div className="flex items-center gap-4 mb-3 text-sm">
          <div className="flex items-center gap-1.5 text-slate-600">
            <Calendar className="w-4 h-4" />
            <span>Due {course.dueDate}</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-600">
            <TrendingUp className="w-4 h-4" />
            <span>{course.progress}%</span>
          </div>
        </div>

        {/* Progress bar */}
        <div className="relative w-full h-2 rounded-full bg-slate-100 overflow-hidden">
          <div
            className="absolute inset-y-0 left-0 rounded-full transition-all duration-500"
            style={{
              width: `${course.progress}%`,
              backgroundColor: course.accentColor,
            }}
          />
        </div>
      </div>
    </div>
  );
}
