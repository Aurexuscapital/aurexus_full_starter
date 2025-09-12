"use client";

import { useState } from "react";
import { PROVIDERS } from "@/types/chat";
import { ChevronDown, Check } from "lucide-react";

interface ProviderSelectorProps {
  selectedProvider: string;
  onProviderChange: (provider: string) => void;
}

export function ProviderSelector({ selectedProvider, onProviderChange }: ProviderSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const currentProvider = PROVIDERS.find(p => p.id === selectedProvider) || PROVIDERS[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
      >
        <span className="text-lg">{currentProvider.icon}</span>
        <span className="font-medium">{currentProvider.name}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-64 overflow-y-auto">
          {PROVIDERS.map((provider) => (
            <button
              key={provider.id}
              onClick={() => {
                onProviderChange(provider.id);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 text-left hover:bg-gray-50 transition-colors ${
                provider.status === "unavailable" ? "opacity-50 cursor-not-allowed" : ""
              }`}
              disabled={provider.status === "unavailable"}
            >
              <span className="text-lg">{provider.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="font-medium">{provider.name}</div>
                <div className="text-xs text-gray-500 truncate">{provider.description}</div>
              </div>
              {selectedProvider === provider.id && (
                <Check className="w-4 h-4 text-blue-600" />
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
