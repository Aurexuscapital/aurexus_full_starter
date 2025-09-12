'use client';

import { useState } from "react";
import { Send, Heart, Zap, TrendingUp, DollarSign, Brain, Settings } from "lucide-react";

interface PersonalityInfo {
  name: string;
  age: number;
  personality_type: string;
  gender: string;
  description: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  kind?: string;
  meters?: Record<string, unknown>;
  personality_info?: PersonalityInfo;
  available_apps?: Record<string, unknown>;
}

interface LifestyleMeters {
  burnout: { score: number; status: string; color: string; message: string };
  stress: { score: number; status: string; color: string; message: string };
  energy: { score: number; status: string; color: string; message: string };
  mood: { score: number; status: string; color: string; message: string };
  financial_health: { score: number; status: string; color: string; message: string };
  life_progress: { score: number; status: string; color: string; message: string };
  body_health: { score: number; status: string; color: string; message: string };
}

export default function HomePage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showMeters, setShowMeters] = useState(false);
  const [meters, setMeters] = useState<LifestyleMeters | null>(null);
  const [aiPersonality, setAiPersonality] = useState<PersonalityInfo | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/ai-enhanced/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          handle: "lifestyle_user",
          text: input.trim()
        })
      });

      const data = await response.json();
      
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.message || "I'm here to help you with your lifestyle goals!",
        kind: data.kind,
        meters: data.meters,
        personality_info: data.personality_info,
        available_apps: data.available_apps
      };

      setMessages(prev => [...prev, aiMessage]);
      
      // Update meters if provided
      if (data.meters) {
        setMeters(data.meters);
        setShowMeters(true);
      }
      
      // Update AI personality if provided
      if (data.personality_info) {
        setAiPersonality(data.personality_info);
      }
      
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "Sorry, I'm having trouble connecting right now. Please try again later."
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getMeterColor = (color: string) => {
    switch (color) {
      case 'green': return 'bg-green-500';
      case 'yellow': return 'bg-yellow-500';
      case 'orange': return 'bg-orange-500';
      case 'red': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getMeterIcon = (meterName: string) => {
    switch (meterName) {
      case 'burnout': return <Brain className="w-4 h-4" />;
      case 'stress': return <Heart className="w-4 h-4" />;
      case 'energy': return <Zap className="w-4 h-4" />;
      case 'mood': return <Heart className="w-4 h-4" />;
      case 'financial_health': return <DollarSign className="w-4 h-4" />;
      case 'life_progress': return <TrendingUp className="w-4 h-4" />;
      case 'body_health': return <Zap className="w-4 h-4" />;
      default: return <Settings className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-800 text-white">
      {/* Header */}
      <div className="text-center py-8 px-4">
        <h1 className="text-5xl font-light tracking-wider mb-4 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
          AUREXUS
        </h1>
        <h2 className="text-2xl font-medium mb-2">Lifestyle AI Companion</h2>
        <p className="text-gray-400 text-sm">
          Your personal AI that knows you better than you know yourself
        </p>
        {aiPersonality && (
          <div className="mt-4 text-sm text-gray-300">
            Meet {aiPersonality.name}, your {aiPersonality.age}-year-old {aiPersonality.personality_type} AI companion
          </div>
        )}
      </div>

      <div className="flex flex-col lg:flex-row max-w-7xl mx-auto px-4 gap-8">
        {/* Main Chat */}
        <div className="flex-1 max-w-2xl mx-auto lg:mx-0">
          {/* Messages */}
          <div className="space-y-6 mb-8">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 text-sm py-12">
                <div className="mb-4">
                  <Brain className="w-12 h-12 mx-auto text-gray-600 mb-4" />
                  <p className="text-lg mb-2">Welcome to your Lifestyle AI Companion!</p>
                  <p className="text-sm">Try asking:</p>
                  <div className="mt-4 space-y-2">
                    <div className="text-xs bg-gray-800 rounded-lg px-3 py-2 inline-block mr-2">
                      &ldquo;Tell me about your day&rdquo;
                    </div>
                    <div className="text-xs bg-gray-800 rounded-lg px-3 py-2 inline-block mr-2">
                      &ldquo;Show me my lifestyle meters&rdquo;
                    </div>
                    <div className="text-xs bg-gray-800 rounded-lg px-3 py-2 inline-block mr-2">
                      &ldquo;Who are you?&rdquo;
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-3 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-white text-black'
                        : 'bg-gray-800 text-white border border-gray-700'
                    }`}
                  >
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    {message.kind && (
                      <div className="mt-2 text-xs text-gray-400">
                        Intent: {message.kind}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 text-white px-4 py-3 rounded-2xl border border-gray-700">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" />
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                    <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="w-full">
            <div className="flex items-center bg-gray-900 rounded-2xl px-4 py-3 border border-gray-700">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Share about your day, ask for insights, or check your meters..."
                className="flex-1 bg-transparent text-white placeholder-gray-400 focus:outline-none text-sm"
                disabled={isLoading}
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="ml-3 bg-white text-black hover:bg-gray-200 disabled:bg-gray-600 disabled:text-gray-400 h-8 w-8 p-0 rounded-full flex items-center justify-center transition-colors"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Lifestyle Meters Sidebar */}
        {showMeters && meters && (
          <div className="w-full lg:w-80 space-y-4">
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2" />
                Your Lifestyle Health
              </h3>
              <div className="space-y-4">
                {Object.entries(meters).map(([key, meter]) => (
                  <div key={key} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getMeterIcon(key)}
                        <span className="text-sm font-medium capitalize">
                          {key.replace('_', ' ')}
                        </span>
                      </div>
                      <span className="text-sm font-bold">{meter.score}/100</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${getMeterColor(meter.color)}`}
                        style={{ width: `${meter.score}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-400">{meter.message}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-900 rounded-2xl p-6 border border-gray-700">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={() => setInput("Tell me about your day")}
                  className="w-full text-left px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                >
                  📅 Daily Check-in
                </button>
                <button
                  onClick={() => setInput("Show me my lifestyle meters")}
                  className="w-full text-left px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                >
                  📊 View Meters
                </button>
                <button
                  onClick={() => setInput("Connect my apps")}
                  className="w-full text-left px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                >
                  🔗 App Integration
                </button>
                <button
                  onClick={() => setInput("Change my AI personality")}
                  className="w-full text-left px-3 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
                >
                  🤖 Personality Settings
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}