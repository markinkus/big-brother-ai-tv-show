"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { apiGet, apiPost } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { PhaserHouseCanvas } from "@/components/phaser-house-canvas";
import { StatStrip } from "@/components/stat-strip";
import { StatusMessage } from "@/components/status-message";

type Room = {
  id: number;
  code: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
};

type Contestant = {
  id: number;
  display_name: string;
  archetype: string;
  avatar_seed: number;
  skin_palette: string;
  skin_accent: string;
  skin_silhouette: string;
  hair_style: string;
};

type SimulationState = {
  season_id: number;
  tick_number: number;
  status: string;
  active_room_code: string | null;
  recent_event_ids: number[];
  active_contestant_ids: number[];
  current_tension: number;
  director_mode: string | null;
  highlight_ids: number[];
  confessional_ids: number[];
};

type Event = {
  id: number;
  tick_number: number;
  event_type: string;
  summary: string;
  payload_json: {
    actor_ids?: number[];
    actor_names?: string[];
    room_code?: string;
    room_name?: string;
    visibility?: string;
    director_mode?: string | null;
    director_reason?: string | null;
    objective_focus?: Record<string, string[]>;
    confessional_ids?: number[];
    highlight_id?: number;
  };
  tension_score: number;
};

type ContestantState = {
  contestant_id: number;
  display_name: string;
  room_code: string | null;
  energy: number;
  stress: number;
  suspicion: number;
  confidence: number;
  social_visibility: number;
  current_focus: string;
  status_effects_json: {
    popularity?: Record<string, number>;
  };
};

type Objective = {
  id: number;
  contestant_name: string;
  title: string;
  priority: number;
  progress: number;
  active: boolean;
  duration_ticks: number;
};

type Memory = {
  id: number;
  contestant_name: string;
  memory_type: string;
  summary: string;
  salience: number;
};

type Highlight = {
  id: number;
  category: string;
  title: string;
  summary: string;
  score: number;
};

type Confessional = {
  id: number;
  contestant_name: string;
  public_transcript: string;
  contradiction_flags_json: string[];
  shadow_flags_json: string[];
};

export function HouseDashboard() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const queryClient = useQueryClient();
  const [controlError, setControlError] = useState<string | null>(null);

  const rooms = useQuery({
    queryKey: ["rooms", seasonId],
    queryFn: async () => (await apiGet<Room[]>(`/api/seasons/${seasonId}/rooms`)).data ?? [],
    refetchInterval: 5_000,
  });
  const contestants = useQuery({
    queryKey: ["contestants", seasonId],
    queryFn: async () => (await apiGet<Contestant[]>(`/api/seasons/${seasonId}/contestants`)).data ?? [],
    refetchInterval: 5_000,
  });
  const state = useQuery({
    queryKey: ["simulation-state", seasonId],
    queryFn: async () => (await apiGet<SimulationState>(`/api/seasons/${seasonId}/simulation/state`)).data,
    refetchInterval: 3_000,
  });
  const events = useQuery({
    queryKey: ["events", seasonId],
    queryFn: async () => (await apiGet<Event[]>(`/api/seasons/${seasonId}/events`)).data ?? [],
    refetchInterval: 3_000,
  });
  const contestantStates = useQuery({
    queryKey: ["contestant-states", seasonId],
    queryFn: async () => (await apiGet<ContestantState[]>(`/api/seasons/${seasonId}/contestant-states`)).data ?? [],
    refetchInterval: 3_000,
  });
  const objectives = useQuery({
    queryKey: ["objectives", seasonId],
    queryFn: async () => (await apiGet<Objective[]>(`/api/seasons/${seasonId}/objectives`)).data ?? [],
    refetchInterval: 3_000,
  });
  const memories = useQuery({
    queryKey: ["memories", seasonId],
    queryFn: async () => (await apiGet<Memory[]>(`/api/seasons/${seasonId}/memories`)).data ?? [],
    refetchInterval: 3_000,
  });
  const highlights = useQuery({
    queryKey: ["highlights", seasonId],
    queryFn: async () => (await apiGet<Highlight[]>(`/api/seasons/${seasonId}/highlights`)).data ?? [],
    refetchInterval: 3_000,
  });
  const confessionals = useQuery({
    queryKey: ["confessionals", seasonId],
    queryFn: async () => (await apiGet<Confessional[]>(`/api/seasons/${seasonId}/confessionals`)).data ?? [],
    refetchInterval: 3_000,
  });

  const latestEvent = useMemo(() => (events.data ?? [])[0] ?? null, [events.data]);
  const activeActorIds = useMemo(() => latestEvent?.payload_json.actor_ids ?? state.data?.active_contestant_ids ?? [], [latestEvent, state.data]);
  const focusRoomCode = latestEvent?.payload_json.room_code ?? state.data?.active_room_code ?? null;
  const highlightedObjectives = useMemo(() => (objectives.data ?? []).filter((item) => item.active).slice(0, 6), [objectives.data]);
  const liveStates = useMemo(() => (contestantStates.data ?? []).slice(0, 4), [contestantStates.data]);
  const hotMemories = useMemo(() => (memories.data ?? []).slice(0, 4), [memories.data]);
  const topHighlights = useMemo(() => (highlights.data ?? []).slice(0, 4), [highlights.data]);
  const latestConfessionals = useMemo(() => (confessionals.data ?? []).slice(0, 3), [confessionals.data]);

  const controlMutation = useMutation({
    mutationFn: async (path: string) => {
      setControlError(null);
      const result = await apiPost<unknown>(path);
      if (result.error) {
        throw new Error(result.error);
      }
      return result.data;
    },
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["simulation-state", seasonId] }),
        queryClient.invalidateQueries({ queryKey: ["events", seasonId] }),
        queryClient.invalidateQueries({ queryKey: ["contestant-states", seasonId] }),
        queryClient.invalidateQueries({ queryKey: ["objectives", seasonId] }),
        queryClient.invalidateQueries({ queryKey: ["memories", seasonId] }),
        queryClient.invalidateQueries({ queryKey: ["highlights", seasonId] }),
        queryClient.invalidateQueries({ queryKey: ["confessionals", seasonId] }),
      ]);
    },
    onError: (error) => {
      setControlError(error instanceof Error ? error.message : "Simulation control failed");
    },
  });

  const runControl = (path: string) => {
    controlMutation.mutate(path);
  };

  return (
    <div className="grid gap-6 xl:grid-cols-[1.35fr_0.9fr]">
      <Panel title="House View" subtitle="Original pixel-art viewport on top of a state-driven simulation with Director pacing and persisted social state.">
        <StatStrip
          items={[
            { label: "Tick", value: state.data?.tick_number ?? 0 },
            { label: "Status", value: state.data?.status ?? "offline" },
            { label: "Director", value: state.data?.director_mode ?? "natural flow" },
            { label: "Tension", value: state.data?.current_tension ?? 0, tone: "danger" },
          ]}
        />
        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            className="rounded-full border border-accent/40 bg-accent/10 px-4 py-2 font-display text-xs uppercase tracking-[0.16em] text-accent transition hover:bg-accent/20 disabled:opacity-50"
            onClick={() => runControl(`/api/seasons/${seasonId}/simulation/start`)}
            disabled={controlMutation.isPending || state.data?.status === "running"}
          >
            Start
          </button>
          <button
            type="button"
            className="rounded-full border border-white/15 bg-white/5 px-4 py-2 font-display text-xs uppercase tracking-[0.16em] text-white/75 transition hover:bg-white/10 disabled:opacity-50"
            onClick={() => runControl(`/api/seasons/${seasonId}/simulation/pause`)}
            disabled={controlMutation.isPending || state.data?.status !== "running"}
          >
            Pause
          </button>
          <button
            type="button"
            className="rounded-full border border-white/15 bg-white/5 px-4 py-2 font-display text-xs uppercase tracking-[0.16em] text-white/75 transition hover:bg-white/10 disabled:opacity-50"
            onClick={() => runControl(`/api/seasons/${seasonId}/simulation/resume`)}
            disabled={controlMutation.isPending || state.data?.status === "running"}
          >
            Resume
          </button>
          <button
            type="button"
            className="rounded-full border border-success/30 bg-success/10 px-4 py-2 font-display text-xs uppercase tracking-[0.16em] text-success transition hover:bg-success/20 disabled:opacity-50"
            onClick={() => runControl(`/api/seasons/${seasonId}/simulation/tick`)}
            disabled={controlMutation.isPending}
          >
            Single Tick
          </button>
          <button
            type="button"
            className="rounded-full border border-white/15 bg-white/5 px-4 py-2 font-display text-xs uppercase tracking-[0.16em] text-white/75 transition hover:bg-white/10 disabled:opacity-50"
            onClick={() => runControl(`/api/seasons/${seasonId}/simulation/ticks/6`)}
            disabled={controlMutation.isPending}
          >
            Run 6 Ticks
          </button>
        </div>
        <p className="mt-4 text-sm text-white/55">
          Each tick now updates relationship deltas, contestant states, objective progress, memories, highlights, and confessionals.
        </p>
        <div className="mt-4">
          <StatusMessage error={controlError ?? rooms.error ?? contestants.error ?? state.error ?? events.error} />
        </div>
        <div className="mt-5">
          <PhaserHouseCanvas
            rooms={rooms.data ?? []}
            contestants={contestants.data ?? []}
            activeRoomCode={focusRoomCode}
            activeActorIds={activeActorIds}
          />
        </div>
        <article className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">
            {latestEvent ? `Tick ${latestEvent.tick_number} · ${latestEvent.payload_json.room_name ?? focusRoomCode ?? "House"}` : "Awaiting first beat"}
          </p>
          <p className="mt-2 text-sm text-white/85">
            {latestEvent?.summary ?? "Start the simulation or run a manual tick to generate the first beat."}
          </p>
          {latestEvent ? (
            <>
              <p className="mt-2 text-xs text-white/55">
                Actors: {(latestEvent.payload_json.actor_names ?? []).join(", ") || "No cast focus"} · Visibility{" "}
                {latestEvent.payload_json.visibility ?? "public"}
              </p>
              <p className="mt-2 text-xs text-white/45">
                Director {latestEvent.payload_json.director_mode ?? "none"} · Tension {latestEvent.tension_score.toFixed(2)}
              </p>
              {latestEvent.payload_json.director_reason ? (
                <p className="mt-2 text-xs text-white/45">{latestEvent.payload_json.director_reason}</p>
              ) : null}
            </>
          ) : null}
        </article>
      </Panel>

      <div className="space-y-6">
        <Panel title="Core State" subtitle="Live contestant state and memory stack, ordered by current visibility.">
          <StatusMessage error={contestantStates.error ?? memories.error} />
          <div className="space-y-3">
            {liveStates.map((entry) => (
              <article key={entry.contestant_id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
                  {entry.display_name} · {entry.room_code ?? "off-grid"}
                </p>
                <p className="mt-2 text-xs text-white/55">{entry.current_focus}</p>
                <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-white/70">
                  <span>Energy {entry.energy.toFixed(1)}</span>
                  <span>Stress {entry.stress.toFixed(1)}</span>
                  <span>Suspicion {entry.suspicion.toFixed(1)}</span>
                  <span>Confidence {entry.confidence.toFixed(1)}</span>
                </div>
                <p className="mt-3 text-xs text-white/45">
                  Public appeal {(entry.status_effects_json?.popularity?.public_appeal ?? 0).toFixed(1)} · Drama value{" "}
                  {(entry.status_effects_json?.popularity?.drama_value ?? 0).toFixed(1)}
                </p>
              </article>
            ))}
            {hotMemories.length ? (
              <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Memory Stack</p>
                <div className="mt-3 space-y-2 text-sm text-white/75">
                  {hotMemories.map((memory) => (
                    <div key={memory.id}>
                      <span className="font-display text-[11px] uppercase tracking-[0.18em] text-white/45">
                        {memory.contestant_name} · {memory.memory_type} · salience {memory.salience.toFixed(2)}
                      </span>
                      <p>{memory.summary}</p>
                    </div>
                  ))}
                </div>
              </article>
            ) : null}
          </div>
        </Panel>

        <Panel title="Objective Radar" subtitle="Active public and hidden objectives with current progress.">
          <StatusMessage error={objectives.error} empty={highlightedObjectives.length ? undefined : "No active objectives yet."} />
          <div className="space-y-3">
            {highlightedObjectives.map((objective) => (
              <article key={objective.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">{objective.contestant_name}</p>
                <p className="mt-2 text-sm text-white/80">{objective.title}</p>
                <p className="mt-2 text-xs text-white/45">
                  Priority {objective.priority.toFixed(1)} · Progress {(objective.progress * 100).toFixed(0)}% · {objective.duration_ticks} ticks left
                </p>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Highlights + Confessionals" subtitle="What the show would surface versus what the diary room is already exposing.">
          <StatusMessage error={highlights.error ?? confessionals.error} />
          <div className="space-y-3">
            {topHighlights.map((highlight) => (
              <article key={highlight.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
                  {highlight.category} · score {highlight.score.toFixed(2)}
                </p>
                <p className="mt-2 text-sm text-white/80">{highlight.title}</p>
                <p className="mt-2 text-xs text-white/55">{highlight.summary}</p>
              </article>
            ))}
            {latestConfessionals.map((confessional) => (
              <article key={confessional.id} className="rounded-2xl border border-danger/20 bg-danger/10 p-4">
                <p className="font-display text-xs uppercase tracking-[0.18em] text-danger">{confessional.contestant_name} confessional</p>
                <p className="mt-2 text-sm text-white/80">{confessional.public_transcript}</p>
                <p className="mt-2 text-xs text-white/45">
                  Contradictions {confessional.contradiction_flags_json.join(", ") || "none"} · Shadow{" "}
                  {confessional.shadow_flags_json.join(", ") || "none"}
                </p>
              </article>
            ))}
            {!topHighlights.length && !latestConfessionals.length ? <StatusMessage empty="No highlights or confessionals yet." /> : null}
          </div>
        </Panel>
      </div>
    </div>
  );
}
