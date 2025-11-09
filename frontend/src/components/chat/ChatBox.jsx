import React, { useState } from 'react';
import { X, ChevronLeft, Plus, Send, Search } from 'lucide-react';
import UserAvatar from '../shared/UserAvatar'; // Adjust path if needed
import { useChat } from '../../context/ChatContext'; // Adjust path if needed

// --- FIX: DUMMY DATA ---
// Added avatar URLs
const dummyConversations = [
  { id: 'user1', name: 'Jane Doe', avatar: 'https://placehold.co/100x100/7B96EB/FFFFFF/png', lastMessage: 'Hey, did you finish the project?' },
  { id: 'user2', name: 'John Smith', avatar: 'https://placehold.co/100x100/FFB84C/FFFFFF/png', lastMessage: 'See you in class.' },
  { id: 'user3', name: 'Project Group 1', avatar: 'https://placehold.co/100x100/96E072/FFFFFF/png', lastMessage: 'Let\'s meet at 4 PM.' },
];
// -----------------

const dummyMessages = {
  'user1': [
    { id: 'm1', sender: 'other', text: 'Hey, did you finish the project?' },
    { id: 'm2', sender: 'self', text: 'Almost! Just need to fix a bug.' },
    { id: 'm3', sender: 'other', text: 'Great! Let me know if you need help.' },
  ],
  'user2': [
    { id: 'm4', sender: 'other', text: 'See you in class.' },
  ],
  'user3': [
    { id: 'm5', sender: 'other', text: 'Let\'s meet at 4 PM.' },
    { id: 'm6', sender: 'self', text: 'Sounds good to me.' },
    { id: 'm7', sender: 'other', text: 'I\'ll book the study room.' },
  ],
};

export default function ChatBox() {
  const { isChatOpen, toggleChat } = useChat();
  const [activeView, setActiveView] = useState('list'); // 'list', 'chat', 'new'
  const [selectedUser, setSelectedUser] = useState(null); // { id, name, avatar }

  if (!isChatOpen) {
    return null;
  }

  const handleSelectUser = (user) => {
    setSelectedUser(user);
    setActiveView('chat');
  };

  const handleBack = () => {
    setActiveView('list');
    setSelectedUser(null);
  };
  
  const handleNewMessage = () => {
    setActiveView('new');
    setSelectedUser(null);
  };

  const getHeader = () => {
    switch (activeView) {
      case 'chat':
        return (
          <div className="flex items-center gap-2">
            {/* --- FIX: Added cursor-pointer --- */}
            <button onClick={handleBack} className="p-1 hover:bg-[#223237] rounded-full cursor-pointer">
              <ChevronLeft className="w-5 h-5" />
            </button>
            {/* --- FIX: Pass avatar src --- */}
            <UserAvatar src={selectedUser?.avatar} className="w-7 h-7" />
            <span className="font-semibold">{selectedUser?.name}</span>
          </div>
        );
      case 'new':
         return (
          <div className="flex items-center gap-2">
            {/* --- FIX: Added cursor-pointer --- */}
            <button onClick={handleBack} className="p-1 hover:bg-[#223237] rounded-full cursor-pointer">
              <ChevronLeft className="w-5 h-5" />
            </button>
            <span className="font-semibold">New Message</span>
          </div>
        );
      case 'list':
      default:
        return <span className="font-semibold">Messages</span>;
    }
  };
  
  const getBody = () => {
     switch (activeView) {
      case 'chat':
        const messages = dummyMessages[selectedUser.id] || [];
        return (
          <>
            <div className="flex-1 p-4 space-y-3 overflow-y-auto">
              {messages.map(msg => (
                <div key={msg.id} className={`flex ${msg.sender === 'self' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`px-3 py-2 rounded-lg max-w-[80%] ${msg.sender === 'self' ? 'bg-blue-600 text-white' : 'bg-[#223237] text-[#D7DADC]'}`}>
                    {msg.text}
                  </div>
                </div>
              ))}
            </div>
            <div className="p-2 border-t border-[#223237] flex items-center gap-2">
              <input type="text" placeholder="Type a message..." className="flex-1 bg-[#131F23] text-sm text-[#D7DADC] placeholder-[#82959B] outline-none rounded-full px-4 py-2" />
              {/* --- FIX: Added cursor-pointer --- */}
              <button className="p-2 text-blue-400 hover:text-blue-300 cursor-pointer">
                <Send className="w-5 h-5" />
              </button>
            </div>
          </>
        );
      case 'new':
        return (
          <div className="flex-1 flex flex-col">
            <div className="p-2 border-b border-[#223237]">
              <div className="flex items-center bg-[#131F23] rounded-full px-3 py-1.5">
                <Search className="w-4 h-4 text-[#82959B]" />
                <input type="text" placeholder="Search for students..." className="ml-2 bg-transparent text-sm text-[#D7DADC] placeholder-[#82959B] outline-none w-full" />
              </div>
            </div>
            <div className="flex-1 p-4 text-center text-sm text-[#82959B]">
              Start typing a name to find a student.
            </div>
          </div>
        );
      case 'list':
      default:
        return (
          <div className="flex-1 overflow-y-auto">
            {dummyConversations.map(convo => (
              // --- FIX: Added cursor-pointer ---
              <button key={convo.id} onClick={() => handleSelectUser(convo)} className="w-full flex items-center gap-3 p-3 text-left hover:bg-[#131F23] cursor-pointer">
                {/* --- FIX: Pass avatar src --- */}
                <UserAvatar src={convo.avatar} className="w-10 h-10" />
                <div className="flex-1 overflow-hidden">
                  <span className="block text-sm font-medium text-[#D7DADC]">{convo.name}</span>
                  <span className="block text-sm text-[#82959B] truncate">{convo.lastMessage}</span>
                </div>
              </button>
            ))}
          </div>
        );
    }
  }

  return (
    <div className="fixed bottom-0 right-4 z-[60] w-80 h-[28rem] bg-[#0F1A1C] border border-[#223237] rounded-t-lg shadow-2xl flex flex-col text-[#D7DADC]">
      {/* Header */}
      <div className="h-14 p-3 flex items-center justify-between border-b border-[#223237]">
        <div className="flex-1">{getHeader()}</div>
        <div className="flex items-center gap-1">
           {activeView === 'list' && (
            // --- FIX: Added cursor-pointer ---
            <button onClick={handleNewMessage} className="p-2 hover:bg-[#131F23] rounded-full cursor-pointer">
              <Plus className="w-5 h-5" />
            </button>
           )}
          {/* --- FIX: Added cursor-pointer --- */}
          <button onClick={toggleChat} className="p-2 hover:bg-[#131F23] rounded-full cursor-pointer">
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>
      
      {/* Body */}
      {getBody()}
    </div>
  );
}