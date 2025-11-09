import { useState } from 'react';
import {
  ShoppingBasket,
  Bus,
  Book,
  Gift,
  Ticket,
  Sandwich,
  Apple,
} from 'lucide-react';

// --- Initial Dummy Data ---

const DUMMY_CATEGORIES = [
  {
    id: 'cat-1',
    name: 'Food Stuff (School Shop)',
    icon: ShoppingBasket,
    items: [
      {
        id: 'food-1',
        name: 'Chocolate Bar',
        cost: 150,
        icon: Sandwich,
        stock: 50,
      },
      { id: 'food-2', name: 'Fruit', icon: Apple, cost: 100, stock: 100 },
      {
        id: 'food-3',
        name: 'Free Lunch Voucher',
        icon: Ticket,
        cost: 500,
        stock: 20,
      },
    ],
  },
  {
    id: 'cat-2',
    name: 'Transport',
    icon: Bus,
    items: [
      {
        id: 'trans-1',
        name: 'Single Bus Pass',
        icon: Ticket,
        cost: 300,
        stock: 40,
      },
      {
        id: 'trans-2',
        name: 'Weekly Bus Pass',
        icon: Ticket,
        cost: 1200,
        stock: 10,
      },
    ],
  },
  {
    id: 'cat-3',
    name: 'School Supplies',
    icon: Book,
    items: [
      { id: 'supply-1', name: 'Notebook', icon: Book, cost: 200, stock: 30 },
      { id: 'supply-2', name: 'Pen Set', icon: Gift, cost: 250, stock: 25 },
    ],
  },
];

const DUMMY_USER_XP = 4200;

/**
 * Hook to manage the XP Shop state and logic.
 */
export const useXPShop = () => {
  const [userXP, setUserXP] = useState(DUMMY_USER_XP);
  const [categories, setCategories] = useState(DUMMY_CATEGORIES);
  // isLoading is false by default since it's dummy data
  const [isLoading, setIsLoading] = useState(false);

  /**
   * Handles the logic for redeeming a reward.
   * @param {object} itemToRedeem - The full item object to be redeemed.
   */
  const handleRedeem = (itemToRedeem) => {
    // Check if user can afford it and if it's in stock
    if (userXP < itemToRedeem.cost) {
      console.error('Redemption failed: Not enough XP');
      return false;
    }
    if (itemToRedeem.stock <= 0) {
      console.error('Redemption failed: Item out of stock');
      return false;
    }

    // 1. Subtract XP
    setUserXP((prevXP) => prevXP - itemToRedeem.cost);

    // 2. Decrement stock
    setCategories((prevCategories) =>
      // Map over categories
      prevCategories.map((category) => ({
        ...category,
        // Map over items in each category
        items: category.items.map((item) =>
          // If this is the item we redeemed, update its stock
          item.id === itemToRedeem.id
            ? { ...item, stock: item.stock - 1 }
            : item
        ),
      }))
    );

    console.log(`Successfully redeemed: ${itemToRedeem.name}`);
    return true;
  };

  return {
    userXP,
    categories,
    isLoading,
    handleRedeem,
  };
};