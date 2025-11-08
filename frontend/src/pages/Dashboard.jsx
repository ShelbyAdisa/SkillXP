import React, { useState } from 'react';
import {
  ArrowUp, ArrowDown, MessageSquare, Share2, Bookmark, MoreHorizontal, Plus,
  Search, Bell, MessageCircle, ChevronDown, Flame, Sparkles, TrendingUp, Clock,
  Menu, Award, Check // Added Award and Check for the new dropdown
} from 'lucide-react';

export default function SkillXPDashboard() {
  const [posts, setPosts] = useState([
    {
      id: 1,
      author: 'TeacherMike',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=TeacherMike',
      time: '4h ago',
      title: 'Just finished Module 3 on JavaScript Promises - This analogy helped me understand',
      content: 'Think of promises like ordering food at a restaurant. You place your order (create promise), you get a receipt (pending), then either your food arrives (resolved) or they tell you they\'re out of that dish (rejected). This completely changed how I understand async code and now everything makes so much more sense!',
      flair: { emoji: '💡', text: 'Tutorial', color: 'bg-emerald-500/10 text-emerald-400' },
      votes: 342,
      userVote: 0,
      comments: 87,
      image: null
    },
    {
      id: 2,
      author: 'CodeNewbie2024',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=CodeNewbie',
      time: '6h ago',
      title: 'Week 2 Assignment - Need help understanding recursion',
      content: 'I\'ve watched the lecture three times but I\'m still confused about the factorial example. Can someone explain it in simpler terms? I understand the base case but the recursive call is throwing me off. Any analogies or visual examples would be super helpful!',
      flair: { emoji: '❓', text: 'Question', color: 'bg-blue-500/10 text-blue-400' },
      votes: 156,
      userVote: 0,
      comments: 43,
      image: null
    },
    {
      id: 3,
      author: 'DevStudent',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=DevStudent',
      time: '8h ago',
      title: 'My final project for the React course - A todo app with authentication!',
      content: 'Finally deployed my first full-stack application! It took me 3 weeks but I learned so much about React hooks, JWT authentication, and MongoDB. Features include user registration, protected routes, and real-time updates. Would love feedback!',
      flair: { emoji: '🎉', text: 'Project', color: 'bg-purple-500/10 text-purple-400' },
      votes: 892,
      userVote: 0,
      comments: 124,
      image: 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=800&h=400&fit=crop'
    },
    {
      id: 4,
      author: 'StudyBuddy',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=StudyBuddy',
      time: '12h ago',
      title: 'Study group forming for the upcoming Algorithm Design exam',
      content: 'Looking for 3-4 people to join a study group. Planning to meet twice a week on Zoom to go through practice problems and review lecture material. All skill levels welcome! Send me a DM if you\'re interested in joining.',
      flair: { emoji: '📚', text: 'Study Group', color: 'bg-amber-500/10 text-amber-400' },
      votes: 234,
      userVote: 0,
      comments: 56,
      image: null
    },
    {
      id: 5,
      author: 'ProfessorSmith',
      authorAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Professor',
      time: '1d ago',
      title: 'Office hours this Thursday moved to Friday 2-4pm',
      content: 'Due to a scheduling conflict, this week\'s office hours will be moved from Thursday to Friday afternoon. Same Zoom link applies. Looking forward to answering your questions about the midterm!',
      flair: { emoji: '📢', text: 'Announcement', color: 'bg-red-500/10 text-red-400' },
      votes: 567,
      userVote: 0,
      comments: 23,
      image: null
    }
  ]);

  // --- NEW: State for sorting ---
  const [sortBy, setSortBy] = useState('Best'); // Default to 'Best'
  const [isSortOpen, setIsSortOpen] = useState(false);
  const [joined, setJoined] = useState(true);

  // --- NEW: Define all sort options ---
  const sortOptions = [
    { name: 'Best', icon: Award },
    { name: 'Hot', icon: Flame },
    { name: 'New', icon: Sparkles },
    { name: 'Top', icon: TrendingUp },
    { name: 'Rising', icon: Clock }
  ];

  // Get the icon for the currently selected sort
  const CurrentSortIcon = sortOptions.find(o => o.name === sortBy)?.icon || Award;

  // Small shared SVGs for logo and avatar to keep icons consistent
  const BrandLogo = ({ className = 'w-8 h-8' }) => (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="12" fill="#1F8FFF" />
      {/* mortarboard / graduation cap */}
      <path d="M12 7l8 3-8 3-8-3 8-3zm0 5v5" stroke="#fff" strokeWidth="0.9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );

  const UserAvatar = ({ className = 'w-10 h-10' }) => (
    <img 
  src="https://api.dicebear.com/7.x/avataaars/svg?seed=User" 
  className="w-8 h-8 rounded-full" 
  alt="User Avatar" 
/>
  );

  const handleVote = (postId, direction) => {
    setPosts(posts.map(post => {
      if (post.id === postId) {
        let newVote = direction;
        let voteDiff = 0;
        
        if (post.userVote === direction) {
          newVote = 0;
          voteDiff = -direction;
        } else {
          voteDiff = direction - post.userVote;
        }
        
        return { ...post, votes: post.votes + voteDiff, userVote: newVote };
      }
      return post;
    }));
  };

  // --- NEW: Sorting logic ---
  // Create a new, sorted array to render
  const sortedPosts = [...posts].sort((a, b) => {
    switch (sortBy) {
      case 'New':
        // Assumes higher ID = newer post.
        // A real app would use a timestamp.
        return b.id - a.id;
      case 'Rising':
        // Let's use comment count as a proxy for 'Rising'
        return b.comments - a.comments;
      case 'Best':
      case 'Hot':
      case 'Top':
      default:
        // Sort by votes for all other categories
        return b.votes - a.votes;
    }
  });

  return (
    <div className="min-h-screen bg-[#0B1416]">
      {/* Top Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0F1A1C] border-b border-[#223237] h-14">
        <div className="h-full px-4 flex items-center justify-between max-w-[1400px] mx-auto">
          <div className="flex items-center gap-4">
            <button className="lg:hidden p-2 hover:bg-[#131F23] rounded-lg">
              <Menu className="w-5 h-5 text-[#D7DADC]" />
            </button>
            <div className="flex items-center gap-2">
              <BrandLogo className="w-8 h-8" />
              <span className="hidden sm:block text-[#D7DADC] text-xl font-semibold">SkillXP</span>
            </div>
              <div className="hidden md:flex items-center bg-[#131F23] border border-[#223237] rounded-full px-4 py-2 w-80 lg:w-96">
              <Search className="w-4 h-4 text-[#82959B]" />
              <input 
                type="text"
                placeholder="Search SkillXP"
                className="ml-2 bg-transparent text-sm text-[#D7DADC] placeholder-[#82959B] outline-none w-full"
              />
            </div>
          </div>
            <div className="flex items-center gap-2">
            <button className="hidden lg:flex items-center gap-2 px-4 py-1.5 bg-[#131F23] hover:bg-[#223237] rounded-full">
              <TrendingUp className="w-4 h-4 text-[#B8C5C9]" />
              <span className="text-sm font-medium text-[#D7DADC]">Popular</span>
            </button>
            <button className="p-2 hover:bg-[#131F23] rounded-lg">
              <MessageCircle className="w-5 h-5 text-[#82959B]" />
            </button>
            <button className="p-2 hover:bg-[#131F23] rounded-lg">
              <Bell className="w-5 h-5 text-[#82959B]" />
            </button>
            <button className="p-2 hover:bg-[#131F23] rounded-lg">
              <Plus className="w-5 h-5 text-[#82959B]" />
            </button>
            <button className="flex items-center gap-2 p-1.5 hover:bg-[#131F23] rounded-lg">
              <UserAvatar className="w-8 h-8 rounded-full" />
              <ChevronDown className="w-4 h-4 text-[#82959B] hidden lg:block" />
            </button>
          </div>
        </div>
      </nav>

      {/* Banner */}
      <div className="pt-14">
        <div className="h-20 bg-gradient-to-r from-[#0079d3] to-[#00a8cc] relative overflow-hidden">
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,.05) 10px, rgba(255,255,255,.05) 20px)'
          }}></div>
        </div>
      </div>

      {/* Subreddit Header */}
      <div className="bg-[#0F1A1C] border-b border-[#223237]">
        <div className="max-w-[1400px] mx-auto px-4">
          <div className="flex items-end -mt-3 pb-4">
            <div className="w-20 h-20 bg-[#0079d3] border-4 border-[#0F1A1C] rounded-full flex items-center justify-center text-4xl shrink-0">
              📚
            </div>
            <div className="ml-4 flex-1 min-w-0">
              <h1 className="text-[#D7DADC] text-2xl font-bold">LearnProgramming</h1>
              <p className="text-[#82959B] text-sm">Class: LearnProgramming</p>
            </div>
            <button 
              onClick={() => setJoined(!joined)}
              className={`px-6 py-1.5 rounded-full font-bold text-sm shrink-0 ${
                joined 
                  ? 'bg-[#223237] text-[#D7DADC] hover:bg-[#2d3f45] border border-[#2d3f45]'
                  : 'bg-[#D7DADC] text-[#0F1A1C] hover:bg-white'
              }`}
            >
              {joined ? 'Joined' : 'Join'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-[1400px] mx-auto px-4 py-5">
  <div className="flex gap-6 justify-center">
          {/* Feed */}
          <div className="flex-1 max-w-[640px]">
            {/* Create Post Bar */}
            <div className="bg-[#0F1A1C] border border-[#223237] rounded-lg p-3 mb-4 flex items-center gap-3">
              {/* use same svg/avatar as navbar profile for create post */}
              <UserAvatar className="w-10 h-10 rounded-full" />
              <input 
                type="text"
                placeholder="Create Post"
                className="flex-1 bg-[#131F23] border border-[#223237] hover:border-[#2d3f45] hover:bg-[#0F1A1C] rounded px-4 py-2 text-sm text-[#D7DADC] placeholder-[#82959B] outline-none cursor-pointer"
              />
            </div>

            {/* --- REPLACED: Sort Tabs now a Dropdown --- */}
            <div className="relative mb-4">
              <button
                onClick={() => setIsSortOpen(!isSortOpen)}
                className="bg-[#0F1A1C] border border-[#223237] rounded-lg p-2 flex items-center w-full hover:border-[#2d3f45] text-left"
              >
                <CurrentSortIcon className="w-5 h-5 text-[#82959B] shrink-0" />
                <span className="text-sm font-medium text-[#D7DADC] capitalize ml-2">
                  {sortBy}
                </span>
                <ChevronDown className="w-5 h-5 text-[#82959B] ml-auto shrink-0" />
              </button>

              {isSortOpen && (
                <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-[#0F1A1C] border border-[#223237] rounded-lg overflow-hidden shadow-lg">
                  {sortOptions.map(({ name, icon: Icon }) => (
                    <button
                      key={name}
                      onClick={() => {
                        setSortBy(name);
                        setIsSortOpen(false);
                      }}
                      className={`flex items-center w-full gap-2 px-3 py-2 text-left text-sm transition-colors ${
                        sortBy === name
                          ? 'bg-[#223237] text-[#D7DADC]'
                          : 'text-[#82959B] hover:bg-[#131F23]'
                      }`}
                    >
                      <Icon className="w-5 h-5 shrink-0" />
                      <span>{name}</span>
                      {sortBy === name && <Check className="w-5 h-5 ml-auto shrink-0" />}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {/* --- END REPLACEMENT --- */}

            {/* Posts */}
            <div className="space-y-3">
              {/* --- UPDATED: Map over sortedPosts instead of posts --- */}
              {sortedPosts.map(post => (
                <div key={post.id} className="bg-[#0F1A1C] border border-[#223237] hover:border-[#2d3f45] rounded-xl overflow-hidden transition-colors">
                  {/* Post Header */}
                  <div className="px-4 pt-3 pb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <img src={post.authorAvatar} className="w-8 h-8 rounded-full shrink-0" alt={`${post.author} avatar`} />
                      <div className="min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="text-xs font-medium text-[#B8C5C9] truncate">Class: LearnProgramming</span>
                          <span className="text-[#82959B]">•</span>
                          <span className="text-xs text-[#82959B]">{post.time}</span>
                        </div>
                        <div className="text-xs text-[#82959B] truncate">u/{post.author}</div>
                      </div>
                    </div>
                    <button className="p-1 hover:bg-[#131F23] rounded-lg shrink-0">
                      <MoreHorizontal className="w-5 h-5 text-[#82959B]" />
                    </button>
                  </div>

                  {/* Post Content */}
                  <div className="px-4 pb-3">
                    <h2 className="text-[#D7DADC] text-lg font-semibold leading-snug mb-2">{post.title}</h2>
                    
                    {post.flair && (
                      <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium mb-3 ${post.flair.color}`}>
                        <span>{post.flair.emoji}</span>
                        <span>{post.flair.text}</span>
                      </div>
                    )}
                    
                    <p className="text-[#B8C5C9] text-sm leading-relaxed line-clamp-3">{post.content}</p>
                  </div>

                  {/* Post Image */}
                  {post.image && (
                    <div className="px-4 pb-3">
                      <img src={post.image} className="w-full rounded-lg" alt="Post content" />
                    </div>
                  )}

                  {/* Action Bar */}
                  <div className="px-3 pb-2 flex items-center gap-1">
                    <button 
                      onClick={() => handleVote(post.id, 1)}
                      className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23] transition-colors ${
                        post.userVote === 1 ? 'bg-[#131F23]' : ''
                      }`}
                    >
                      <ArrowUp className={`w-5 h-5 ${post.userVote === 1 ? 'text-orange-500 fill-orange-500' : 'text-[#82959B]'}`} />
                      <span className={`text-xs font-bold ${
                        post.userVote === 1 ? 'text-orange-500' : 
                        post.userVote === -1 ? 'text-blue-500' : 
                        'text-[#B8C5C9]'
                      }`}>
                        {post.votes >= 1000 ? `${(post.votes / 1000).toFixed(1)}k` : post.votes}
                      </span>
                      <ArrowDown 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleVote(post.id, -1);
                        }}
                        className={`w-5 h-5 ${post.userVote === -1 ? 'text-blue-500 fill-blue-500' : 'text-[#82959B]'}`} 
                      />
                    </button>
                    <button className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23]">
                      <MessageSquare className="w-5 h-5 text-[#82959B]" />
                      <span className="text-xs font-bold text-[#B8C5C9]">{post.comments}</span>
                    </button>
                    <button className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23]">
                      <Share2 className="w-5 h-5 text-[#82959B]" />
                      <span className="text-xs font-bold text-[#B8C5C9]">Share</span>
                    </button>
                    <button className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23] ml-auto">
                      <Bookmark className="w-5 h-5 text-[#82959B]" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Sidebar */}
          {/* Right Sidebar */}
          <div className="hidden lg:block w-80 shrink-0 space-y-4">
            {/* About Community */}
            <div className="bg-[#0F1A1C] border border-[#223237] rounded-xl overflow-hidden">
              <div className="h-10 bg-gradient-to-r from-[#0079d3] to-[#00a8cc]"></div>
              <div className="p-4">
                <h3 className="text-[#D7DADC] text-sm font-semibold mb-3">About Class</h3>
                <p className="text-[#B8C5C9] text-sm leading-relaxed mb-4">
                  A place for students and instructors to discuss coursework, share resources, and collaborate on class projects.
                </p>
                <div className="flex gap-4 mb-4">
                  <div>
                    <div className="text-[#D7DADC] text-base font-semibold">124</div>
                    <div className="text-[#82959B] text-xs">Members</div>
                  </div>
                  <div>
                    <div className="text-[#D7DADC] text-base font-semibold">2</div>
                    <div className="text-[#82959B] text-xs">Online</div>
                  </div>
                </div>
                <div className="border-t border-[#223237] pt-3 mb-4">
                  <div className="text-[#82959B] text-xs">Created Jan 15, 2024</div>
                </div>
                <button className="w-full bg-[#D7DADC] hover:bg-white text-[#0F1A1C] font-bold text-sm py-2 rounded-full transition-colors">
                  Create Post
                </button>
              </div>
            </div>

            {/* Rules */}
            <div className="bg-[#0F1A1C] border border-[#223237] rounded-xl p-4 text-sm">
              <h3 className="text-[#D7DADC] text-sm font-semibold mb-3">Classroom Rules</h3>
              <div className="space-y-3">
                {[
                  'Be respectful and civil to peers and instructors.',
                  'No plagiarism or cheating — cite sources and submit original work.',
                  'Keep posts related to course topics and assignments.',
                  'No spam, advertising, or off-topic self-promotion.',
                  'Use appropriate tags (Question, Assignment, Resource) and include context.'
                ].map((rule, idx) => (
                  <div key={idx} className="text-[#B8C5C9] pb-3 border-b border-[#223237] last:border-0">
                    <span className="text-[#D7DADC] font-medium">{idx + 1}.</span> {rule}
                  </div>
                ))}
              </div>
            </div>

            {/* Moderators */}
            <div className="bg-[#0F1A1C] border border-[#223237] rounded-xl p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-[#D7DADC] text-sm font-semibold">Instructors</h3>
                <button className="text-[#0079d3] hover:underline text-xs font-bold">View all</button>
              </div>
              <div className="space-y-3">
                {['ProfessorSmith', 'TeachingAssistant', 'CourseAdmin'].map((mod, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${mod}`} className="w-8 h-8 rounded-full" alt={`${mod} avatar`} />
                    <span className="text-[#B8C5C9] text-sm hover:underline cursor-pointer">{mod}</span>
                  </div>
                ))}
              </div>
              <button className="w-full mt-4 border border-[#223237] hover:bg-[#131F23] text-[#D7DADC] font-bold text-sm py-2 rounded-full transition-colors">
                Message the instructors
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}