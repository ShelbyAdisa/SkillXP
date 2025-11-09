import { useState, useEffect } from 'react';

// --- FIX: Updated with DiceBear avatars and placehold.co images ---
const DUMMY_POSTS = [
  {
    id: 1,
    author: 'tech_wizard_01',
    authorAvatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Ryan',
    time: '2 hours ago',
    title: 'I built a new app with React Native!',
    content: 'It was a really fun project, learned a lot about mobile dev. React Native makes it so easy to build cross-platform. Has anyone else tried it?',
    image: 'https://img.freepik.com/free-vector/furniture-shopping-app-interface_23-2148660330.jpg',
    flair: { text: 'Project', emoji: '🚀', color: 'bg-blue-600 text-blue-100' },
    votes: 128,
    comments: 16,
    userVote: 0,
    className: 'WebDev',
    classSlug: 'webdev',
  },
  {
    id: 2,
    author: 'history_buff_88',
    authorAvatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Aidan',
    time: '5 hours ago',
    title: 'Discussion: The fall of the Roman Empire',
    content: 'What do you think was the single biggest factor? I\'m arguing it was economic instability, not just barbarian invasions.',
    image: null,
    flair: { text: 'Discussion', emoji: '💬', color: 'bg-green-600 text-green-100' },
    votes: 42,
    comments: 31,
    userVote: 1,
    className: 'History101',
    classSlug: 'history101',
  },
  {
    id: 3,
    author: 'data_dreamer',
    authorAvatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Chase',
    time: '1 day ago',
    title: 'My new Matplotlib visualization for housing prices',
    content: 'Check out this visualization I made for my final project. The correlation between proximity to schools and price is fascinating.',
    image: 'https://realpython.com/cdn-cgi/image/width=1200,format=auto/https://files.realpython.com/media/gridspec_ex.9bce5a0726e9.png',
    flair: { text: 'Data', emoji: '📊', color: 'bg-yellow-600 text-yellow-100' },
    votes: 215,
    comments: 29,
    userVote: 0,
    className: 'DataScience',
    classSlug: 'datascience',
  },
  {
    id: 4,
    author: 'code_newbie',
    authorAvatar: 'https://api.dicebear.com/9.x/avataaars/svg?seed=Eliza',
    time: '2 days ago',
    title: 'Help with Python "for" loop',
    content: 'I\'m stuck on this simple loop, I keep getting an index error. Can anyone see what I\'m doing wrong?',
    image: null,
    flair: { text: 'Help', emoji: '❓', color: 'bg-red-600 text-red-100' },
    votes: 9,
    comments: 12,
    userVote: 0,
    // This post will still fall back to "LearnProgramming"
    className: null,
    classSlug: null,
  },
];

export const useStudentDashboardFeed = () => {
  const [posts, setPosts] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate an API call
    const timer = setTimeout(() => {
      setPosts(DUMMY_POSTS);
      setIsLoading(false);
    }, 500); // 0.5 second delay

    // Cleanup timer on component unmount
    return () => clearTimeout(timer);
  }, []);

  return { posts, isLoading };
};