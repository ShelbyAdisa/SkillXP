import './index.css'
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import { AuthProvider } from './context/AuthContext.jsx'   // ✅ import your provider

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>   {/* ✅ wrap your app here */}
      <App />
    </AuthProvider>
  </StrictMode>,
)
