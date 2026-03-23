"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { apiGet, apiPost } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

type Journalist = {
  id: number;
  display_name: string;
  style: string;
  ideology: string;
  sensationalism: number;
  empathy: number;
};

type Article = {
  id: number;
  journalist_id: number;
  title: string;
  dek: string;
  body: string;
  tone: string;
  stance: string;
  referenced_contestant_ids_json: number[];
};

type Highlight = {
  id: number;
  category: string;
  title: string;
};

type Contestant = {
  id: number;
  display_name: string;
};

export function NewsroomFeed() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const queryClient = useQueryClient();
  const [selectedJournalist, setSelectedJournalist] = useState<string>("all");
  const [selectedTone, setSelectedTone] = useState<string>("all");
  const [selectedContestant, setSelectedContestant] = useState<string>("all");

  const journalists = useQuery({
    queryKey: ["journalists", seasonId],
    queryFn: async () => (await apiGet<Journalist[]>(`/api/seasons/${seasonId}/journalists`)).data ?? [],
  });
  const articles = useQuery({
    queryKey: ["articles", seasonId],
    queryFn: async () => (await apiGet<Article[]>(`/api/seasons/${seasonId}/articles`)).data ?? [],
  });
  const highlights = useQuery({
    queryKey: ["newsroom-highlights", seasonId],
    queryFn: async () => (await apiGet<Highlight[]>(`/api/seasons/${seasonId}/highlights`)).data ?? [],
  });
  const contestants = useQuery({
    queryKey: ["newsroom-contestants", seasonId],
    queryFn: async () => (await apiGet<Contestant[]>(`/api/seasons/${seasonId}/contestants`)).data ?? [],
  });

  const cycle = useMutation({
    mutationFn: async () => apiPost(`/api/seasons/${seasonId}/newsroom/run-cycle`),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["articles", seasonId] });
    },
  });

  const journalistById = useMemo(
    () => new Map((journalists.data ?? []).map((journalist) => [journalist.id, journalist])),
    [journalists.data],
  );
  const contestantById = useMemo(
    () => new Map((contestants.data ?? []).map((contestant) => [contestant.id, contestant.display_name])),
    [contestants.data],
  );
  const tones = useMemo(
    () => Array.from(new Set((articles.data ?? []).map((article) => article.tone))),
    [articles.data],
  );
  const filteredArticles = useMemo(
    () =>
      (articles.data ?? []).filter((article) => {
        if (selectedJournalist !== "all" && article.journalist_id !== Number(selectedJournalist)) {
          return false;
        }
        if (selectedTone !== "all" && article.tone !== selectedTone) {
          return false;
        }
        if (selectedContestant !== "all" && !article.referenced_contestant_ids_json.includes(Number(selectedContestant))) {
          return false;
        }
        return true;
      }),
    [articles.data, selectedContestant, selectedJournalist, selectedTone],
  );
  const trendingNarratives = useMemo(() => {
    const buckets = new Map<string, number>();
    for (const highlight of highlights.data ?? []) {
      buckets.set(highlight.category, (buckets.get(highlight.category) ?? 0) + 1);
    }
    for (const article of articles.data ?? []) {
      buckets.set(article.tone, (buckets.get(article.tone) ?? 0) + 1);
    }
    return Array.from(buckets.entries())
      .sort((left, right) => right[1] - left[1])
      .slice(0, 5);
  }, [articles.data, highlights.data]);

  return (
    <div className="grid gap-6 xl:grid-cols-[0.9fr_1.1fr]">
      <Panel title="Newsroom Desk" subtitle="Journalists read highlights, contradictions, and rivalry shifts to shape public narrative.">
        <button
          type="button"
          className="mb-4 rounded-2xl border border-accent/40 bg-accent px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-black"
          onClick={() => cycle.mutate()}
        >
          Run Newsroom Cycle
        </button>
        <p className="mb-4 text-sm text-white/55">
          The newsroom does not invent hidden truth. It reframes persisted house state into tabloid, analytical, or moralized public stories.
        </p>
        <StatusMessage error={journalists.error ?? cycle.data?.error} />
        <div className="space-y-3">
          {(journalists.data ?? []).map((journalist) => (
            <article key={journalist.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-display text-sm uppercase tracking-[0.18em] text-accent">{journalist.display_name}</p>
              <p className="mt-2 text-sm text-white/75">
                {journalist.style} · {journalist.ideology}
              </p>
              <p className="mt-2 text-xs text-white/45">
                Sensationalism {journalist.sensationalism.toFixed(2)} · Empathy {journalist.empathy.toFixed(2)}
              </p>
            </article>
          ))}
        </div>

        <article className="mt-5 rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Trending Narratives</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {trendingNarratives.map(([label, count]) => (
              <span key={label} className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs uppercase tracking-[0.14em] text-white/65">
                {label} · {count}
              </span>
            ))}
          </div>
        </article>
      </Panel>

      <Panel title="Article Feed" subtitle="Filter by journalist, tone, or contestant to inspect how the public story is being shaped.">
        <div className="mb-4 grid gap-3 md:grid-cols-3">
          <label className="block">
            <span className="mb-2 block font-display text-xs uppercase tracking-[0.18em] text-white/55">Journalist</span>
            <select
              className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
              value={selectedJournalist}
              onChange={(event) => setSelectedJournalist(event.target.value)}
            >
              <option value="all">All desks</option>
              {(journalists.data ?? []).map((journalist) => (
                <option key={journalist.id} value={journalist.id}>
                  {journalist.display_name}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block font-display text-xs uppercase tracking-[0.18em] text-white/55">Tone</span>
            <select
              className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
              value={selectedTone}
              onChange={(event) => setSelectedTone(event.target.value)}
            >
              <option value="all">All tones</option>
              {tones.map((tone) => (
                <option key={tone} value={tone}>
                  {tone}
                </option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block font-display text-xs uppercase tracking-[0.18em] text-white/55">Contestant</span>
            <select
              className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
              value={selectedContestant}
              onChange={(event) => setSelectedContestant(event.target.value)}
            >
              <option value="all">All cast</option>
              {(contestants.data ?? []).map((contestant) => (
                <option key={contestant.id} value={contestant.id}>
                  {contestant.display_name}
                </option>
              ))}
            </select>
          </label>
        </div>
        <StatusMessage error={articles.error ?? highlights.error} empty={filteredArticles.length ? undefined : "No published articles yet."} />
        <div className="space-y-4">
          {filteredArticles.map((article) => (
            <article key={article.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-display text-sm uppercase tracking-[0.18em] text-accent">{article.title}</p>
              <p className="mt-2 text-sm text-white/55">{article.dek}</p>
              <p className="mt-3 text-sm text-white/80">{article.body}</p>
              <p className="mt-3 text-xs uppercase tracking-[0.2em] text-white/45">
                {article.tone} · {article.stance}
              </p>
              <p className="mt-2 text-xs text-white/45">
                Cast focus:{" "}
                {article.referenced_contestant_ids_json.length
                  ? article.referenced_contestant_ids_json.map((contestantId) => contestantById.get(contestantId) ?? `#${contestantId}`).join(", ")
                  : "none"}
              </p>
              <p className="mt-2 text-xs text-white/35">
                Desk: {journalistById.get(article.journalist_id)?.display_name ?? `Journalist ${article.journalist_id}`}
              </p>
            </article>
          ))}
        </div>
      </Panel>
    </div>
  );
}
