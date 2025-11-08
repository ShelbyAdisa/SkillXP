import { useState } from 'react';

// Define dummy data
const dummyData = [
  { id: 1, slug: 'calculus-101', name: 's/calculus-101' },
  { id: 2, slug: 'python-basics', name: 's/python-basics' },
  { id: 3, slug: 'history-202', name: 's/history-202' },
  { id: 4, slug: 'school-announcements', name: 's/school-announcements' },
];

// This hook now instantly returns the dummy skillspaces
export const useMySkillSpaces = () => {
  const [skillspaces] = useState(dummyData); // Set initial state to dummy data

  return { skillspaces };
};