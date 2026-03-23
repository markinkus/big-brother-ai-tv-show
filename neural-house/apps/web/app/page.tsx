import Image from "next/image";
import Link from "next/link";

import { Panel } from "@/components/panel";
import { RetroShell } from "@/components/retro-shell";

const destinations = [
  ["Start Season", "/house"],
  ["Generate Persona Cards", "/persona-cards"],
  ["Run Audition", "/audition"],
  ["Manage Contestants", "/contestants"],
  ["Watch Simulation", "/house"],
  ["Watch VIP Live", "/vip"],
  ["Newsroom", "/newsroom"],
  ["Watch Weekly Live", "/live"],
  ["Recap", "/recap"],
];

export default function TitleScreen() {
  return (
    <RetroShell eyebrow="Title Screen" title="Neural House">
      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <Panel
          title="Show Core"
          subtitle="State-driven social simulation first. Entertainment output is generated from house state, not the other way around."
        >
          <div className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
            <div className="rounded-3xl border border-white/10 bg-black/20 p-6">
              <p className="font-display text-3xl uppercase tracking-[0.22em] text-accent">The AI Reality Show Simulator</p>
              <p className="mt-5 max-w-2xl text-base leading-7 text-white/75">
                Contestants live in a deterministic social machine. The House pushes pacing, the newsroom shapes public narrative,
                and the VIP layer exposes premium live observability without dumping private hidden truth.
              </p>
              <p className="mt-5 text-sm uppercase tracking-[0.18em] text-white/45">
                New in this phase: configurable audition agent studio with provider/model settings, character traits, and skin playback.
              </p>
            </div>
            <div className="overflow-hidden rounded-3xl border border-white/10 bg-black/20">
              <Image
                alt="Official Neural House poster"
                className="h-full w-full object-cover"
                height={1181}
                priority
                src="/NeuralHouse.png"
                width={828}
              />
            </div>
          </div>
        </Panel>
        <Panel title="Navigate" subtitle="First-deliverable screen shell.">
          <div className="grid gap-3">
            {destinations.map(([label, href]) => (
              <Link
                key={href}
                href={href}
                className="rounded-2xl border border-white/10 bg-black/20 px-4 py-4 font-display text-xs uppercase tracking-[0.22em] text-white/80 transition hover:border-accent/40 hover:text-accent"
              >
                {label}
              </Link>
            ))}
          </div>
        </Panel>
      </div>
    </RetroShell>
  );
}
