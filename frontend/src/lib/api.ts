import { ChatRequest, ChatResponse } from "@/types/chat";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function sendMessage(
  message: string,
  sessionId: string,
  consentDataUsage: boolean = true,
  consentContact: boolean = false
): Promise<ChatResponse> {
  const request: ChatRequest = {
    session_id: sessionId,
    message,
    source: "web",
    consent_data_usage: consentDataUsage,
    consent_contact: consentContact,
  };

  try {
    const response = await fetch(`${API_BASE_URL}/public/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      "Network error - please check your connection",
      0,
      error
    );
  }
}

export async function switchProvider(provider: string): Promise<void> {
  // This would typically be a backend endpoint to switch providers
  // For now, we'll just store it in localStorage
  localStorage.setItem("selectedProvider", provider);
}

export function getSelectedProvider(): string {
  return localStorage.getItem("selectedProvider") || "mock";
}
