"use client";

import { ChatMessage } from "@/types/chat";
import { formatTime } from "@/lib/utils";
import { Bot, User, Clock, Zap, Database } from "lucide-react";

interface MessageProps {
  message: ChatMessage;
}

export function Message({ message }: MessageProps) {
  const isUser = message.role === "user";
  const isBlocked = message.allowed === false;

  return (
    <div className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
        </div>
      )}

      <div className={`max-w-[80%] ${isUser ? "order-first" : ""}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-blue-600 text-white"
              : isBlocked
              ? "bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 text-amber-800 dark:text-amber-200"
              : "bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white"
          }`}
        >
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </div>

          {!isUser && message.topic && (
            <div className="mt-2 text-xs opacity-70">
              Topic: {message.topic}
            </div>
          )}
        </div>

        <div className={`flex items-center gap-2 mt-1 text-xs text-gray-500 dark:text-gray-400 ${isUser ? "justify-end" : "justify-start"}`}>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            {formatTime(message.timestamp)}
          </div>

          {!isUser && message.provider && (
            <div className="flex items-center gap-1">
              <Database className="w-3 h-3" />
              {message.provider}
            </div>
          )}

          {!isUser && message.latency_ms && (
            <div className="flex items-center gap-1">
              <Zap className="w-3 h-3" />
              {message.latency_ms}ms
            </div>
          )}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </div>
        </div>
      )}
    </div>
  );
}