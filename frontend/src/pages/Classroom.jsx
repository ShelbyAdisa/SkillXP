import React, { useState } from 'react';
import {
  Flame, Sparkles, TrendingUp, Clock, Award
} from 'lucide-react';

// Import your new classroom components
import ClassHeader from '../components/classroom/ClassHeader';
import Feed from '../components/classroom/Feed';
import Sidebar from '../components/classroom/Sidebar';

// Data from the original file
const initialPosts = [
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
];

const sortOptions = [
  { name: 'Best', icon: Award },
  { name: 'Hot', icon: Flame },
  { name: 'New', icon: Sparkles },
  { name: 'Top', icon: TrendingUp },
  { name: 'Rising', icon: Clock }
];

export default function Classroom() {
  // --- State ---
  // In the future, you'll fetch this data based on the :classId from the URL
  const [posts, setPosts] = useState(initialPosts);
  const [sortBy, setSortBy] = useState('Best');
  const [isSortOpen, setIsSortOpen] = useState(false);
  const [joined, setJoined] = useState(true);

  // --- Logic ---
  const handleVote = (postId, direction) => {
    setPosts(posts.map(post => {
      // --- THIS IS THE FIX ---
      if (post.id === postId) { 
      // ---------------------
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

  const sortedPosts = [...posts].sort((a, b) => {
    switch (sortBy) {
      case 'New':
        return b.id - a.id;
      case 'Rising':
        return b.comments - a.comments;
      case 'Best':
      case 'Hot':
      case 'Top':
      default:
        return b.votes - a.votes;
    }
  });

  // --- Render ---
  // This component is rendered *inside* the <Layout>,
  // so it doesn't need the navbar or site background color.
  return (
    <>
      {/* Banner */}
      <div className="pt-14">
        <div className="h-20 bg-gradient-to-r from-[#0079d3] to-[#00a8cc] relative overflow-hidden">
          <div className="absolute inset-0 opacity-10" style={{
            backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,.05) 10px, rgba(255,255,255,.05) 20px)'
          }}></div>
        </div>
      </div>

      {/* Class Header */}
      <ClassHeader joined={joined} setJoined={setJoined} />

      {/* Main Content */}
      <div className="max-w-[1400px] mx-auto px-4 py-5">
        <div className="flex gap-6 justify-center">
          
          {/* Feed */}
          <Feed
            sortedPosts={sortedPosts}
            handleVote={handleVote}
            sortBy={sortBy}
            setSortBy={setSortBy}
            isSortOpen={isSortOpen}
            setIsSortOpen={setIsSortOpen}
            sortOptions={sortOptions}
          />
          
          {/* Sidebar */}
          <Sidebar />

        </div>
      </div>
    </>
  );
}