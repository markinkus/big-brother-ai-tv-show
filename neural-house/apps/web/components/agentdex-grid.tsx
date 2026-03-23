"use client";

import { useQuery } from "@tanstack/react-query";

import { apiGet } from "@/lib/api";
import { PixelCharacter } from "@/components/pixel-character";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

type Contestant = {
  id: number;
  display_name: string;
  archetype: string;
  public_goal: string;
  hidden_goal_summary: string;
  speech_style: string;
  persona_card_id: number | null;
  skin_palette?: string;
  skin_accent?: string;
  skin_silhouette?: string;
  hair_style?: string;
  avatar_seed?: number;
};

function derivePreviewSeed(contestant: Contestant) {
  const material = [
    contestant.display_name,
    contestant.archetype,
    contestant.skin_palette ?? "studio_blue",
    contestant.skin_accent ?? "gold",
    contestant.skin_silhouette ?? "host-ready",
    contestant.hair_style ?? "crown",
    String(contestant.avatar_seed ?? contestant.id * 31),
  ].join("|");
  return Array.from(material).reduce((sum, char) => sum + char.charCodeAt(0), 0);
}

function silhouetteStyle(silhouette?: string) {
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

export function AgentDexGrid() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const contestants = useQuery({
    queryKey: ["contestants", seasonId],
    queryFn: async () => (await apiGet<Contestant[]>(`/api/seasons/${seasonId}/contestants`)).data ?? [],
  });

  return (
    <Panel title="AgentDex" subtitle="Contestant profile shell linked to persona-card lineage and live state.">
      <StatusMessage error={contestants.error} empty={contestants.data?.length ? undefined : "No contestants loaded."} />
      <div className="grid gap-4 lg:grid-cols-2">
        {(contestants.data ?? []).map((contestant) => (
          <article key={contestant.id} className="rounded-3xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center gap-4">
              <div className="rounded-2xl border border-white/10 bg-black/25 p-2" style={silhouetteStyle(contestant.skin_silhouette)}>
                <PixelCharacter
                  accentKey={contestant.skin_accent ?? "gold"}
                  hairStyle={contestant.hair_style ?? "crown"}
                  paletteKey={contestant.skin_palette ?? "studio_blue"}
                  seed={derivePreviewSeed(contestant)}
                  scale={2}
                  shadow={false}
                  silhouette={contestant.skin_silhouette ?? "host-ready"}
                  variant="portrait"
                />
              </div>
              <div>
                <p className="font-display text-sm uppercase tracking-[0.18em] text-accent">{contestant.display_name}</p>
                <p className="mt-1 text-sm text-white/70">{contestant.archetype} · {contestant.speech_style}</p>
              </div>
            </div>
            <p className="mt-4 text-sm text-white/80">{contestant.public_goal}</p>
            <div className="mt-4 grid grid-cols-2 gap-2 text-[10px] uppercase tracking-[0.16em] text-white/50">
              <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2">
                Palette {contestant.skin_palette ?? "studio_blue"}
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2">
                Accent {contestant.skin_accent ?? "gold"}
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2">
                Hair {contestant.hair_style ?? "crown"}
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-2">
                Silhouette {contestant.skin_silhouette ?? "host-ready"}
              </div>
            </div>
            <div className="mt-3 rounded-2xl border border-white/10 bg-white/5 p-3 text-xs uppercase tracking-[0.18em] text-white/50">
              Persona Card {contestant.persona_card_id ?? "unlinked"}
            </div>
          </article>
        ))}
      </div>
    </Panel>
  );
}
