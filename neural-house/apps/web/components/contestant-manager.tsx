"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { FormEvent, useEffect, useState } from "react";

import { apiGet, apiPatch, apiPost } from "@/lib/api";
import { PixelCharacter } from "@/components/pixel-character";
import { hairStyleOptions, pixelAccentPalettes, pixelBodyPalettes, silhouetteOptions } from "@/lib/pixel-art";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

type Contestant = {
  id: number;
  display_name: string;
  archetype: string;
  public_bio: string;
  public_goal: string;
  hidden_goal_summary: string;
  speech_style: string;
  active: boolean;
  skin_palette?: string;
  skin_accent?: string;
  skin_silhouette?: string;
  hair_style?: string;
  avatar_seed?: number;
};

type ContestantForm = {
  display_name: string;
  archetype: string;
  public_bio: string;
  public_goal: string;
  hidden_goal_summary: string;
  speech_style: string;
  avatar_seed: number;
  skin_palette: string;
  skin_accent: string;
  skin_silhouette: string;
  hair_style: string;
};

function derivedPreviewSeed(form: ContestantForm) {
  const material = [
    form.display_name || "NEURAL",
    form.archetype,
    form.skin_palette,
    form.skin_accent,
    form.skin_silhouette,
    form.hair_style,
    String(form.avatar_seed),
  ].join("|");
  return Array.from(material).reduce((sum, char) => sum + char.charCodeAt(0), 0);
}

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

const defaultForm = {
  display_name: "",
  archetype: "Diplomat",
  public_bio: "",
  public_goal: "",
  hidden_goal_summary: "",
  speech_style: "measured and calm",
  avatar_seed: 0,
  skin_palette: "studio_blue",
  skin_accent: "gold",
  skin_silhouette: "host-ready",
  hair_style: "crown",
} satisfies ContestantForm;

const bodyPaletteOptions = Object.keys(pixelBodyPalettes);
const accentOptions = Object.keys(pixelAccentPalettes);
const hairOptions = [...hairStyleOptions];

export function ContestantManager() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const queryClient = useQueryClient();
  const [form, setForm] = useState(defaultForm);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const contestants = useQuery({
    queryKey: ["contestants", seasonId],
    queryFn: async () => (await apiGet<Contestant[]>(`/api/seasons/${seasonId}/contestants`)).data ?? [],
  });

  const createMutation = useMutation({
    mutationFn: async () => apiPost<Contestant>(`/api/seasons/${seasonId}/contestants`, form),
    onSuccess: async () => {
      setForm(defaultForm);
      setSelectedId(null);
      await queryClient.invalidateQueries({ queryKey: ["contestants", seasonId] });
    },
  });

  const patchMutation = useMutation({
    mutationFn: async ({ contestantId, payload }: { contestantId: number; payload: Partial<ContestantForm> & { active?: boolean } }) =>
      apiPatch<Contestant>(`/api/contestants/${contestantId}`, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["contestants", seasonId] });
    },
  });

  useEffect(() => {
    if (selectedId === null) {
      return;
    }
    const contestant = (contestants.data ?? []).find((entry) => entry.id === selectedId);
    if (!contestant) {
      return;
    }
    setForm({
      display_name: contestant.display_name,
      archetype: contestant.archetype,
      public_bio: contestant.public_bio,
      public_goal: contestant.public_goal,
      hidden_goal_summary: contestant.hidden_goal_summary,
      speech_style: contestant.speech_style,
      avatar_seed: contestant.avatar_seed ?? 0,
      skin_palette: contestant.skin_palette ?? "studio_blue",
      skin_accent: contestant.skin_accent ?? "gold",
      skin_silhouette: contestant.skin_silhouette ?? "host-ready",
      hair_style: contestant.hair_style ?? "crown",
    });
  }, [contestants.data, selectedId]);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (selectedId !== null) {
      patchMutation.mutate({ contestantId: selectedId, payload: form });
      return;
    }
    createMutation.mutate();
  }

  const previewSeed = derivedPreviewSeed(form);

  return (
    <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
      <Panel title="Contestant Editor" subtitle="Create or update a cast member. Identity, story, and skin are edited in separate blocks.">
        <form className="space-y-4" onSubmit={submit}>
          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Identity</p>
              <p className="mt-2 text-sm text-white/60">Basic cast ID and public framing.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Display Name</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.display_name}
                  onChange={(event) => setForm((current) => ({ ...current, display_name: event.target.value }))}
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
            <div className="grid gap-4 md:grid-cols-2">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Avatar Seed</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  type="number"
                  value={form.avatar_seed}
                  onChange={(event) => setForm((current) => ({ ...current, avatar_seed: Number(event.target.value) }))}
                />
              </label>
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Speech Style</span>
                <input
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.speech_style}
                  onChange={(event) => setForm((current) => ({ ...current, speech_style: event.target.value }))}
                />
              </label>
            </div>
          </section>

          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Story</p>
              <p className="mt-2 text-sm text-white/60">What the house sees publicly versus what the contestant is hiding.</p>
            </div>
            <label className="block">
              <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Public Bio</span>
              <textarea
                className="min-h-24 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                value={form.public_bio}
                onChange={(event) => setForm((current) => ({ ...current, public_bio: event.target.value }))}
              />
            </label>
            <label className="block">
              <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Public Goal</span>
              <textarea
                className="min-h-20 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                value={form.public_goal}
                onChange={(event) => setForm((current) => ({ ...current, public_goal: event.target.value }))}
              />
            </label>
            <label className="block">
              <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Hidden Goal</span>
              <textarea
                className="min-h-20 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                value={form.hidden_goal_summary}
                onChange={(event) => setForm((current) => ({ ...current, hidden_goal_summary: event.target.value }))}
              />
            </label>
          </section>

          <section className="space-y-3 rounded-3xl border border-white/10 bg-black/20 p-4">
            <div>
              <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Skin</p>
              <p className="mt-2 text-sm text-white/60">These controls drive the live pixel preview and the saved record.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-4">
              <label className="block">
                <span className="mb-2 block font-display text-xs uppercase tracking-[0.2em] text-white/55">Palette</span>
                <select
                  className="w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm outline-none"
                  value={form.skin_palette}
                  onChange={(event) => setForm((current) => ({ ...current, skin_palette: event.target.value }))}
                >
                  {bodyPaletteOptions.map((item) => (
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
                  value={form.skin_accent}
                  onChange={(event) => setForm((current) => ({ ...current, skin_accent: event.target.value }))}
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
                  value={form.skin_silhouette}
                  onChange={(event) => setForm((current) => ({ ...current, skin_silhouette: event.target.value }))}
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
                  value={form.hair_style}
                  onChange={(event) => setForm((current) => ({ ...current, hair_style: event.target.value }))}
                >
                  {hairOptions.map((item) => (
                    <option key={item} value={item}>
                      {item}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          </section>

          <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Live Pixel Preview</p>
            <div className="mt-4 flex items-center gap-5">
              <div className="rounded-2xl border border-white/10 bg-black/30 p-3" style={silhouetteStyle(form.skin_silhouette)}>
                <PixelCharacter
                  accentKey={form.skin_accent}
                  hairStyle={form.hair_style}
                  paletteKey={form.skin_palette}
                  seed={previewSeed}
                  scale={4}
                  silhouette={form.skin_silhouette}
                  variant="portrait"
                />
              </div>
              <div className="space-y-2 text-xs uppercase tracking-[0.16em] text-white/55">
                <div>Palette {form.skin_palette}</div>
                <div>Accent {form.skin_accent}</div>
                <div>Hair {form.hair_style}</div>
                <div>Silhouette {form.skin_silhouette}</div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/60">
            {selectedId !== null
              ? "Editing the selected contestant. Submit updates the story and skin fields shown above."
              : "Create flow still uses the same API, now with the skin editor driving the new fields in the form."}
          </div>
          <button
            type="submit"
            className="rounded-2xl border border-accent/40 bg-accent px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-black"
          >
            {selectedId !== null ? "Update Contestant" : "Create Contestant"}
          </button>
          {selectedId !== null ? (
            <button
              type="button"
              className="ml-3 rounded-2xl border border-white/10 px-4 py-3 font-display text-xs uppercase tracking-[0.2em] text-white/70"
              onClick={() => {
                setSelectedId(null);
                setForm(defaultForm);
              }}
            >
              Clear Selection
            </button>
          ) : null}
        </form>
      </Panel>

      <Panel title="Current Cast" subtitle="First deliverable cast list and basic deactivation action.">
        <StatusMessage
          error={
            contestants.error ??
            (createMutation.data?.error || null) ??
            (patchMutation.data?.error || null)
          }
          empty={contestants.data?.length ? undefined : "No contestants yet."}
        />
        <div className="space-y-3">
          {(contestants.data ?? []).map((contestant) => (
            <article
              key={contestant.id}
              className={`rounded-2xl border p-4 ${
                selectedId === contestant.id ? "border-accent/60 bg-accent/10" : "border-white/10 bg-black/20"
              }`}
              onClick={() => setSelectedId(contestant.id)}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-4">
                  <div className="rounded-2xl border border-white/10 bg-black/30 p-2">
                    <PixelCharacter
                      accentKey={contestant.skin_accent ?? "gold"}
                      hairStyle={contestant.hair_style ?? "crown"}
                      paletteKey={contestant.skin_palette ?? "studio_blue"}
                      seed={contestant.avatar_seed ?? contestant.id * 29}
                      scale={2}
                      shadow={false}
                      silhouette={contestant.skin_silhouette ?? "host-ready"}
                      variant="portrait"
                    />
                  </div>
                  <div>
                    <p className="font-display text-sm uppercase tracking-[0.18em] text-accent">{contestant.display_name}</p>
                    <p className="mt-1 text-sm text-white/70">{contestant.archetype}</p>
                    <p className="mt-3 text-sm text-white/80">{contestant.public_bio}</p>
                    <div className="mt-3 grid grid-cols-2 gap-2 text-[10px] uppercase tracking-[0.16em] text-white/45">
                      <span>Palette {contestant.skin_palette ?? "studio_blue"}</span>
                      <span>Accent {contestant.skin_accent ?? "gold"}</span>
                      <span>Hair {contestant.hair_style ?? "crown"}</span>
                      <span>Silhouette {contestant.skin_silhouette ?? "host-ready"}</span>
                    </div>
                  </div>
                </div>
                <button
                  type="button"
                  className="rounded-2xl border border-white/10 px-3 py-2 text-xs uppercase tracking-[0.2em] text-white/70"
                  onClick={(event) => {
                    event.stopPropagation();
                    patchMutation.mutate({ contestantId: contestant.id, payload: { active: false } });
                  }}
                >
                  Deactivate
                </button>
              </div>
            </article>
          ))}
        </div>
      </Panel>
    </div>
  );
}
