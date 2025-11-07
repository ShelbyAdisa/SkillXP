// src/components/dashboard/Hero.jsx

import React from 'react';
import { Sparkles, Target, BookOpen } from 'lucide-react';

const Hero = ({ userName, streak, coursesInProgress }) => {
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div className="relative overflow-hidden rounded-xl md:rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4 sm:p-6 md:p-8 mb-6 md:mb-8">
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-40 h-40 md:w-64 md:h-64 bg-blue-500/10 rounded-full blur-3xl" />
      <div className="absolute bottom-0 left-0 w-40 h-40 md:w-64 md:h-64 bg-purple-500/10 rounded-full blur-3xl" />
      
      <div className="relative z-10">
        <div className="flex flex-col lg:flex-row items-start justify-between gap-4">
          <div className="flex-1 w-full">
            <div className="flex items-center gap-2 mb-2">
              <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-yellow-400" />
              <span className="text-yellow-400 text-xs sm:text-sm font-medium">Keep it up!</span>
            </div>
            <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white mb-2">
              {getGreeting()}, {userName}
            </h2>
            <p className="text-slate-300 text-sm sm:text-base md:text-lg mb-4 sm:mb-6">
              Ready to continue your learning journey?
            </p>

            <div className="flex flex-col sm:flex-row flex-wrap gap-4 sm:gap-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center flex-shrink-0">
                  <Target className="w-5 h-5 sm:w-6 sm:h-6 text-blue-400" />
                </div>
                <div>
                  <p className="text-xl sm:text-2xl font-bold text-white">{streak}</p>
                  <p className="text-slate-400 text-xs sm:text-sm">Day Streak</p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-white/10 backdrop-blur-sm flex items-center justify-center flex-shrink-0">
                  <BookOpen className="w-5 h-5 sm:w-6 sm:h-6 text-purple-400" />
                </div>
                <div>
                  <p className="text-xl sm:text-2xl font-bold text-white">{coursesInProgress}</p>
                  <p className="text-slate-400 text-xs sm:text-sm">Active Courses</p>
                </div>
              </div>
            </div>
          </div>

          {/* Optional illustration or image */}
          <div className="hidden lg:block flex-shrink-0">
            <div className="w-32 h-32 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 backdrop-blur-sm flex items-center justify-center">
              <div className="w-20 h-20 rounded-xl bg-white/10 flex items-center justify-center">
                <Sparkles className="w-10 h-10 text-yellow-400" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;