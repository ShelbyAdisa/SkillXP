import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

// Utility function to get user from local storage
const getLocalUser = () => {
  const userString = localStorage.getItem('skillxp_user');
  return userString ? JSON.parse(userString) : null;
};

// Utility function to generate a simple unique ID (replaces Firebase UID)
const generateUID = () => Math.random().toString(36).substring(2, 15);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(getLocalUser());
  const [loading, setLoading] = useState(true);
  // isAuthReady is always true after initial check since it's local storage
  const [isAuthReady, setIsAuthReady] = useState(true); 

  useEffect(() => {
    // Simulate a brief loading period for local storage check
    setTimeout(() => {
      setUser(getLocalUser());
      setLoading(false);
    }, 100);
  }, []);

  const signup = async (email, password, firstName, lastName, role) => {
    // Simulate user creation by checking for existing user by email
    // NOTE: For security, a real app would use a server/database for this.
    if (localStorage.getItem(`user_${email}`)) {
      throw new Error("Email already in use. Please try logging in.");
    }

    const newUser = {
      uid: generateUID(),
      email,
      password, // Storing password only for local storage simulation/validation
      role: role || 'STUDENT',
      first_name: firstName,
      last_name: lastName,
    };
    
    // Store user data in local storage
    localStorage.setItem('skillxp_user', JSON.stringify(newUser));
    localStorage.setItem(`user_${email}`, JSON.stringify(newUser)); // Index by email for lookup

    setUser(newUser);
  };

  const login = async (email, password) => {
    const storedUserString = localStorage.getItem(`user_${email}`);
    
    if (!storedUserString) {
      throw new Error("User not found.");
    }

    const storedUser = JSON.parse(storedUserString);
    
    // Simulate password validation
    if (storedUser.password !== password) {
      throw new Error("Invalid password.");
    }
    
    // Log the user in
    localStorage.setItem('skillxp_user', storedUserString);
    setUser(storedUser);
  };

  const logout = async () => {
    localStorage.removeItem('skillxp_user');
    setUser(null);
  };

  const value = {
    user,
    loading,
    isAuthReady,
    signup,
    login,
    logout,
  };

  return <AuthContext.Provider value={!loading ? value : { user: null, loading: true, isAuthReady: false, signup, login, logout }}>{children}</AuthContext.Provider>;
};