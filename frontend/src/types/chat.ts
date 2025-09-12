export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  topic?: string;
  allowed?: boolean;
  provider?: string;
  model?: string;
  tokens_in?: number;
  tokens_out?: number;
  latency_ms?: number;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  source: string;
  consent_data_usage: boolean;
  consent_contact: boolean;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  topic: string;
  allowed: boolean;
}

export interface Provider {
  id: string;
  name: string;
  description: string;
  status: "available" | "unavailable" | "testing";
  icon: string;
}

export const PROVIDERS: Provider[] = [
  {
    id: "mock",
    name: "Mock",
    description: "Testing provider with deterministic responses",
    status: "available",
    icon: "🧪",
  },
  {
    id: "openai",
    name: "OpenAI",
    description: "GPT-4o, GPT-4o-mini, GPT-3.5-turbo",
    status: "unavailable",
    icon: "🤖",
  },
  {
    id: "anthropic",
    name: "Anthropic",
    description: "Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku",
    status: "unavailable",
    icon: "🧠",
  },
  {
    id: "google",
    name: "Google",
    description: "Gemini 1.5 Flash, Gemini 1.5 Pro, Gemini 1.0 Pro",
    status: "unavailable",
    icon: "🔍",
  },
  {
    id: "mistral",
    name: "Mistral",
    description: "Mistral Large, Mistral Medium, Mistral Small",
    status: "unavailable",
    icon: "🌪️",
  },
  {
    id: "cohere",
    name: "Cohere",
    description: "Command R+, Command R, Command Light",
    status: "unavailable",
    icon: "🔗",
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    description: "Access to 100+ models from various providers",
    status: "unavailable",
    icon: "🌐",
  },
  {
    id: "perplexity",
    name: "Perplexity",
    description: "Web-aware models with real-time information",
    status: "unavailable",
    icon: "🔮",
  },
  {
    id: "bedrock",
    name: "AWS Bedrock",
    description: "Claude, Llama, Mistral via AWS",
    status: "unavailable",
    icon: "☁️",
  },
];

