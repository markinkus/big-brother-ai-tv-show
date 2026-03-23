import { ContestantManager } from "@/components/contestant-manager";
import { RetroShell } from "@/components/retro-shell";

export default function ContestantsPage() {
  return (
    <RetroShell eyebrow="Casting Desk" title="Contestant Editor">
      <ContestantManager />
    </RetroShell>
  );
}

