import React from 'react';
import Card from '../shared/Card'; // Uses your existing Card component
import RewardItem from './RewardItem';

const RewardCategory = ({ category, userXP, onRedeem }) => {
  const CategoryIcon = category.icon;

  return (
    <Card
      title={category.name}
      action={<CategoryIcon className="w-6 h-6 text-[#82959B]" />}
    >
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
        {category.items.map((item) => (
          <RewardItem
            key={item.id}
            item={item}
            userXP={userXP}
            onRedeem={onRedeem}
          />
        ))}
      </div>
    </Card>
  );
};

export default RewardCategory;