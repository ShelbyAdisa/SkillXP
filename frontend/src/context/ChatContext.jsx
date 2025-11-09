import React, { createContext, useContext, useState } from 'react';

const ChatContext = createContext();

export const useChat = () => useContext(ChatContext);

export const ChatProvider = ({ children }) => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  
  // In the future, you can add state for active conversation
  // const [activeConversationId, setActiveConversationId] = useState(null);

  const toggleChat = () => {
    setIsChatOpen(prev => !prev);
  };

  // You can add more functions here, like:
  // const openChatWithUser = (userId) => {
  //   setActiveConversationId(userId);
  //   setIsChatOpen(true);
  // };

  const value = {
    isChatOpen,
    toggleChat,
    // openChatWithUser,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};