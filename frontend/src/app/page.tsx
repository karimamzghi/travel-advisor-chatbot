"use client";

import Image from "next/image";
import {
  FormEvent,
  useEffect,
  useRef,
  useState,
} from "react";
import {
  Bot,
  Clock3,
  Coins,
  Gauge,
  MapPinned,
  Plane,
  RefreshCcw,
  Send,
  Sparkles,
  Wrench,
} from "lucide-react";

import { sendChatMessage } from "@/lib/api";

import type {
  ChatMessage,
  Itinerary,
  ModelMetrics,
  Provider,
} from "@/types/chat";

const INITIAL_MESSAGE =
  "Hi, adventurer! I’m LostNoMore 🧳 Tell me where you would like to travel.";

function createSessionId(): string {
  if (
    typeof crypto !== "undefined" &&
    typeof crypto.randomUUID === "function"
  ) {
    return crypto.randomUUID();
  }

  return `lostnomore-${Date.now()}`;
}

export default function HomePage() {
  const [sessionId, setSessionId] = useState("");
  const [provider, setProvider] =
    useState<Provider>("openai");

  const [messages, setMessages] = useState<
    ChatMessage[]
  >([
    {
      id: "welcome",
      role: "assistant",
      content: INITIAL_MESSAGE,
    },
  ]);

  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] =
    useState(false);

  const [itinerary, setItinerary] =
    useState<Itinerary | null>(null);

  const [metrics, setMetrics] =
    useState<ModelMetrics | null>(null);

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const existingSession =
      window.localStorage.getItem(
        "lostnomore-session-id",
      );

    const currentSession =
      existingSession ?? createSessionId();

    window.localStorage.setItem(
      "lostnomore-session-id",
      currentSession,
    );

    setSessionId(currentSession);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, isLoading]);

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const message = input.trim();

    if (!message || !sessionId || isLoading) {
      return;
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: message,
      },
    ]);

    setInput("");
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        sessionId,
        provider,
        message,
      });

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.assistant_message,
        },
      ]);

      setItinerary(response.itinerary);
      setMetrics(response.metrics);
    } finally {
      setIsLoading(false);
    }
  }

  function handleNewTrip() {
    const nextSessionId = createSessionId();

    window.localStorage.setItem(
      "lostnomore-session-id",
      nextSessionId,
    );

    setSessionId(nextSessionId);
    setMessages([
      {
        id: crypto.randomUUID(),
        role: "assistant",
        content: INITIAL_MESSAGE,
      },
    ]);
    setItinerary(null);
    setMetrics(null);
    setInput("");
  }

  return (
    <main className="travel-background min-h-screen">
      <Header
        provider={provider}
        setProvider={setProvider}
        providerLocked={messages.length > 1}
        onNewTrip={handleNewTrip}
      />

      <div className="mx-auto max-w-6xl px-4 py-7 sm:px-6">
        <Hero />

        <section className="mt-7 overflow-hidden rounded-[34px] border-2 border-[#17211b] bg-white shadow-[9px_9px_0_#17211b]">
          <div className="border-b-2 border-[#17211b] bg-[#55bfe0] px-5 py-4">
            <div className="flex items-center gap-3">
              <div className="grid h-11 w-11 place-items-center rounded-2xl border-2 border-[#17211b] bg-white">
                <Bot size={23} />
              </div>

              <div>
                <h2 className="font-black">
                  Chat with LostNoMore
                </h2>
                <p className="text-sm font-medium">
                  Tell me your dream. I’ll pack the plan.
                </p>
              </div>
            </div>
          </div>

          <div className="hide-scrollbar min-h-[430px] max-h-[62vh] space-y-5 overflow-y-auto bg-[#fffdf7] p-5 sm:p-7">
            {messages.map((message) => (
              <ChatBubble
                key={message.id}
                message={message}
              />
            ))}

            {isLoading && <LoadingBubble />}

            <div ref={messagesEndRef} />
          </div>

          <form
            onSubmit={handleSubmit}
            className="border-t-2 border-[#17211b] bg-white p-4 sm:p-5"
          >
            <div className="flex gap-3">
              <input
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                disabled={isLoading}
                placeholder="Tell me about your trip..."
                className="min-w-0 flex-1 rounded-2xl border-2 border-[#17211b] bg-[#fffaf0] px-4 py-3 font-medium outline-none transition focus:bg-white"
              />

              <button
                type="submit"
                disabled={
                  !input.trim() ||
                  isLoading ||
                  !sessionId
                }
                className="flex items-center gap-2 rounded-2xl border-2 border-[#17211b] bg-[#188a65] px-5 py-3 font-black text-white shadow-[4px_4px_0_#17211b] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Send size={18} />
                <span className="hidden sm:inline">
                  Send
                </span>
              </button>
            </div>
          </form>
        </section>

        {itinerary && (
          <ItinerarySection itinerary={itinerary} />
        )}

        {metrics && (
          <MetricsSection metrics={metrics} />
        )}
      </div>
    </main>
  );
}

function Header({
  provider,
  setProvider,
  providerLocked,
  onNewTrip,
}: {
  provider: Provider;
  setProvider: (provider: Provider) => void;
  providerLocked: boolean;
  onNewTrip: () => void;
}) {
  return (
    <header className="sticky top-0 z-20 border-b-2 border-[#17211b] bg-white/90 backdrop-blur-xl">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <div className="flex items-center gap-3">
          <Image
            src="/lostnomore-logo.png"
            alt="LostNoMore suitcase mascot"
            width={105}
            height={70}
            priority
            className="h-16 w-auto object-contain"
          />

          <div className="hidden sm:block">
            <p className="text-xs font-black uppercase tracking-[0.2em] text-[#188a65]">
              AI travel companion
            </p>

            <h1 className="text-2xl font-black tracking-tight">
              LostNoMore
            </h1>

            <p className="text-sm text-slate-500">
              Never get lost. Just explore.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={provider}
            disabled={providerLocked}
            onChange={(event) =>
              setProvider(
                event.target.value as Provider,
              )
            }
            className="rounded-xl border-2 border-[#17211b] bg-[#fffaf0] px-3 py-2 text-sm font-black"
          >
            <option value="openai">
              OpenAI
            </option>

            <option value="anthropic">
              Anthropic
            </option>
          </select>

          <button
            type="button"
            onClick={onNewTrip}
            className="flex items-center gap-2 rounded-xl border-2 border-[#17211b] bg-[#ffc84a] px-3 py-2 text-sm font-black shadow-[3px_3px_0_#17211b] transition hover:-translate-y-0.5"
          >
            <RefreshCcw size={16} />
            <span className="hidden sm:inline">
              New trip
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="grid items-center gap-6 rounded-[34px] border-2 border-[#17211b] bg-[#ffc84a] p-6 shadow-[8px_8px_0_#17211b] md:grid-cols-[1fr_260px]">
      <div>
        <div className="mb-3 inline-flex items-center gap-2 rounded-full border-2 border-[#17211b] bg-white px-3 py-1 text-sm font-black">
          <Sparkles size={16} />
          Adventure starts here
        </div>

        <h2 className="max-w-2xl text-4xl font-black leading-tight sm:text-5xl">
          Confusion ends.
          <br />
          Your next trip begins.
        </h2>

        <p className="mt-4 max-w-xl text-base font-medium leading-7">
          Chat naturally, choose your AI travel
          brain, and receive a personalized
          itinerary powered by live weather data.
        </p>
      </div>

      <div className="relative hidden justify-center md:flex">
        <div className="absolute h-44 w-44 rounded-full border-2 border-[#17211b] bg-[#55bfe0]" />

        <Image
          src="/lostnomore-logo.png"
          alt=""
          width={220}
          height={180}
          className="relative z-10 h-48 w-auto object-contain"
        />
      </div>
    </section>
  );
}

function ChatBubble({
  message,
}: {
  message: ChatMessage;
}) {
  const isUser = message.role === "user";

  return (
    <div
      className={
        isUser
          ? "ml-auto flex max-w-[85%] justify-end"
          : "mr-auto flex max-w-[92%] items-start gap-3"
      }
    >
      {!isUser && (
        <Image
          src="/lostnomore-logo.png"
          alt=""
          width={48}
          height={48}
          className="h-11 w-11 shrink-0 object-contain"
        />
      )}

      <article
        className={
          isUser
            ? "rounded-3xl rounded-br-md border-2 border-[#17211b] bg-[#55bfe0] px-4 py-3 font-medium shadow-[4px_4px_0_#17211b]"
            : "rounded-3xl rounded-bl-md border-2 border-[#17211b] bg-[#fff2bd] px-4 py-3 shadow-[4px_4px_0_#17211b]"
        }
      >
        <p className="whitespace-pre-wrap text-sm leading-6">
          {message.content}
        </p>
      </article>
    </div>
  );
}

function LoadingBubble() {
  return (
    <div className="mr-auto flex max-w-[92%] items-center gap-3">
      <Image
        src="/lostnomore-logo.png"
        alt=""
        width={48}
        height={48}
        className="h-11 w-11 animate-bounce object-contain"
      />

      <div className="rounded-3xl rounded-bl-md border-2 border-[#17211b] bg-[#fff2bd] px-4 py-3 shadow-[4px_4px_0_#17211b]">
        <p className="font-black">
          LostNoMore is packing…
        </p>

        <p className="text-sm text-slate-600">
          Checking your preferences and planning
          the route.
        </p>
      </div>
    </div>
  );
}

function ItinerarySection({
  itinerary,
}: {
  itinerary: Itinerary;
}) {
  return (
    <section className="mt-10">
      <div className="mb-5 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border-2 border-[#17211b] bg-[#188a65] px-4 py-2 font-black text-white shadow-[3px_3px_0_#17211b]">
          <Plane size={18} />
          Adventure ready!
        </div>

        <h2 className="mt-4 text-3xl font-black sm:text-4xl">
          {itinerary.trip_title}
        </h2>

        <p className="mx-auto mt-3 max-w-3xl leading-7 text-slate-600">
          {itinerary.trip_summary}
        </p>
      </div>

      <div className="space-y-6">
        {itinerary.days.map((day) => (
          <article
            key={day.day}
            className="overflow-hidden rounded-[30px] border-2 border-[#17211b] bg-white shadow-[7px_7px_0_#17211b]"
          >
            <div className="flex items-center gap-4 border-b-2 border-[#17211b] bg-[#ffc84a] p-5">
              <div className="grid h-12 w-12 shrink-0 place-items-center rounded-full border-2 border-[#17211b] bg-white text-xl font-black">
                {day.day}
              </div>

              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-[#0d6049]">
                  Day {day.day}
                </p>

                <h3 className="text-xl font-black">
                  {day.title}
                </h3>
              </div>
            </div>

            <div className="grid gap-4 p-5 md:grid-cols-3">
              {day.activities.map(
                (activity, index) => (
                  <div
                    key={`${day.day}-${index}`}
                    className="rounded-2xl border-2 border-[#17211b] bg-[#fffaf0] p-4"
                  >
                    <p className="text-xs font-black uppercase tracking-[0.15em] text-[#188a65]">
                      {activity.period}
                    </p>

                    <h4 className="mt-2 font-black">
                      {activity.title}
                    </h4>

                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      {activity.description}
                    </p>

                    {activity.location && (
                      <div className="mt-3 flex items-center gap-2 text-sm font-bold">
                        <MapPinned size={15} />
                        {activity.location}
                      </div>
                    )}
                  </div>
                ),
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function MetricsSection({
  metrics,
}: {
  metrics: ModelMetrics;
}) {
  return (
    <details className="mt-10 rounded-[30px] border-2 border-[#17211b] bg-white shadow-[7px_7px_0_#17211b]">
      <summary className="flex cursor-pointer list-none items-center gap-3 bg-[#55bfe0] p-5 font-black">
        <Gauge size={22} />
        View AI model performance
      </summary>

      <div className="grid gap-4 p-5 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          icon={<Bot size={18} />}
          label="Provider"
          value={metrics.provider}
        />

        <MetricCard
          icon={<Sparkles size={18} />}
          label="Model"
          value={metrics.model}
        />

        <MetricCard
          icon={<Clock3 size={18} />}
          label="Latency"
          value={`${metrics.latency_seconds.toFixed(2)} sec`}
        />

        <MetricCard
          icon={<Coins size={18} />}
          label="Estimated cost"
          value={`$${metrics.estimated_cost_usd.toFixed(6)}`}
        />

        <MetricCard
          icon={<Gauge size={18} />}
          label="Input tokens"
          value={metrics.input_tokens.toLocaleString()}
        />

        <MetricCard
          icon={<Gauge size={18} />}
          label="Output tokens"
          value={metrics.output_tokens.toLocaleString()}
        />

        <MetricCard
          icon={<Gauge size={18} />}
          label="Total tokens"
          value={metrics.total_tokens.toLocaleString()}
        />

        <MetricCard
          icon={<Wrench size={18} />}
          label="Weather tool"
          value={
            metrics.weather_tool_used
              ? "Used"
              : "Not used"
          }
        />
      </div>
    </details>
  );
}

function MetricCard({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border-2 border-[#17211b] bg-[#fffaf0] p-4">
      <div className="flex items-center gap-2 text-[#188a65]">
        {icon}

        <p className="text-xs font-black uppercase tracking-[0.12em]">
          {label}
        </p>
      </div>

      <p className="mt-2 break-words font-black capitalize">
        {value}
      </p>
    </div>
  );
}

