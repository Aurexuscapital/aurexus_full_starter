'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User } from '@/types/auth';
import { AuthService } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: { email: string; password: string; role: "public" | "developer" | "investor" | "admin"; firstName?: string; lastName?: string; company?: string }) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  hasRole: (role: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await AuthService.getCurrentUser();
        setUser(currentUser);
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await AuthService.login({ email, password });
    setUser(response.user);
  };

  const register = async (userData: { email: string; password: string; role: "public" | "developer" | "investor" | "admin"; firstName?: string; lastName?: string; company?: string }) => {
    const response = await AuthService.register(userData);
    setUser(response);
  };

  const logout = () => {
    AuthService.logout();
    setUser(null);
  };

  const isAuthenticated = !!user;
  const hasRole = (role: string) => AuthService.hasRole(role);

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        register,
        logout,
        isAuthenticated,
        hasRole,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
