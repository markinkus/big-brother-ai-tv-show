"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiGet, apiPost } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

type LiveSegment = {
  slot: string;
  headline: string;
  summary: string;
  tone: string;
  target_names: string[];
};

type AudiencePulse = {
  cluster: string;
  leaning: string;
  mood: string;
  intensity: number;
};

type WeeklyLive = {
  season_id: number;
  tick_number: number;
  presenter_intro: string;
  commentator_panels: string[];
  segments: LiveSegment[];
  audience_pulse: AudiencePulse[];
  scoreboard: string[];
};

export function LiveStudioBoard() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const queryClient = useQueryClient();
  const livePack = useQuery({
    queryKey: ["weekly-live", seasonId],
    queryFn: async () => (await apiGet<WeeklyLive>(`/api/seasons/${seasonId}/live/latest`)).data,
    refetchInterval: 5_000,
  });
  const runShow = useMutation({
    mutationFn: async () => apiPost<WeeklyLive>(`/api/seasons/${seasonId}/live/run-weekly-show`),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["weekly-live", seasonId] });
    },
  });

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      <Panel title="Presenter Panel" subtitle="Structured live pack generated from persisted highlights, confessionals, and relationship pressure.">
        <button
          type="button"
          className="mb-4 rounded-2xl border border-accent/40 bg-accent px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-black"
          onClick={() => runShow.mutate()}
        >
          Run Weekly Live
        </button>
        <StatusMessage error={livePack.error ?? runShow.data?.error} />
        <p className="text-sm text-white/75">{livePack.data?.presenter_intro ?? "Weekly live pack will appear here once the season has readable state."}</p>
        <div className="mt-4 space-y-3">
          {(livePack.data?.segments ?? []).slice(0, 3).map((segment) => (
            <article key={`${segment.slot}-${segment.headline}`} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">{segment.slot}</p>
              <p className="mt-2 text-sm text-white/85">{segment.headline}</p>
              <p className="mt-2 text-xs text-white/55">{segment.summary}</p>
            </article>
          ))}
        </div>
      </Panel>

      <Panel title="Commentators" subtitle="Two lanes of deterministic commentary, plus live show segment stack.">
        <div className="space-y-3">
          {(livePack.data?.commentator_panels ?? []).map((panel) => (
            <article key={panel} className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-white/75">
              {panel}
            </article>
          ))}
          {(livePack.data?.segments ?? []).slice(3).map((segment) => (
            <article key={`${segment.slot}-${segment.headline}`} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
                {segment.slot} · {segment.tone}
              </p>
              <p className="mt-2 text-sm text-white/80">{segment.summary}</p>
              <p className="mt-2 text-xs text-white/45">{segment.target_names.join(", ") || "House-wide beat"}</p>
            </article>
          ))}
        </div>
      </Panel>

      <Panel title="Audience Feed" subtitle="Synthetic audience pulse and pressure scoreboard derived from the current social map.">
        <div className="space-y-3">
          {(livePack.data?.audience_pulse ?? []).map((pulse) => (
            <article key={pulse.cluster} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">{pulse.cluster}</p>
              <p className="mt-2 text-sm text-white/80">{pulse.leaning}</p>
              <p className="mt-2 text-xs text-white/45">
                Mood {pulse.mood} · intensity {pulse.intensity.toFixed(2)}
              </p>
            </article>
          ))}
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Pressure Scoreboard</p>
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {(livePack.data?.scoreboard ?? []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        </div>
      </Panel>
    </div>
  );
}
