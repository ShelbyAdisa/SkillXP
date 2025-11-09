import React from 'react';

const RewardItem = ({ item, userXP, onRedeem }) => {
  const canAfford = userXP >= item.cost;
  const isOutOfStock = item.stock <= 0;
  
  // The icon component is passed directly in the item object
  const ItemIcon = item.icon;

  return (
    <div
      className={`
      bg-[#0F1A1C] rounded-lg border border-[#223237] p-4 
      flex flex-col items-center text-center
      ${
        !canAfford || isOutOfStock
          ? 'opacity-50'
          : 'hover:border-[#2d3f45] transition-shadow duration-200'
      }
    `}
    >
      <ItemIcon className="w-12 h-12 text-cyan-400 mb-3" />
      <h4 className="text-md font-semibold text-[#D7DADC]">{item.name}</h4>
      <span className="text-lg font-bold text-yellow-400 my-2">
        {item.cost} XP
      </span>
      <p className="text-xs text-[#82959B] mb-4">
        {isOutOfStock ? 'Out of Stock' : `${item.stock} remaining`}
      </p>

      {/* Assuming you have a Button component, otherwise style a <button> */}
      <button
        onClick={() => onRedeem(item)}
        disabled={!canAfford || isOutOfStock}
        className={`
        w-full py-2 px-4 rounded-md text-sm font-semibold transition-colors
        ${
          canAfford && !isOutOfStock
            ? 'bg-cyan-600 text-white hover:bg-cyan-500'
            : 'bg-gray-700 text-gray-400 cursor-not-allowed'
        }
      `}
      >
        {isOutOfStock ? 'Out of Stock' : !canAfford ? 'Not Enough XP' : 'Redeem'}
      </button>
    </div>
  );
};

export default RewardItem;