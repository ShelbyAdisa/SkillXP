import React from 'react'
import { Award, BookOpen, Users } from 'lucide-react'

const Services = () => {
  return (
    <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="p-6 rounded-xl bg-white border border-slate-200">
        <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center mb-3">
          <Award className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Gamified Progress</h3>
        <p className="text-slate-600 text-sm">Earn XP, track streaks, and level up your learning journey.</p>
      </div>

      <div className="p-6 rounded-xl bg-white border border-slate-200">
        <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center mb-3">
          <BookOpen className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Personalized Hub</h3>
        <p className="text-slate-600 text-sm">Manage courses, track progress, and resume where you left off.</p>
      </div>

      <div className="p-6 rounded-xl bg-white border border-slate-200">
        <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center mb-3">
          <Users className="w-5 h-5 text-white" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Community & Leaderboards</h3>
        <p className="text-slate-600 text-sm">Learn with peers and see your rank across your school.</p>
      </div>
    </section>
  )
}

export default Services

