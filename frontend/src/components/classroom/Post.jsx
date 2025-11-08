import React from 'react';
import {
  ArrowUp, ArrowDown, MessageSquare, Share2, Bookmark, MoreHorizontal
} from 'lucide-react';

export default function Post({ post, handleVote }) {
  return (
    <div className="bg-[#0F1A1C] border border-[#223237] hover:border-[#2d3f45] rounded-xl overflow-hidden transition-colors">
      {/* Post Header */}
      <div className="px-4 pt-3 pb-2 flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0">
          <img src={post.authorAvatar} className="w-8 h-8 rounded-full shrink-0" alt={`${post.author} avatar`} />
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-medium text-[#B8C5C9] truncate">Class: LearnProgramming</span>
              <span className="text-[#82959B]">•</span>
              <span className="text-xs text-[#82959B]">{post.time}</span>
            </div>
            <div className="text-xs text-[#82959B] truncate">u/{post.author}</div>
          </div>
        </div>
        <button className="p-1 hover:bg-[#131F23] rounded-lg shrink-0">
          <MoreHorizontal className="w-5 h-5 text-[#82959B]" />
        </button>
      </div>

      {/* Post Content */}
      <div className="px-4 pb-3">
        <h2 className="text-[#D7DADC] text-lg font-semibold leading-snug mb-2">{post.title}</h2>
        
        {post.flair && (
          <div className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium mb-3 ${post.flair.color}`}>
            <span>{post.flair.emoji}</span>
            <span>{post.flair.text}</span>
          </div>
        )}
        
        <p className="text-[#B8C5C9] text-sm leading-relaxed line-clamp-3">{post.content}</p>
      </div>

      {/* Post Image */}
      {post.image && (
        <div className="px-4 pb-3">
          <img src={post.image} className="w-full rounded-lg" alt="Post content" />
        </div>
      )}

      {/* Action Bar */}
      <div className="px-3 pb-2 flex items-center gap-1">
        <button 
          onClick={() => handleVote(post.id, 1)}
          className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23] transition-colors ${
            post.userVote === 1 ? 'bg-[#131F23]' : ''
          }`}
        >
          <ArrowUp className={`w-5 h-5 ${post.userVote === 1 ? 'text-orange-500 fill-orange-500' : 'text-[#82959B]'}`} />
          <span className={`text-xs font-bold ${
            post.userVote === 1 ? 'text-orange-500' : 
            post.userVote === -1 ? 'text-blue-500' : 
            'text-[#B8C5C9]'
          }`}>
            {post.votes >= 1000 ? `${(post.votes / 1000).toFixed(1)}k` : post.votes}
          </span>
          <ArrowDown 
            onClick={(e) => {
              e.stopPropagation();
              handleVote(post.id, -1);
            }}
            className={`w-5 h-5 ${post.userVote === -1 ? 'text-blue-500 fill-blue-500' : 'text-[#82959B]'}`} 
          />
        </button>
        <button className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23]">
          <MessageSquare className="w-5 h-5 text-[#82959B]" />
          <span className="text-xs font-bold text-[#B8C5C9]">{post.comments}</span>
        </button>
        <button className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23]">
          <Share2 className="w-5 h-5 text-[#82959B]" />
          <span className="text-xs font-bold text-[#B8C5C9]">Share</span>
        </button>
        <button className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-full hover:bg-[#131F23] ml-auto">
          <Bookmark className="w-5 h-5 text-[#82959B]" />
        </button>
      </div>
    </div>
  );
}