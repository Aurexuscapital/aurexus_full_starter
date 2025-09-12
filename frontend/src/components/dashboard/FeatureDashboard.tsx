"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { 
  House, 
  Calculator, 
  TrendingUp, 
  MapPin, 
  FileText, 
  Settings, 
  Brain,
  Search
} from "lucide-react";

const features = [
  {
    id: "valuation",
    title: "Property Valuation",
    description: "Instant property value estimates with confidence scores",
    icon: House,
    status: "available",
    category: "free"
  },
  {
    id: "roi-simulator",
    title: "ROI Simulator",
    description: "Calculate renovation returns and investment potential",
    icon: Calculator,
    status: "available",
    category: "free"
  },
  {
    id: "market-analysis",
    title: "Market Analysis",
    description: "Comprehensive market trends and insights",
    icon: TrendingUp,
    status: "available",
    category: "free"
  },
  {
    id: "neighborhood-radar",
    title: "Neighborhood Radar",
    description: "Track investment opportunities by location",
    icon: MapPin,
    status: "available",
    category: "free"
  },
  {
    id: "reports",
    title: "Market Reports",
    description: "Monthly market insights and analysis",
    icon: FileText,
    status: "available",
    category: "free"
  },
  {
    id: "scenario-simulator",
    title: "Scenario Simulator",
    description: "Multi-property investment scenarios",
    icon: Settings,
    status: "coming-soon",
    category: "premium"
  },
  {
    id: "due-diligence",
    title: "Due Diligence",
    description: "Comprehensive investment analysis reports",
    icon: Brain,
    status: "coming-soon",
    category: "premium"
  }
];

export function FeatureDashboard() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<"all" | "free" | "premium">("all");

  const filteredFeatures = features.filter(feature => {
    const matchesSearch = feature.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         feature.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === "all" || feature.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const freeFeatures = filteredFeatures.filter(f => f.category === "free");
  const premiumFeatures = filteredFeatures.filter(f => f.category === "premium");

  return (
    <div className="h-full flex flex-col bg-white dark:bg-gray-900">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search features..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
          />
        </div>
        
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
          <Button
            variant={selectedCategory === "all" ? "default" : "ghost"}
            size="sm"
            onClick={() => setSelectedCategory("all")}
            className="flex-1 text-xs"
          >
            All
          </Button>
          <Button
            variant={selectedCategory === "free" ? "default" : "ghost"}
            size="sm"
            onClick={() => setSelectedCategory("free")}
            className="flex-1 text-xs"
          >
            Free
          </Button>
          <Button
            variant={selectedCategory === "premium" ? "default" : "ghost"}
            size="sm"
            onClick={() => setSelectedCategory("premium")}
            className="flex-1 text-xs"
          >
            Premium
          </Button>
        </div>
      </div>

      {/* Features List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {freeFeatures.length > 0 && (
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-2 h-2 bg-green-500 rounded-full" />
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Free Features
              </h3>
            </div>
            <div className="space-y-3">
              {freeFeatures.map((feature) => (
                <FeatureCard key={feature.id} feature={feature} />
              ))}
            </div>
          </div>
        )}

        {premiumFeatures.length > 0 && (
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-2 h-2 bg-blue-500 rounded-full" />
              <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                Premium Features
              </h3>
            </div>
            <div className="space-y-3">
              {premiumFeatures.map((feature) => (
                <FeatureCard key={feature.id} feature={feature} />
              ))}
            </div>
          </div>
        )}

        {filteredFeatures.length === 0 && (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-6 h-6 text-gray-400" />
            </div>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              No features found matching your search
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function FeatureCard({ feature }: { feature: typeof features[0] }) {
  const Icon = feature.icon;
  
  return (
    <div className="group p-4 bg-gray-50 dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 transition-all duration-200 cursor-pointer">
      <div className="flex items-start space-x-3">
        <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center flex-shrink-0">
          <Icon className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-1">
            <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {feature.title}
            </h4>
            <div className="flex items-center space-x-2">
              {feature.status === "available" && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
                  Available
                </span>
              )}
              {feature.status === "coming-soon" && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-400">
                  Coming Soon
                </span>
              )}
            </div>
          </div>
          <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
            {feature.description}
          </p>
        </div>
      </div>
    </div>
  );
}