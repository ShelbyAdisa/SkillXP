import React from 'react';
import { useXPShop } from '../../hooks/useXPShop';
import RewardCategory from '../../components/shop/RewardCategory';
import Card from '../../components/shared/Card';
// Import a loading spinner if you have one
// import LoadingSpinner from '../../components/shared/LoadingSpinner';

const XPShop = () => {
  const { userXP, categories, isLoading, handleRedeem } = useXPShop();

  // Handle loading state
  if (isLoading) {
    // return <LoadingSpinner />;
    return <div className="text-white pt-24 text-center">Loading Shop...</div>;
  }

  return (
    // Re-using the layout from StudentDashboard.jsx
    <div className="max-w-7xl mx-auto p-4 pt-25 md:ml-5">
      
      {/* --- Header & XP Total --- */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <h1 className="text-3xl font-bold text-[#D7DADC]">XP Shop</h1>
        <Card className="p-4 md:w-auto w-full">
          <div className="flex items-center gap-3">
            <span className="text-sm text-[#82959B]">Your XP Balance:</span>
            <span className="text-2xl font-bold text-yellow-400">
              {userXP.toLocaleString()} XP
            </span>
          </div>
        </Card>
      </div>

      {/* --- Reward Categories --- */}
      <div className="space-y-8">
        {categories.map((category) => (
          <RewardCategory
            key={category.id}
            category={category}
            userXP={userXP}
            onRedeem={handleRedeem}
          />
        ))}
      </div>
    </div>
  );
};

export default XPShop;