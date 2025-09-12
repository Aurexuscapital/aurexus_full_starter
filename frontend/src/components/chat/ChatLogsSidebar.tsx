"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { 
  Plus, 
  Search, 
  // MoreVertical, 
  Trash2, 
  Clock,
  MessageSquare
} from "lucide-react";

const mockChats = [
  {
    id: "1",
    title: "Brisbane Property Trends",
    preview: "What are the current market trends in Brisbane?",
    timestamp: "30m ago",
    messageCount: 5,
    status: "active"
  },
  {
    id: "2", 
    title: "Investment Strategy",
    preview: "Should I invest in apartments or houses?",
    timestamp: "2h ago",
    messageCount: 8,
    status: "inactive"
  },
  {
    id: "3",
    title: "Suburb Analysis",
    preview: "Tell me about Paddington real estate",
    timestamp: "1d ago", 
    messageCount: 12,
    status: "inactive"
  },
  {
    id: "4",
    title: "Property Valuation",
    preview: "What's the value of my property?",
    timestamp: "2d ago",
    messageCount: 3,
    status: "inactive"
  },
  {
    id: "5",
    title: "Market Forecast",
    preview: "How will interest rates affect prices?",
    timestamp: "3d ago",
    messageCount: 6,
    status: "inactive"
  }
];

export function ChatLogsSidebar() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedChat, setSelectedChat] = useState("1");

  const filteredChats = mockChats.filter(chat =>
    chat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    chat.preview.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Chat History
          </h2>
          <Button
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white h-8 px-3"
          >
            <Plus className="w-4 h-4 mr-1" />
            New Chat
          </Button>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          />
        </div>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-2">
        <div className="space-y-1">
          {filteredChats.map((chat) => (
            <ChatItem
              key={chat.id}
              chat={chat}
              isSelected={selectedChat === chat.id}
              onClick={() => setSelectedChat(chat.id)}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
          Aurexus AI • Real Estate Intelligence
        </div>
      </div>
    </div>
  );
}

function ChatItem({ 
  chat, 
  isSelected, 
  onClick 
}: { 
  chat: typeof mockChats[0]; 
  isSelected: boolean; 
  onClick: () => void;
}) {
  const [showActions, setShowActions] = useState(false);

  return (
    <div
      className={`group relative p-3 rounded-lg cursor-pointer transition-all duration-200 ${
        isSelected
          ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
          : "hover:bg-gray-50 dark:hover:bg-gray-800"
      }`}
      onClick={onClick}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {chat.title}
            </h3>
            {chat.status === "active" && (
              <div className="w-2 h-2 bg-green-500 rounded-full flex-shrink-0" />
            )}
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2 mb-2">
            {chat.preview}
          </p>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3 text-xs text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{chat.timestamp}</span>
              </div>
              <div className="flex items-center space-x-1">
                <MessageSquare className="w-3 h-3" />
                <span>{chat.messageCount} messages</span>
              </div>
            </div>
            {showActions && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={(e) => {
                  e.stopPropagation();
                  // Handle delete
                }}
              >
                <Trash2 className="w-3 h-3 text-red-500" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}