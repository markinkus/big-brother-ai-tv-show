"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";

import { apiGet, apiPost } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatStrip } from "@/components/stat-strip";
import { StatusMessage } from "@/components/status-message";

type Room = {
  code: string;
  name: string;
};

type VipRoomSummary = {
  room_code: string;
  room_name: string;
  occupant_names: string[];
  activity_summary: string;
  tension: number;
};

type VipState = {
  season_id: number;
  tick_number: number;
  selected_room_code: string | null;
  tension: number;
  active_alliances: string[];
  active_conflicts: string[];
  recent_events: string[];
  recent_highlights: string[];
  last_change_digest: string[];
  room_summaries: VipRoomSummary[];
  visibility_policy: string;
  rooms: Room[];
};

type VipSession = {
  id: number;
  selected_room_code: string | null;
};

export function VipLivePanel() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const vipRoom = useNeuralHouseStore((state) => state.vipRoom);
  const setVipRoom = useNeuralHouseStore((state) => state.setVipRoom);
  const queryClient = useQueryClient();

  const vipState = useQuery({
    queryKey: ["vip-state", seasonId, vipRoom],
    queryFn: async () =>
      (await apiGet<VipState>(`/api/seasons/${seasonId}/vip/state?premium_user_id=1${vipRoom ? `&selected_room_code=${vipRoom}` : ""}`)).data,
    refetchInterval: 3_000,
  });

  const session = useMutation({
    mutationFn: async () =>
      apiPost<VipSession>(`/api/seasons/${seasonId}/vip/session/start`, {
        premium_user_id: 1,
        selected_room_code: vipRoom,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["vip-state", seasonId, vipRoom] });
    },
  });

  const activeRoomSummary = useMemo(
    () => (vipState.data?.room_summaries ?? []).find((room) => room.room_code === (vipState.data?.selected_room_code ?? vipRoom ?? "")) ?? null,
    [vipRoom, vipState.data],
  );

  return (
    <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <Panel title="VIP Live Zone" subtitle="Premium spectator surface with room focus, recent changes, and protected public-pattern inference.">
        <div className="mb-4 flex flex-wrap gap-2">
          {(vipState.data?.rooms ?? []).map((room) => (
            <button
              key={room.code}
              type="button"
              className={`rounded-2xl border px-3 py-2 font-display text-xs uppercase tracking-[0.18em] ${
                vipRoom === room.code ? "border-accent/60 bg-accent/15 text-accent" : "border-white/10 text-white/70"
              }`}
              onClick={() => setVipRoom(room.code)}
            >
              {room.name}
            </button>
          ))}
        </div>
        <button
          type="button"
          className="rounded-2xl border border-accent/40 bg-accent px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-black"
          onClick={() => session.mutate()}
        >
          Start VIP Session
        </button>
        <p className="mt-4 text-sm text-white/55">
          VIP reads the same house state as the show, but preserves private asymmetry by default. Confessional truth remains masked unless admin rules change.
        </p>
        <StatusMessage error={vipState.error ?? session.data?.error} />
        <div className="mt-5">
          <StatStrip
            items={[
              { label: "Tick", value: vipState.data?.tick_number ?? 0 },
              { label: "Focus", value: vipState.data?.selected_room_code ?? vipRoom ?? "all rooms" },
              { label: "Tension", value: vipState.data?.tension ?? 0, tone: "danger" },
              { label: "Access", value: "premium", tone: "success" },
            ]}
          />
        </div>

        {activeRoomSummary ? (
          <article className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
              Active Room · {activeRoomSummary.room_name}
            </p>
            <p className="mt-2 text-sm text-white/80">{activeRoomSummary.activity_summary}</p>
            <p className="mt-2 text-xs text-white/45">
              Occupants {activeRoomSummary.occupant_names.join(", ") || "none"} · Tension {activeRoomSummary.tension.toFixed(2)}
            </p>
          </article>
        ) : null}
      </Panel>

      <Panel title="Spectator Intelligence" subtitle="Room-by-room summaries, current alliances, active conflicts, and the last meaningful changes.">
        <div className="space-y-3">
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Visibility Policy</p>
            <p className="mt-3 text-sm text-white/75">{vipState.data?.visibility_policy ?? "Loading VIP rules..."}</p>
          </article>
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Alliances</p>
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {(vipState.data?.active_alliances ?? []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Conflicts</p>
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {(vipState.data?.active_conflicts ?? []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Last Change Digest</p>
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {(vipState.data?.last_change_digest ?? []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Recent Highlights</p>
            <ul className="mt-3 space-y-2 text-sm text-white/75">
              {(vipState.data?.recent_highlights ?? []).map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
          <article className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Room Grid</p>
            <div className="mt-3 space-y-2 text-sm text-white/75">
              {(vipState.data?.room_summaries ?? []).map((room) => (
                <div key={room.room_code} className="rounded-2xl border border-white/10 bg-black/20 p-3">
                  <p className="font-display text-[11px] uppercase tracking-[0.18em] text-white/55">
                    {room.room_name} · tension {room.tension.toFixed(2)}
                  </p>
                  <p className="mt-1">{room.activity_summary}</p>
                </div>
              ))}
            </div>
          </article>
        </div>
      </Panel>
    </div>
  );
}
