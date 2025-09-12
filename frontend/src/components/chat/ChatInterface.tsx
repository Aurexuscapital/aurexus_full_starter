"use client";

import { useState, useEffect, useRef } from "react";
import { ChatMessage } from "@/types/chat";
import { Message } from "./Message";
import { ChatInput } from "./ChatInput";
import { ProviderSelector } from "./ProviderSelector";
import { sendMessage, switchProvider, getSelectedProvider } from "@/lib/api";
import { AlertCircle, RefreshCw } from "lucide-react";

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState(getSelectedProvider());
  const [sessionId] = useState(() => crypto.randomUUID());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Welcome to Aurexus Public AI! I can help you with:\n\n• Macro trends in real estate\n• Suburb analytics and market data\n• Housing market insights\n• Real estate investment strategies\n• GTM strategies for real estate\n• Cap raise basics\n\nWhat would you like to know?",
        timestamp: new Date(),
        topic: "welcome",
        allowed: true,
        provider: "system",
      },
    ]);
  }, []);

  const handleSendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await sendMessage(content, sessionId, true, false);
      
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        timestamp: new Date(),
        topic: response.topic,
        allowed: response.allowed,
        provider: selectedProvider,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to send message");
      
      const errorMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "I'm sorry, I'm having trouble connecting right now. Please try again later.",
        timestamp: new Date(),
        topic: "error",
        allowed: false,
        provider: selectedProvider,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProviderChange = async (provider: string) => {
    setSelectedProvider(provider);
    await switchProvider(provider);
  };

  const handleRetry = () => {
    setError(null);
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">Aurexus Public AI</h1>
          <p className="text-sm text-gray-500">Real Estate Intelligence Platform</p>
        </div>
        <ProviderSelector
          selectedProvider={selectedProvider}
          onProviderChange={handleProviderChange}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}
        
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
              <div className="text-gray-500">Thinking...</div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Error Banner */}
      {error && (
        <div className="mx-4 mb-2 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-red-600" />
          <span className="text-sm text-red-800">{error}</span>
          <button
            onClick={handleRetry}
            className="ml-auto flex items-center gap-1 text-sm text-red-600 hover:text-red-800"
          >
            <RefreshCw className="w-3 h-3" />
            Retry
          </button>
        </div>
      )}

      {/* Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        disabled={!!error}
      />
    </div>
  );
}
