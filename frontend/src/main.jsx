import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'   // ✅ import your provider
import { ThemeProvider } from './context/ThemeContext.jsx';
import { ChatProvider } from './context/ChatContext';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider> 
      <ChatProvider>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </ChatProvider>
    </AuthProvider>
  </StrictMode>,
)
