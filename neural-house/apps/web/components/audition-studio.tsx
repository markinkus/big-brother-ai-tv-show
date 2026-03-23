"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { FormEvent, useMemo, useState } from "react";

import { apiGet, apiPost } from "@/lib/api";
import { Panel } from "@/components/panel";
import { PixelCharacter } from "@/components/pixel-character";
import { StatStrip } from "@/components/stat-strip";
import { StatusMessage } from "@/components/status-message";
import { buildSpritePalette, hairStyleOptions, pixelAccentPalettes, pixelBodyPalettes, silhouetteOptions } from "@/lib/pixel-art";

type AuditionSession = {
  id: number;
  status: string;
  environment_label: string;
  provider: string;
  api_base_url: string | null;
  model_name: string;
  provider_enabled: boolean;
  character_name: string;
  archetype: string;
  speech_style: string;
  public_hook: string;
  traits_json: string[];
  strengths_json: string[];
  weaknesses_json: string[];
  skin_palette: string;
  skin_accent: string;
  skin_silhouette: string;
  hair_style: string;
  simulated_minutes: number;
  playback_ms_per_beat: number;
  total_beats: number;
  current_beat: number;
  summary: string;
};

type AuditionEvent = {
  id: number;
  tick_number: number;
  simulated_second: number;
  zone: string;
  action_type: string;
  summary: string;
  dialogue: string | null;
  state_snapshot_json: {
    confidence: number;
    stress: number;
    camera_heat: number;
  };
};

type AuditionLiveState = {
  session: AuditionSession;
  visible_events: AuditionEvent[];
  next_event_eta_ms: number | null;
};

const zonePositions: Record<string, { left: string; top: string; label: string }> = {
  entrance: { left: "8%", top: "72%", label: "Entrance" },
  host_mark: { left: "22%", top: "48%", label: "Host Mark" },
  camera_lane: { left: "48%", top: "70%", label: "Camera Lane" },
  spotlight: { left: "50%", top: "30%", label: "Spotlight" },
  confessional_cam: { left: "78%", top: "42%", label: "Confessional Cam" },
  exit_mark: { left: "84%", top: "74%", label: "Exit" },
};

const defaultForm = {
  provider: "local_stub",
  apiBaseUrl: "",
  modelName: "deterministic-fallback",
  providerEnabled: false,
  characterName: "Nova",
  archetype: "Audition Firebrand",
  speechStyle: "bright, camera-aware, slightly dangerous",
  publicHook: "Put me on stage and the room stops pretending to be calm.",
  traits: "bold, strategic, theatrical",
  strengths: "camera instinct, composure, timing",
  weaknesses: "ego spikes, impatience",
  palette: "studio_blue",
  accent: "gold",
  silhouette: "host-ready",
  hairStyle: "crown",
  simulatedMinutes: 6,
  playbackMsPerBeat: 5000,
};

const paletteOptions = Object.keys(pixelBodyPalettes);
const accentOptions = Object.keys(pixelAccentPalettes);

function silhouetteStyle(silhouette: string) {
  switch (silhouette) {
    case "sharp":
      return { transform: "scaleX(0.92) translateY(1px)" };
    case "soft":
      return { transform: "scaleX(1.04) translateY(0px)" };
    case "masked":
      return { transform: "scaleX(0.98) translateY(2px)" };
    case "android":
      return { transform: "scaleX(0.88) translateY(1px)" };
    default:
      return { transform: "scaleX(1) translateY(0px)" };
  }
}

export function AuditionStudio() {
  const [form, setForm] = useState(defaultForm);
  const [sessionId, setSessionId] = useState<number | null>(null);

  const startMutation = useMutation({
    mutationFn: async () =>
      apiPost<AuditionSession>("/api/auditions", {
        provider_config: {
          provider: form.provider,
          api_base_url: form.apiBaseUrl || null,
          model_name: form.modelName,
          enabled: form.providerEnabled,
        },
        agent_config: {
          character_name: form.characterName,
          archetype: form.archetype,
          speech_style: form.speechStyle,
          public_hook: form.publicHook,
          traits: form.traits.split(",").map((item) => item.trim()).filter(Boolean),
          strengths: form.strengths.split(",").map((item) => item.trim()).filter(Boolean),
          weaknesses: form.weaknesses.split(",").map((item) => item.trim()).filter(Boolean),
          skin: {
            palette: form.palette,
            accent: form.accent,
            silhouette: form.silhouette,
            hair_style: form.hairStyle,
          },
        },
        simulated_minutes: form.simulatedMinutes,
        playback_ms_per_beat: form.playbackMsPerBeat,
      }),
    onSuccess: (result) => {
      if (result.data) {
        setSessionId(result.data.id);
      }
    },
  });

  const liveQuery = useQuery({
    queryKey: ["audition-live", sessionId],
    enabled: sessionId !== null,
    refetchInterval: (query) => {
      const data = query.state.data as AuditionLiveState | undefined;
      return data?.session.status === "completed" ? false : 1200;
    },
    queryFn: async () => {
      const result = await apiGet<AuditionLiveState>(`/api/auditions/${sessionId}/live`);
      if (!result.data) {
        throw new Error(result.error ?? "Unable to load audition state");
      }
      return result.data;
    },
  });

  const currentEvent = useMemo(
    () => liveQuery.data?.visible_events.at(-1) ?? null,
    [liveQuery.data],
  );

  const currentZone = currentEvent?.zone ?? "entrance";
  const spritePosition = zonePositions[currentZone] ?? zonePositions.entrance;
  const spriteSeed = useMemo(() => {
    const name = liveQuery.data?.session.character_name ?? form.characterName;
    return Array.from(name).reduce((sum, char) => sum + char.charCodeAt(0), sessionId ?? 97);
  }, [form.characterName, liveQuery.data?.session.character_name, sessionId]);
  const stagePalette = useMemo(
    () =>
      buildSpritePalette({
        paletteKey: liveQuery.data?.session.skin_palette ?? form.palette,
        accentKey: liveQuery.data?.session.skin_accent ?? form.accent,
        seed: spriteSeed,
      }),
    [form.accent, form.palette, liveQuery.data?.session.skin_accent, liveQuery.data?.session.skin_palette, spriteSeed],
  );

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    startMutation.mutate();
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <Panel
        title="Provino Config"
        subtitle="Build one audition subject. The stage stays deterministic unless an optional provider is explicitly enabled."
      >
        <form className="space-y-4" onSubmit={submit}>
          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Engine</p>
              <p className="mt-2 text-sm text-white/60">
                `local_stub` keeps the audition deterministic. Any external provider is optional and only used when enabled.
              </p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Provider</span>
                <select
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.provider}
                  onChange={(event) => setForm((current) => ({ ...current, provider: event.target.value }))}
                >
                  {["local_stub", "ollama", "openai_compatible", "anthropic_compatible"].map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Model Name</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.modelName}
                  onChange={(event) => setForm((current) => ({ ...current, modelName: event.target.value }))}
                />
              </label>
            </div>
            <label className="block">
              <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">API Base URL</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                value={form.apiBaseUrl}
                placeholder="http://localhost:11434/v1"
                onChange={(event) => setForm((current) => ({ ...current, apiBaseUrl: event.target.value }))}
              />
            </label>
            <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/75">
              <input
                checked={form.providerEnabled}
                type="checkbox"
                onChange={(event) => setForm((current) => ({ ...current, providerEnabled: event.target.checked }))}
              />
              When enabled, the provider config is included. The world state still drives the audition.
            </label>
          </section>

          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Contestant</p>
              <p className="mt-2 text-sm text-white/60">Define the public persona and the private pressure points the audition should expose.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Character Name</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.characterName}
                  onChange={(event) => setForm((current) => ({ ...current, characterName: event.target.value }))}
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Archetype</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.archetype}
                  onChange={(event) => setForm((current) => ({ ...current, archetype: event.target.value }))}
                />
              </label>
            </div>
            <label className="block">
              <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Speech Style</span>
              <input
                className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                value={form.speechStyle}
                onChange={(event) => setForm((current) => ({ ...current, speechStyle: event.target.value }))}
              />
            </label>
            <label className="block">
              <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Public Hook</span>
              <textarea
                className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                value={form.publicHook}
                onChange={(event) => setForm((current) => ({ ...current, publicHook: event.target.value }))}
              />
            </label>
            <div className="grid gap-4 md:grid-cols-3">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Traits</span>
                <textarea
                  className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.traits}
                  onChange={(event) => setForm((current) => ({ ...current, traits: event.target.value }))}
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Strengths</span>
                <textarea
                  className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.strengths}
                  onChange={(event) => setForm((current) => ({ ...current, strengths: event.target.value }))}
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Weaknesses</span>
                <textarea
                  className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.weaknesses}
                  onChange={(event) => setForm((current) => ({ ...current, weaknesses: event.target.value }))}
                />
              </label>
            </div>
          </section>

          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Skin</p>
              <p className="mt-2 text-sm text-white/60">Palette, accent, silhouette, and hair are mirrored in the live preview below.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-4">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Palette</span>
                <select
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.palette}
                  onChange={(event) => setForm((current) => ({ ...current, palette: event.target.value }))}
                >
                  {paletteOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Accent</span>
                <select
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.accent}
                  onChange={(event) => setForm((current) => ({ ...current, accent: event.target.value }))}
                >
                  {accentOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Silhouette</span>
                <select
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.silhouette}
                  onChange={(event) => setForm((current) => ({ ...current, silhouette: event.target.value }))}
                >
                  {silhouetteOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Hair Style</span>
                <select
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.hairStyle}
                  onChange={(event) => setForm((current) => ({ ...current, hairStyle: event.target.value }))}
                >
                  {hairStyleOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </section>

          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Timing</p>
              <p className="mt-2 text-sm text-white/60">Longer runs create more visible beats. Playback speed only affects how quickly the feed reveals them.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Simulated Minutes</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  min={2}
                  max={12}
                  type="number"
                  value={form.simulatedMinutes}
                  onChange={(event) => setForm((current) => ({ ...current, simulatedMinutes: Number(event.target.value) }))}
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Playback ms / Beat</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  min={500}
                  max={15000}
                  step={500}
                  type="number"
                  value={form.playbackMsPerBeat}
                  onChange={(event) => setForm((current) => ({ ...current, playbackMsPerBeat: Number(event.target.value) }))}
                />
              </label>
            </div>
          </section>

          <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Live Pixel Preview</p>
            <div className="mt-4 flex items-center gap-5">
              <div className="rounded-2xl border border-white/10 bg-black/30 p-3" style={silhouetteStyle(form.silhouette)}>
                <PixelCharacter
                  accentKey={form.accent}
                  hairStyle={form.hairStyle}
                  paletteKey={form.palette}
                  seed={spriteSeed}
                  scale={4}
                  silhouette={form.silhouette}
                  variant="portrait"
                />
              </div>
              <div className="space-y-2 text-xs uppercase tracking-[0.16em] text-white/55">
                <div>Palette {form.palette}</div>
                <div>Accent {form.accent}</div>
                <div>Hair {form.hairStyle}</div>
                <div>Silhouette {form.silhouette}</div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/60">
            {form.providerEnabled
              ? "Provider integration is enabled, but the audition still remains state-driven."
              : "Provider integration is off. The audition runs on the deterministic fallback path."}
          </div>
          <button
            type="submit"
            className="rounded-2xl border border-accent/40 bg-accent px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-black"
          >
            Start Audition
          </button>
        </form>
      </Panel>

      <div className="space-y-6">
        <Panel title="Live Audition" subtitle="Real-time playback of a deterministic TV provino sequence.">
          <StatusMessage error={startMutation.data?.error ?? (liveQuery.error instanceof Error ? liveQuery.error : null)} />
          <StatStrip
            items={[
              { label: "Status", value: liveQuery.data?.session.status ?? "idle" },
              { label: "Provider", value: liveQuery.data?.session.provider ?? form.provider },
              { label: "Model", value: liveQuery.data?.session.model_name ?? form.modelName },
              { label: "Next Beat", value: liveQuery.data?.next_event_eta_ms ? `${(liveQuery.data.next_event_eta_ms / 1000).toFixed(1)}s` : "done" },
            ]}
          />

          <div
            className="pixel-frame pixel-stage-grid pixel-scanlines relative mt-5 h-[28rem] overflow-hidden rounded-3xl border border-white/10"
            style={{
              boxShadow: `inset 0 0 0 2px ${stagePalette.trim}22, inset 0 0 28px ${stagePalette.accent}18`,
            }}
          >
            <div className="absolute inset-x-0 top-0 h-16 bg-[repeating-linear-gradient(90deg,rgba(255,255,255,0.05)_0_12px,transparent_12px_24px)] opacity-50" />
            <div className="absolute left-4 top-20 h-32 w-10 rounded-sm border border-white/10 bg-black/35" />
            <div className="absolute right-4 top-20 h-32 w-10 rounded-sm border border-white/10 bg-black/35" />
            <div className="absolute inset-x-[14%] top-[52%] h-[30%] bg-[repeating-linear-gradient(90deg,rgba(255,255,255,0.06)_0_12px,rgba(0,0,0,0.02)_12px_24px)] opacity-60" />
            <div className="absolute left-8 top-6 rounded-full border border-cyan-200/30 bg-cyan-200/10 px-3 py-1 font-display text-[10px] uppercase tracking-[0.22em] text-cyan-100">
              {liveQuery.data?.session.environment_label ?? "Neural House TV Audition Loft"}
            </div>
            {Object.entries(zonePositions).map(([key, position]) => (
              <div
                key={key}
                className="pixel-zone absolute flex h-16 w-24 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-md border border-white/10 bg-black/25 text-center font-display text-[10px] uppercase tracking-[0.16em] text-white/55"
                style={{ left: position.left, top: position.top }}
              >
                {position.label}
              </div>
            ))}
            <div
              className="absolute -translate-x-1/2 -translate-y-1/2 transition-all duration-700"
              style={{ left: spritePosition.left, top: spritePosition.top }}
            >
              <PixelCharacter
                accentKey={liveQuery.data?.session.skin_accent ?? form.accent}
                className="pixel-bob"
                hairStyle={liveQuery.data?.session.hair_style ?? form.hairStyle}
                paletteKey={liveQuery.data?.session.skin_palette ?? form.palette}
                scale={4}
                seed={spriteSeed}
                silhouette={liveQuery.data?.session.skin_silhouette ?? form.silhouette}
                variant="portrait"
              />
            </div>
            <div className="absolute inset-x-0 bottom-0 border-t border-white/10 bg-black/35 p-4">
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">
                {currentEvent?.action_type ?? "awaiting cue"}
              </p>
              <p className="mt-2 text-sm text-white/80">
                {currentEvent?.summary ?? "Launch an audition to watch the agent enter the TV loft and react to studio cues."}
              </p>
              <p className="mt-2 text-sm text-white/60">
                {currentEvent?.dialogue ?? "The feed is idle."}
              </p>
            </div>
          </div>
        </Panel>

        <Panel title="State Feed" subtitle="Character telemetry and visible beat log.">
          <StatStrip
            items={[
              { label: "Confidence", value: currentEvent?.state_snapshot_json.confidence ?? 0, tone: "success" },
              { label: "Stress", value: currentEvent?.state_snapshot_json.stress ?? 0, tone: "danger" },
              { label: "Camera Heat", value: currentEvent?.state_snapshot_json.camera_heat ?? 0 },
              { label: "Visible Beats", value: liveQuery.data?.visible_events.length ?? 0 },
            ]}
          />
          <div className="mt-5 grid gap-4 lg:grid-cols-[0.72fr_1.28fr]">
            <article className="rounded-3xl border border-white/10 bg-black/20 p-4">
              <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
                {liveQuery.data?.session.character_name ?? form.characterName}
              </p>
              <p className="mt-2 text-sm text-white/70">{liveQuery.data?.session.archetype ?? form.archetype}</p>
              <p className="mt-3 text-sm text-white/80">{liveQuery.data?.session.summary ?? "Configure one agent and press Start Audition."}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(liveQuery.data?.session.traits_json ?? form.traits.split(",").map((item) => item.trim()).filter(Boolean)).map((trait) => (
                  <span
                    key={trait}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.16em] text-white/65"
                  >
                    {trait}
                  </span>
                ))}
              </div>
              <div className="mt-4 grid grid-cols-2 gap-2 text-[10px] uppercase tracking-[0.16em] text-white/45">
                <span>Palette {liveQuery.data?.session.skin_palette ?? form.palette}</span>
                <span>Accent {liveQuery.data?.session.skin_accent ?? form.accent}</span>
                <span>Hair {liveQuery.data?.session.hair_style ?? form.hairStyle}</span>
                <span>Silhouette {liveQuery.data?.session.skin_silhouette ?? form.silhouette}</span>
              </div>
            </article>
            <div className="space-y-3">
              {(liveQuery.data?.visible_events ?? []).slice().reverse().map((event) => (
                <article key={event.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
                      Beat {event.tick_number + 1} · {event.zone.replaceAll("_", " ")}
                    </p>
                    <p className="text-xs text-white/45">{event.simulated_second}s</p>
                  </div>
                  <p className="mt-2 text-sm text-white/80">{event.summary}</p>
                  <p className="mt-2 text-sm text-white/60">{event.dialogue}</p>
                </article>
              ))}
              {!liveQuery.data?.visible_events.length ? (
                <StatusMessage empty="No visible beats yet. The live feed starts as soon as the audition session is created." />
              ) : null}
            </div>
          </div>
        </Panel>
      </div>
    </div>
  );
}
