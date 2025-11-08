import { useState } from 'react';

// Define the dummy data right here
const dummyFeed = [
  {
    id: 'asg-1',
    type: 'ASSIGNMENT',
    skillspace: 's/calculus-101',
    author: 'u/teacher-smith',
    timestamp: 'Due: Tomorrow @ 11:59 PM',
    title: 'Chapter 5 Problem Set',
    content: 'Complete problems 1-10 on page 50. Show your work!',
    stats: { upvotes: 2, comments: 4 },
    callToAction: { text: 'View Assignment', link: '/assignments/1' }
  },
  {
    id: 'grd-1',
    type: 'GRADE',
    skillspace: 's/history-202',
    author: 'System',
    timestamp: '1 hour ago',
    title: 'History Essay Grade is In!',
    content: 'You scored 88/100. Well done.',
    stats: { upvotes: 1, comments: 0 },
    callToAction: { text: 'View Feedback', link: '/grades/history-essay' }
  },
  {
    id: 'post-1',
    type: 'DISCUSSION',
    skillspace: 's/python-basics',
    author: 'u/sara-peer',
    timestamp: '3 hours ago',
    title: "Stuck on the 'for loop' in Project 2...",
    content: "I keep getting an infinite loop, can anyone see why? Here's my code snippet...",
    stats: { upvotes: 5, comments: 12 },
  },
];

// This hook now instantly returns the dummy data and sets isLoading to false.
export const useStudentDashboardFeed = () => {
  const [posts] = useState(dummyFeed);
  const [isLoading] = useState(false);

  return { posts, isLoading };
};