"use client";

import { useQuery } from "@tanstack/react-query";

import { apiGet } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

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
};

type Article = {
  id: number;
  title: string;
  dek: string;
};

export function EpisodeRecapBoard() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const highlights = useQuery({
    queryKey: ["recap-highlights", seasonId],
    queryFn: async () => (await apiGet<Highlight[]>(`/api/seasons/${seasonId}/highlights`)).data ?? [],
    refetchInterval: 5_000,
  });
  const confessionals = useQuery({
    queryKey: ["recap-confessionals", seasonId],
    queryFn: async () => (await apiGet<Confessional[]>(`/api/seasons/${seasonId}/confessionals`)).data ?? [],
    refetchInterval: 5_000,
  });
  const articles = useQuery({
    queryKey: ["recap-articles", seasonId],
    queryFn: async () => (await apiGet<Article[]>(`/api/seasons/${seasonId}/articles`)).data ?? [],
    refetchInterval: 5_000,
  });

  return (
    <Panel title="Episode Cards" subtitle="Daily/weekly recap derived from persisted highlights, confessionals, and newsroom framing.">
      <StatusMessage error={highlights.error ?? confessionals.error ?? articles.error} empty={highlights.data?.length ? undefined : "No recap cards yet."} />
      <div className="grid gap-4 lg:grid-cols-3">
        {(highlights.data ?? []).slice(0, 3).map((highlight) => (
          <article key={highlight.id} className="rounded-3xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">
              {highlight.category} · score {highlight.score.toFixed(2)}
            </p>
            <p className="mt-3 text-sm text-white/85">{highlight.title}</p>
            <p className="mt-3 text-sm text-white/65">{highlight.summary}</p>
          </article>
        ))}
      </div>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <article className="rounded-3xl border border-white/10 bg-black/20 p-4">
          <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Confessional Pressure</p>
          <div className="mt-3 space-y-3 text-sm text-white/75">
            {(confessionals.data ?? []).slice(0, 3).map((confessional) => (
              <div key={confessional.id}>
                <p className="font-display text-[11px] uppercase tracking-[0.18em] text-white/45">{confessional.contestant_name}</p>
                <p>{confessional.public_transcript}</p>
                <p className="mt-1 text-xs text-white/35">
                  Contradictions {confessional.contradiction_flags_json.join(", ") || "none"}
                </p>
              </div>
            ))}
          </div>
        </article>
        <article className="rounded-3xl border border-white/10 bg-black/20 p-4">
          <p className="font-display text-xs uppercase tracking-[0.18em] text-accent">Newsroom Echo</p>
          <div className="mt-3 space-y-3 text-sm text-white/75">
            {(articles.data ?? []).slice(0, 3).map((article) => (
              <div key={article.id}>
                <p className="font-display text-[11px] uppercase tracking-[0.18em] text-white/45">{article.title}</p>
                <p>{article.dek}</p>
              </div>
            ))}
          </div>
        </article>
      </div>
    </Panel>
  );
}
