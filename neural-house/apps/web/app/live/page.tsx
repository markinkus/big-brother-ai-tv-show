import { LiveStudioBoard } from "@/components/live-studio-board";
import { RetroShell } from "@/components/retro-shell";

export default function LivePage() {
  return (
    <RetroShell eyebrow="Studio" title="Weekly Live">
      <LiveStudioBoard />
    </RetroShell>
  );
}
