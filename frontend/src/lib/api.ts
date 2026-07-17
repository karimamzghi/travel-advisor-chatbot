import type {
  ChatResponse,
  Provider,
} from "@/types/chat";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8000";

interface SendMessageInput {
  sessionId: string;
  provider: Provider;
  message: string;
}

export async function sendChatMessage({
  sessionId,
  provider,
  message,
}: SendMessageInput): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      provider,
      message,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();

    console.error(
      "Chat API error:",
      response.status,
      errorText,
    );

    throw new Error(
      errorText || "Failed to send chat message."
    );
  }

  const data: ChatResponse = await response.json();

  console.log("FULL CHAT RESPONSE:", data);
  console.log("METRICS:", data.metrics);

  return data;
}
