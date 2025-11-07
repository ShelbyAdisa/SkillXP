import React from 'react'
import { Link } from 'react-router-dom'
import { GraduationCap, Mail, Github, Twitter, Linkedin } from 'lucide-react'

const Footer = () => {
  return (
    <footer className="bg-slate-100 text-slate-700">
      <div className="max-w-[1200px] mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Section */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="bg-slate-900 p-2 rounded-lg">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-slate-900">SkillXP Nexus</span>
            </div>
            <p className="text-slate-600 mb-4 max-w-md">
              Transform your learning journey with gamified education. Earn XP, climb leaderboards, and unlock your full potential.
            </p>
            <div className="flex items-center gap-3">
              <a href="#" className="w-10 h-10 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 flex items-center justify-center transition-colors">
                <Twitter className="w-5 h-5 text-slate-700" />
              </a>
              <a href="#" className="w-10 h-10 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 flex items-center justify-center transition-colors">
                <Linkedin className="w-5 h-5 text-slate-700" />
              </a>
              <a href="#" className="w-10 h-10 rounded-lg bg-white border border-slate-300 hover:bg-slate-50 flex items-center justify-center transition-colors">
                <Github className="w-5 h-5 text-slate-700" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-slate-900 font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/home" className="hover:text-slate-900 transition-colors">Home</Link>
              </li>
              <li>
                <Link to="/dashboard" className="hover:text-slate-900 transition-colors">Dashboard</Link>
              </li>
              <li>
                <Link to="/elibrary" className="hover:text-slate-900 transition-colors">eLibrary</Link>
              </li>
              <li>
                <Link to="/forums" className="hover:text-slate-900 transition-colors">Forums</Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="text-slate-900 font-semibold mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/login" className="hover:text-slate-900 transition-colors">Login</Link>
              </li>
              <li>
                <Link to="/signup" className="hover:text-slate-900 transition-colors">Sign Up</Link>
              </li>
              <li>
                <a href="#" className="hover:text-slate-900 transition-colors">Help Center</a>
              </li>
              <li>
                <a href="#" className="flex items-center gap-2 hover:text-slate-900 transition-colors">
                  <Mail className="w-4 h-4" />
                  Contact Us
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-slate-300">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-600">
              © {new Date().getFullYear()} SkillXP Nexus. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm">
              <a href="#" className="hover:text-slate-900 transition-colors">Privacy Policy</a>
              <a href="#" className="hover:text-slate-900 transition-colors">Terms of Service</a>
              <a href="#" className="hover:text-slate-900 transition-colors">Cookie Policy</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

export default Footer

