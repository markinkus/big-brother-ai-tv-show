import { API_BASE_URL } from "@/lib/api";

export type AuditionAgentConfig = {
  provider: string;
  apiBaseUrl: string;
  modelName: string;
  characterName: string;
  traits: string[];
  skin: string;
  paletteId: string;
};

export type AuditionEvent = {
  id: string;
  atSecond: number;
  timestampLabel: string;
  summary: string;
  tone: "neutral" | "danger" | "success";
};

export type AuditionFeedFrame = {
  id: string;
  startSecond: number;
  endSecond: number;
  title: string;
  beat: string;
  camera: string;
  motion: string;
  spokenLine: string;
  roomMood: string;
  directorNote: string;
  audienceRead: string;
};

export type AuditionSnapshot = {
  sessionId: string | null;
  status: "idle" | "queued" | "running" | "complete" | "error";
  elapsedSeconds: number;
  durationSeconds: number;
  roomName: string;
  provider: string;
  modelName: string;
  events: AuditionEvent[];
  frames: AuditionFeedFrame[];
};

export type AuditionLaunchResult = {
  endpoint: string | null;
  error: string | null;
  snapshot: AuditionSnapshot | null;
  sessionId: string | null;
};

const fallbackProviders = ["openai", "anthropic", "google", "openrouter"];

const providerEndpoints = [
  "/api/auditions/providers",
  "/api/provino/providers",
  "/api/providers/llm",
];

function startEndpoints(seasonId: number) {
  return [
    `/api/seasons/${seasonId}/auditions/start`,
    `/api/seasons/${seasonId}/auditions/sessions`,
    `/api/seasons/${seasonId}/provino/start`,
    "/api/auditions/start",
    "/api/auditions/sessions",
    "/api/provino/start",
  ];
}

function sessionEndpoints(seasonId: number, sessionId: string) {
  return [
    `/api/seasons/${seasonId}/auditions/sessions/${sessionId}`,
    `/api/seasons/${seasonId}/provino/sessions/${sessionId}`,
    `/api/auditions/sessions/${sessionId}`,
    `/api/auditions/${sessionId}`,
    `/api/provino/sessions/${sessionId}`,
  ];
}

type RequestResult = {
  endpoint: string | null;
  error: string | null;
  payload: unknown;
};

function asObject(value: unknown): Record<string, unknown> | null {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function asString(value: unknown): string | null {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length ? trimmed : null;
  }
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }
  return null;
}

function asNumber(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim().length) {
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  }
  return null;
}

function normalizeStatus(value: unknown): AuditionSnapshot["status"] {
  const normalized = asString(value)?.toLowerCase();
  if (normalized === "queued" || normalized === "running" || normalized === "complete" || normalized === "error") {
    return normalized;
  }
  return "running";
}

function toTimestampLabel(totalSeconds: number) {
  const minutes = Math.floor(totalSeconds / 60)
    .toString()
    .padStart(2, "0");
  const seconds = Math.max(0, totalSeconds % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${seconds}`;
}

function normalizeEvents(rawEvents: unknown, durationSeconds: number): AuditionEvent[] {
  if (!Array.isArray(rawEvents)) {
    return [];
  }

  return rawEvents
    .map((event, index) => {
      if (typeof event === "string") {
        const atSecond = Math.min(durationSeconds, index * 30);
        return {
          id: `event-${index}`,
          atSecond,
          timestampLabel: toTimestampLabel(atSecond),
          summary: event,
          tone: "neutral" as const,
        };
      }

      const object = asObject(event);
      if (!object) {
        return null;
      }

      const atSecond =
        asNumber(object.at_second) ??
        asNumber(object.elapsed_seconds) ??
        (() => {
          const minute = asNumber(object.minute) ?? 0;
          const second = asNumber(object.second) ?? 0;
          return minute * 60 + second;
        })() ??
        Math.min(durationSeconds, index * 30);

      const summary =
        asString(object.summary) ??
        asString(object.description) ??
        asString(object.message) ??
        asString(object.label) ??
        "Audition beat";

      const toneValue = asString(object.tone)?.toLowerCase();
      const tone =
        toneValue === "danger" || toneValue === "success"
          ? toneValue
          : summary.toLowerCase().includes("hesitates") || summary.toLowerCase().includes("pressure")
            ? "danger"
            : summary.toLowerCase().includes("lands") || summary.toLowerCase().includes("wins")
              ? "success"
              : "neutral";

      return {
        id: asString(object.id) ?? `event-${index}`,
        atSecond,
        timestampLabel: asString(object.timestamp) ?? toTimestampLabel(atSecond),
        summary,
        tone,
      };
    })
    .filter((event): event is AuditionEvent => Boolean(event));
}

function normalizeFrames(rawFrames: unknown, durationSeconds: number): AuditionFeedFrame[] {
  if (!Array.isArray(rawFrames)) {
    return [];
  }

  return rawFrames
    .map((frame, index) => {
      const fallbackStart = Math.min(durationSeconds, index * 40);
      const fallbackEnd = Math.min(durationSeconds, fallbackStart + 40);

      if (typeof frame === "string") {
        return {
          id: `frame-${index}`,
          startSecond: fallbackStart,
          endSecond: Math.max(fallbackEnd, fallbackStart + 20),
          title: `Beat ${index + 1}`,
          beat: frame,
          camera: "mid shot",
          motion: "holds the mark with deliberate posture",
          spokenLine: frame,
          roomMood: "controlled",
          directorNote: "Telemetry light, replaying generic studio framing.",
          audienceRead: "The room starts listening for intent.",
        };
      }

      const object = asObject(frame);
      if (!object) {
        return null;
      }

      const startSecond = asNumber(object.start_second) ?? asNumber(object.at_second) ?? fallbackStart;
      const endSecond = asNumber(object.end_second) ?? Math.min(durationSeconds, startSecond + 40);

      return {
        id: asString(object.id) ?? `frame-${index}`,
        startSecond,
        endSecond: Math.max(endSecond, startSecond + 15),
        title: asString(object.title) ?? asString(object.label) ?? asString(object.scene) ?? `Beat ${index + 1}`,
        beat: asString(object.beat) ?? asString(object.summary) ?? asString(object.description) ?? "Audition room action.",
        camera: asString(object.camera) ?? asString(object.shot) ?? "mid shot",
        motion: asString(object.motion) ?? asString(object.action) ?? "keeps the scene live with crisp blocking",
        spokenLine: asString(object.spoken_line) ?? asString(object.quote) ?? asString(object.line) ?? "",
        roomMood: asString(object.room_mood) ?? asString(object.mood) ?? "measured",
        directorNote: asString(object.director_note) ?? asString(object.note) ?? "No director note supplied.",
        audienceRead: asString(object.audience_read) ?? asString(object.reaction) ?? "Audience reaction still forming.",
      };
    })
    .filter((frame): frame is AuditionFeedFrame => Boolean(frame));
}

function normalizeSnapshot(payload: unknown): AuditionSnapshot | null {
  const object = asObject(payload);
  if (!object) {
    return null;
  }

  const durationSeconds =
    asNumber(object.duration_seconds) ??
    ((asNumber(object.duration_minutes) ?? asNumber(object.minutes)) ? (asNumber(object.duration_minutes) ?? asNumber(object.minutes) ?? 0) * 60 : null) ??
    240;

  const elapsedSeconds =
    asNumber(object.elapsed_seconds) ??
    (() => {
      const minute = asNumber(object.current_minute) ?? 0;
      const second = asNumber(object.current_second) ?? 0;
      return minute * 60 + second;
    })() ??
    0;

  const rawEvents = object.events ?? object.event_log ?? object.log ?? object.timeline ?? [];
  const rawFrames = object.frames ?? object.live_feed ?? object.feed ?? object.scenes ?? [];

  return {
    sessionId: asString(object.session_id ?? object.id ?? asObject(object.session)?.id) ?? null,
    status: normalizeStatus(object.status),
    elapsedSeconds,
    durationSeconds,
    roomName: asString(object.room_name ?? asObject(object.room)?.name ?? object.room) ?? "Audition Room A",
    provider: asString(object.provider) ?? "configured provider",
    modelName: asString(object.model_name ?? object.model) ?? "configured model",
    events: normalizeEvents(rawEvents, durationSeconds),
    frames: normalizeFrames(rawFrames, durationSeconds),
  };
}

function mergeErrorMessages(messages: string[]) {
  return messages.filter(Boolean).slice(0, 3).join(" | ") || "Audition backend unavailable";
}

async function requestJson(paths: string[], init?: RequestInit): Promise<RequestResult> {
  const errors: string[] = [];

  for (const path of paths) {
    try {
      const response = await fetch(`${API_BASE_URL}${path}`, {
        ...init,
        headers: {
          "Content-Type": "application/json",
          ...(init?.headers ?? {}),
        },
        cache: "no-store",
      });

      if (!response.ok) {
        errors.push(`${path}: ${response.status} ${response.statusText}`);
        continue;
      }

      const text = await response.text();
      return {
        endpoint: path,
        error: null,
        payload: text ? (JSON.parse(text) as unknown) : null,
      };
    } catch (error) {
      errors.push(`${path}: ${error instanceof Error ? error.message : "Unknown request failure"}`);
    }
  }

  return { endpoint: null, error: mergeErrorMessages(errors), payload: null };
}

export async function fetchAuditionProviders(seasonId: number) {
  const seasonProviderEndpoints = providerEndpoints.flatMap((path) => [`/api/seasons/${seasonId}${path.slice(4)}`, path]);
  const result = await requestJson(seasonProviderEndpoints);
  const object = asObject(result.payload);
  const rawProviders =
    (Array.isArray(result.payload) ? result.payload : null) ??
    (Array.isArray(object?.providers) ? object?.providers : null) ??
    (Array.isArray(object?.items) ? object?.items : null) ??
    [];

  const providers = rawProviders
    .map((provider) =>
      typeof provider === "string" ? provider : asString(asObject(provider)?.id ?? asObject(provider)?.name ?? provider),
    )
    .filter((provider): provider is string => Boolean(provider));

  return {
    endpoint: result.endpoint,
    error: result.error,
    providers: providers.length ? providers : fallbackProviders,
  };
}

export async function startAuditionSession(seasonId: number, agent: AuditionAgentConfig): Promise<AuditionLaunchResult> {
  const payload = {
    provider: agent.provider,
    api_base_url: agent.apiBaseUrl,
    base_url: agent.apiBaseUrl,
    model: agent.modelName,
    model_name: agent.modelName,
    character_name: agent.characterName,
    traits: agent.traits,
    character_traits: agent.traits,
    skin: agent.skin,
    palette_id: agent.paletteId,
    duration_minutes: 4,
    duration_seconds: 240,
    room_name: "Studio Audition Room",
    character: {
      name: agent.characterName,
      traits: agent.traits,
      skin: agent.skin,
      palette_id: agent.paletteId,
    },
    room: {
      code: "audition-room",
      name: "Studio Audition Room",
    },
  };

  const result = await requestJson(startEndpoints(seasonId), {
    method: "POST",
    body: JSON.stringify(payload),
  });

  const snapshot = normalizeSnapshot(result.payload);

  return {
    endpoint: result.endpoint,
    error: result.error,
    snapshot,
    sessionId: snapshot?.sessionId ?? null,
  };
}

export async function pollAuditionSession(seasonId: number, sessionId: string) {
  const result = await requestJson(sessionEndpoints(seasonId, sessionId));
  return {
    endpoint: result.endpoint,
    error: result.error,
    snapshot: normalizeSnapshot(result.payload),
  };
}
