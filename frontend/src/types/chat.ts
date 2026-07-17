export type Provider = "openai" | "anthropic";

export interface Budget {
  amount: number | null;
  currency: string | null;
  period: "total" | "per_day" | "unknown";
  includes_accommodation: boolean | null;
}

export interface Travellers {
  adults: number | null;
  children: number | null;
  child_ages: number[];
}

export interface TripProfile {
  destination: string | null;
  duration_days: number | null;
  start_date: string | null;
  end_date: string | null;
  travellers: Travellers;
  interests: string[];
  preferences: string[];
  constraints: string[];
  pace: "relaxed" | "balanced" | "intensive" | "unknown";
  budget: Budget;
}

export interface Activity {
  period: "morning" | "afternoon" | "evening";
  title: string;
  description: string;
  location: string | null;
  estimated_duration_minutes: number | null;
  estimated_cost: number | null;
  currency: string | null;
}

export interface ItineraryDay {
  day: number;
  title: string;
  activities: Activity[];
}

export interface Itinerary {
  trip_title: string;
  trip_summary: string;
  days: ItineraryDay[];
  practical_tips: string[];
  estimated_budget: {
    currency: string;
    total: number | null;
    notes: string[];
  };
}

export interface ChatResponse {
  session_id: string;
  provider: Provider;
  status:
    | "collecting_information"
    | "needs_clarification"
    | "generating_itinerary"
    | "completed";
  assistant_message: string;
  trip_profile: TripProfile;
  itinerary: Itinerary | null;
  metrics: ModelMetrics | null;
}

export interface ModelMetrics {
  provider: string;
  model: string;
  latency_seconds: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost_usd: number;
  weather_tool_used: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}
