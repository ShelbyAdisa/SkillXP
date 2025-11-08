import React from 'react';
import UserAvatar from '../shared/UserAvatar';
import Post from './Post';
import { ChevronDown, Check } from 'lucide-react';

// Sub-component: CreatePostBar
// (You can move this to its own file if you want it even more modular)
const CreatePostBar = () => (
  <div className="bg-[#0F1A1C] border border-[#223237] rounded-lg p-3 mb-4 flex items-center gap-3">
    <UserAvatar className="w-10 h-10 rounded-full" />
    <input 
      type="text"
      placeholder="Create Post"
      className="flex-1 bg-[#131F23] border border-[#223237] hover:border-[#2d3f45] hover:bg-[#0F1A1C] rounded px-4 py-2 text-sm text-[#D7DADC] placeholder-[#82959B] outline-none cursor-pointer"
    />
  </div>
);

// Sub-component: SortDropdown
// (You can also move this to its own file)
const SortDropdown = ({
  sortBy,
  setSortBy,
  isSortOpen,
  setIsSortOpen,
  sortOptions
}) => {
  const CurrentSortIcon = sortOptions.find(o => o.name === sortBy)?.icon;

  return (
    <div className="relative mb-4">
      <button
        onClick={() => setIsSortOpen(!isSortOpen)}
        className="bg-[#0F1A1C] border border-[#223237] rounded-lg p-2 flex items-center w-full hover:border-[#2d3f45] text-left"
      >
        <CurrentSortIcon className="w-5 h-5 text-[#82959B] shrink-0" />
        <span className="text-sm font-medium text-[#D7DADC] capitalize ml-2">
          {sortBy}
        </span>
        <ChevronDown className="w-5 h-5 text-[#82959B] ml-auto shrink-0" />
      </button>

      {isSortOpen && (
        <div className="absolute top-full left-0 right-0 z-10 mt-1 bg-[#0F1A1C] border border-[#223237] rounded-lg overflow-hidden shadow-lg">
          {sortOptions.map(({ name, icon: Icon }) => (
            <button
              key={name}
              onClick={() => {
                setSortBy(name);
                setIsSortOpen(false);
              }}
              className={`flex items-center w-full gap-2 px-3 py-2 text-left text-sm transition-colors ${
                sortBy === name
                  ? 'bg-[#223237] text-[#D7DADC]'
                  : 'text-[#82959B] hover:bg-[#131F23]'
              }`}
            >
              <Icon className="w-5 h-5 shrink-0" />
              <span>{name}</span>
              {sortBy === name && <Check className="w-5 h-5 ml-auto shrink-0" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// Main Feed Component
export default function Feed({
  sortedPosts,
  handleVote,
  sortBy,
  setSortBy,
  isSortOpen,
  setIsSortOpen,
  sortOptions
}) {
  return (
    <div className="flex-1 max-w-[640px]">
      <CreatePostBar />
      
      <SortDropdown
        sortBy={sortBy}
        setSortBy={setSortBy}
        isSortOpen={isSortOpen}
        setIsSortOpen={setIsSortOpen}
        sortOptions={sortOptions}
      />

      <div className="space-y-3">
        {sortedPosts.map(post => (
          <Post key={post.id} post={post} handleVote={handleVote} />
        ))}
      </div>
    </div>
  );
}