import { useState } from 'react';

// This hook now instantly returns the dummy XP
export const useStudentRewards = () => {
  const [xp] = useState(1250); // Set initial state to the dummy XP

  return { xp };
};