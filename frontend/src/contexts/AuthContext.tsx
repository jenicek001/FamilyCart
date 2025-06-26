"use client";

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import apiClient from '@/lib/api';
import { useRouter } from 'next/navigation';
import { User } from '@/types';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  loading: boolean;
  fetchUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      
      // Set the Authorization header for all axios requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`;
      console.log("Initialized with token:", storedToken);
      
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchUser = async () => {
    try {
      const { data } = await apiClient.get('/api/v1/users/me');
      // Add full_name derived from first_name and last_name
      const userData = {
        ...data,
        full_name: data.first_name && data.last_name 
          ? `${data.first_name} ${data.last_name}`
          : data.first_name || data.last_name || ''
      };
      setUser(userData);
    } catch (error: any) {
      console.error('Failed to fetch user', error);
      
      // Handle token expiration specifically
      if (error.response?.status === 401) {
        console.warn('User fetch failed with 401 - token likely expired');
        logout(); // This will clear token and redirect
      } else {
        // For other errors, still logout to be safe
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  const login = (newToken: string) => {
    // Ensure the token is saved correctly and in the right format
    localStorage.setItem('token', newToken);
    setToken(newToken);
    
    // This is captured by apiClient interceptor automatically
    console.log("Token stored:", newToken);
    
    fetchUser();
    router.push('/dashboard');
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    // No need to manually delete headers - apiClient will handle this
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading, fetchUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
