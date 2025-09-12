"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Message } from "@/components/chat/Message";
import { Send, Mic, Plus } from "lucide-react";
import { ChatMessage } from "@/types/chat";

export function MainChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
      allowed: true,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "I'm here to help you with real estate insights and analysis. What would you like to know about property trends, valuations, or investment strategies?",
        timestamp: new Date(),
        allowed: true,
        topic: "real_estate",
        provider: "mock",
        latency_ms: 150,
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-white dark:bg-gray-900">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6">
              <span className="text-white font-bold text-2xl">A</span>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">
              Welcome to Aurexus
            </h2>
            <p className="text-gray-600 dark:text-gray-400 max-w-md mb-8">
              Your intelligent real estate assistant. Ask me about market trends, property valuations, investment strategies, and more.
            </p>
            
            {/* Quick Start Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-2xl w-full">
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Property Valuation</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Get instant property value estimates</p>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Market Analysis</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Understand local market trends</p>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Investment Strategy</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Optimize your real estate portfolio</p>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-colors cursor-pointer">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Suburb Insights</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400">Deep dive into neighborhood data</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <Message key={message.id} message={message} />
            ))}
            {isLoading && (
              <div className="flex items-center space-x-2 text-gray-500 dark:text-gray-400">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }} />
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }} />
                <span className="ml-2 text-sm">Thinking...</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask anything about real estate..."
                className="w-full px-4 py-3 pr-12 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 min-h-[44px] max-h-32"
                rows={1}
                style={{
                  height: "auto",
                  minHeight: "44px",
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement;
                  target.style.height = "auto";
                  target.style.height = Math.min(target.scrollHeight, 128) + "px";
                }}
              />
              <Button
                variant="ghost"
                size="sm"
                className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <Mic className="w-4 h-4" />
              </Button>
            </div>
            <Button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white h-11 w-11 p-0 rounded-xl transition-all duration-200"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="flex items-center justify-between mt-3 text-xs text-gray-500 dark:text-gray-400">
            <div className="flex items-center space-x-4">
              <span>Press Enter to send, Shift+Enter for new line</span>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                className="text-xs h-8 px-3 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
              >
                <Plus className="w-3 h-3 mr-1" />
                New Chat
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}