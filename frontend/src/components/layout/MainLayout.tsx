"use client";

import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { ThemeToggle } from "@/components/ui/theme-toggle";
import { Button } from "@/components/ui/button";
import { ChatLogsSidebar } from "@/components/chat/ChatLogsSidebar";
import { FeatureDashboard } from "@/components/dashboard/FeatureDashboard";
import { MainChatInterface } from "@/components/chat/MainChatInterface";
import { LoginForm } from "@/components/auth/LoginForm";
import { RegisterForm } from "@/components/auth/RegisterForm";
import { Menu, X, Settings, User } from "lucide-react";

export function MainLayout() {
  const { user, isAuthenticated } = useAuth();
  const [showAuth, setShowAuth] = useState(false);
  const [authMode, setAuthMode] = useState<"login" | "register">("login");
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  const handleAuth = (mode: "login" | "register") => {
    setAuthMode(mode);
    setShowAuth(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <span className="text-xl font-semibold text-gray-900 dark:text-white">
                Aurexus
              </span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-4">
              <Button
                variant="ghost"
                className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
              >
                <Settings className="w-4 h-4 mr-2" />
                Features
              </Button>
              
              <ThemeToggle />
              
              {isAuthenticated ? (
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
                    <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                  </div>
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {user?.email}
                  </span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <Button
                    variant="ghost"
                    onClick={() => handleAuth("login")}
                    className="text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                  >
                    Sign In
                  </Button>
                  <Button
                    onClick={() => handleAuth("register")}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    Get Started
                  </Button>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowMobileMenu(!showMobileMenu)}
              >
                {showMobileMenu ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Desktop Sidebar */}
        <div className="hidden lg:block w-80 border-r border-gray-200/50 dark:border-gray-700/50">
          <div className="h-full flex flex-col">
            <ChatLogsSidebar />
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 flex">
            {/* Feature Dashboard - Desktop */}
            <div className="hidden xl:block w-80 border-r border-gray-200/50 dark:border-gray-700/50">
              <FeatureDashboard />
            </div>

            {/* Chat Interface */}
            <div className="flex-1 flex flex-col">
              <MainChatInterface />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {showMobileMenu && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/50" onClick={() => setShowMobileMenu(false)} />
          <div className="fixed right-0 top-0 h-full w-80 bg-white dark:bg-gray-900 shadow-xl">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold">Menu</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowMobileMenu(false)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>
              
              <div className="space-y-4">
                <FeatureDashboard />
                <ChatLogsSidebar />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      {showAuth && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/50" onClick={() => setShowAuth(false)} />
          <div className="relative bg-white dark:bg-gray-900 rounded-2xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-semibold text-gray-900 dark:text-white">
                  {authMode === "login" ? "Welcome back" : "Create account"}
                </h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowAuth(false)}
                >
                  <X className="w-5 h-5" />
                </Button>
              </div>

              {authMode === "login" ? (
                <LoginForm onSuccess={() => setShowAuth(false)} />
              ) : (
                <RegisterForm onSuccess={() => setShowAuth(false)} />
              )}

              <div className="mt-6 text-center">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {authMode === "login" ? "Don't have an account?" : "Already have an account?"}
                </p>
                <Button
                  variant="link"
                  onClick={() => setAuthMode(authMode === "login" ? "register" : "login")}
                  className="text-blue-600 hover:text-blue-700"
                >
                  {authMode === "login" ? "Sign up" : "Sign in"}
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}