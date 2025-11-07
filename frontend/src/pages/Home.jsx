import React from 'react'
import { Link } from 'react-router-dom'
import Services from '../components/Services'
import Footer from '../components/Footer'
import Header from '../components/Header'
import { TrendingUp, Users, BookOpen, MessageCircle, ArrowRight, Zap, Shield, Heart } from 'lucide-react'

const Home = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <Header variant="public" />

      <main>
        {/* Hero Section */}
        <section className="bg-white border-b border-slate-200 py-16 sm:py-20 md:py-24">
          <div className="max-w-[1200px] mx-auto px-6 sm:px-8 md:px-12">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-slate-900 mb-6">
                  Learning that puts students first
                </h1>
                
                <p className="text-lg sm:text-xl text-slate-600 mb-8 leading-relaxed">
                  SkillXP Nexus is more than an LMS. We combine academics with wellbeing, 
                  mentorship, and community to create a holistic learning environment.
                </p>
                
                <div className="flex flex-col sm:flex-row items-start gap-4 mb-8">
                  <Link 
                    to="/signup" 
                    className="px-6 py-3 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors font-medium text-base flex items-center gap-2 w-full sm:w-auto justify-center"
                  >
                    Get Started
                    <ArrowRight className="w-4 h-4" />
                  </Link>
                  <Link 
                    to="/login" 
                    className="px-6 py-3 rounded-lg border border-slate-300 text-slate-900 hover:bg-slate-50 transition-colors font-medium text-base w-full sm:w-auto text-center"
                  >
                    Sign In
                  </Link>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-6 pt-8 border-t border-slate-200">
                  <div>
                    <p className="text-2xl sm:text-3xl font-semibold text-slate-900 mb-1">10,000+</p>
                    <p className="text-slate-600 text-sm">Students</p>
                  </div>
                  <div>
                    <p className="text-2xl sm:text-3xl font-semibold text-slate-900 mb-1">500+</p>
                    <p className="text-slate-600 text-sm">Educators</p>
                  </div>
                  <div>
                    <p className="text-2xl sm:text-3xl font-semibold text-slate-900 mb-1">50+</p>
                    <p className="text-slate-600 text-sm">Schools</p>
                  </div>
                </div>
              </div>

              {/* Hero Image */}
              <div className="relative">
                <div className="rounded-2xl overflow-hidden border border-slate-200 shadow-xl">
                  <img 
                    src="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop" 
                    alt="Students collaborating"
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* What Makes Us Different */}
        <section className="py-16 sm:py-20 bg-slate-50">
          <div className="max-w-[1200px] mx-auto px-6 sm:px-8">
            <div className="mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">What makes us different</h2>
              <p className="text-slate-600 text-lg">We prioritize the complete student experience</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
                  <Heart className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">Student Wellbeing First</h3>
                <p className="text-slate-600 leading-relaxed">
                  Built-in mental health support, anonymous help channels, and resources to ensure 
                  students feel safe and supported throughout their learning journey.
                </p>
              </div>

              <div>
                <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">Mentorship at Scale</h3>
                <p className="text-slate-600 leading-relaxed">
                  Connect students with mentors, enable peer-to-peer support, and foster meaningful 
                  relationships that extend beyond the classroom walls.
                </p>
              </div>

              <div>
                <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
                  <Zap className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">Engaged Learning</h3>
                <p className="text-slate-600 leading-relaxed">
                  Gamification that motivates without distraction. Track progress, earn achievements, 
                  and make learning something students actually want to do.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Core Features */}
        <section className="py-16 sm:py-20 bg-white">
          <div className="max-w-[1200px] mx-auto px-6 sm:px-8">
            <div className="mb-12">
              <h2 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">Everything your school needs</h2>
              <p className="text-slate-600 text-lg">A complete platform for modern education</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-4">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Smart eLibrary</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  AI-powered resource recommendations tailored to each student's learning style and needs.
                </p>
              </div>
              
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Classroom Hub</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Streamlined assignment management, attendance tracking, and real-time student progress monitoring.
                </p>
              </div>
              
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-4">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Wellbeing Hub</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Anonymous support channels, counselor connections, and mental health resources available 24/7.
                </p>
              </div>
              
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-4">
                  <Users className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Mentorship Network</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Match students with mentors, schedule sessions, and track mentorship outcomes at scale.
                </p>
              </div>
              
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-4">
                  <MessageCircle className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Community Forums</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Safe spaces for peer discussions, interest groups, and collaborative learning experiences.
                </p>
              </div>
              
              <div className="p-6 rounded-xl bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors">
                <div className="w-12 h-12 rounded-lg bg-slate-900 flex items-center justify-center mb-4">
                  <TrendingUp className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 mb-2">Analytics Dashboard</h3>
                <p className="text-slate-600 text-sm leading-relaxed">
                  Comprehensive insights into student performance, engagement, and wellbeing metrics.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Trust Section */}
        <section className="py-16 sm:py-20 bg-slate-50">
          <div className="max-w-[1200px] mx-auto px-6 sm:px-8">
            <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center">
              <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-6">
                <Shield className="w-8 h-8 text-slate-700" />
              </div>
              <h2 className="text-3xl font-bold text-slate-900 mb-4">Built for education, trusted by schools</h2>
              <p className="text-lg text-slate-600 mb-8 max-w-2xl mx-auto">
                FERPA compliant, enterprise-grade security, and dedicated support for your institution.
              </p>
              <Link 
                to="/signup" 
                className="inline-flex items-center gap-2 px-8 py-4 rounded-lg bg-slate-900 text-white hover:bg-slate-800 transition-colors font-semibold text-base"
              >
                Request a Demo
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 sm:py-20 bg-white">
          <div className="max-w-[1200px] mx-auto px-6 sm:px-8">
            <div className="bg-slate-900 rounded-2xl p-12 sm:p-16 text-center">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">Ready to transform your school?</h2>
              <p className="text-lg text-slate-300 mb-8 max-w-2xl mx-auto">
                Join the growing community of schools using SkillXP Nexus to create better learning experiences.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link 
                  to="/signup" 
                  className="px-8 py-4 rounded-lg bg-white text-slate-900 hover:bg-slate-100 transition-colors font-semibold text-base w-full sm:w-auto text-center"
                >
                  Get Started Free
                </Link>
                <Link 
                  to="/login" 
                  className="px-8 py-4 rounded-lg border-2 border-white text-white hover:bg-white/10 transition-colors font-semibold text-base w-full sm:w-auto text-center"
                >
                  Sign In
                </Link>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  )
}

export default Home