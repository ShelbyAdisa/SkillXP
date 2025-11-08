import React from 'react';
import Card from '../../shared/Card';
import Leaderboard from '../../Leaderboard'; // Import your existing component

const LeaderboardCard = () => {
  return (
    <Card title="Weekly Leaderboard">
      {/* This just wraps your existing Leaderboard component in a Card.
        You'll need to make sure your Leaderboard component fetches
        its own data or we can pass dummy data to it.
        For now, just embedding it.
      */}
      <Leaderboard />
    </Card>
  );
};

export default LeaderboardCard;