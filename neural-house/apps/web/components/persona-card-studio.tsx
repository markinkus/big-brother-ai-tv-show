"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { apiGet, apiPost } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

type PersonaCard = {
  id: number;
  label: string;
  status: string;
  dominant_archetype: string;
  synopsis: string;
  public_pitch: string;
  private_complexity_summary: string;
  trustability_score: number;
  manipulation_susceptibility: number;
};

export function PersonaCardStudio() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const queryClient = useQueryClient();
  const [requestedCount, setRequestedCount] = useState(3);

  const cards = useQuery({
    queryKey: ["persona-cards", seasonId],
    queryFn: async () => (await apiGet<PersonaCard[]>(`/api/seasons/${seasonId}/persona-cards`)).data ?? [],
  });

  const generate = useMutation({
    mutationFn: async () =>
      apiPost<PersonaCard[]>(`/api/seasons/${seasonId}/persona-cards/generate`, {
        requested_count: requestedCount,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["persona-cards", seasonId] });
    },
  });

  const approve = useMutation({
    mutationFn: async (cardId: number) => apiPost<PersonaCard>(`/api/persona-cards/${cardId}/approve`),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["persona-cards", seasonId] });
    },
  });

  const createContestant = useMutation({
    mutationFn: async (cardId: number) =>
      apiPost(`/api/persona-cards/${cardId}/create-contestant`, {
        display_name_override: undefined,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["persona-cards", seasonId] });
      await queryClient.invalidateQueries({ queryKey: ["contestants", seasonId] });
    },
  });

  return (
    <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
      <Panel
        title="Generator Controls"
        subtitle="Structured candidate-card generation before contestant instantiation."
      >
        <label className="block">
          <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Requested Count</span>
          <input
            className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
            type="number"
            min={1}
            max={6}
            value={requestedCount}
            onChange={(event) => setRequestedCount(Number(event.target.value))}
          />
        </label>
        <button
          type="button"
          className="mt-4 rounded-2xl border border-accent/40 bg-accent px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-black"
          onClick={() => generate.mutate()}
        >
          Generate Cards
        </button>
        <StatusMessage error={generate.data?.error || approve.data?.error || createContestant.data?.error} />
      </Panel>

      <Panel title="Candidate Cards" subtitle="Approve and convert a persona card into a contestant.">
        <div className="space-y-4">
          {(cards.data ?? []).map((card) => (
            <article key={card.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="font-display text-sm uppercase tracking-[0.18em] text-accent">{card.label}</p>
                  <p className="mt-1 text-xs uppercase tracking-[0.18em] text-white/55">
                    {card.dominant_archetype} · {card.status}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="rounded-2xl border border-white/10 px-3 py-2 text-xs uppercase tracking-[0.2em] text-white/70"
                    onClick={() => approve.mutate(card.id)}
                  >
                    Approve
                  </button>
                  <button
                    type="button"
                    className="rounded-2xl border border-accent/40 px-3 py-2 text-xs uppercase tracking-[0.2em] text-accent"
                    onClick={() => createContestant.mutate(card.id)}
                  >
                    Create Contestant
                  </button>
                </div>
              </div>
              <p className="mt-3 text-sm text-white/80">{card.synopsis}</p>
              <div className="mt-3 grid gap-3 md:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white/70">{card.public_pitch}</div>
                <div className="rounded-2xl border border-white/10 bg-white/5 p-3 text-sm text-white/70">
                  {card.private_complexity_summary}
                </div>
              </div>
            </article>
          ))}
          {!cards.data?.length ? <StatusMessage empty="No persona cards generated yet." /> : null}
        </div>
      </Panel>
    </div>
  );
}

