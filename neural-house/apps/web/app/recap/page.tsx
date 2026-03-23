import { EpisodeRecapBoard } from "@/components/episode-recap-board";
import { RetroShell } from "@/components/retro-shell";

export default function RecapPage() {
  return (
    <RetroShell eyebrow="Episode Layer" title="Recap">
      <EpisodeRecapBoard />
    </RetroShell>
  );
}
