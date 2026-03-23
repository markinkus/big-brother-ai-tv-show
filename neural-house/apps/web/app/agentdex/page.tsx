import { AgentDexGrid } from "@/components/agentdex-grid";
import { RetroShell } from "@/components/retro-shell";

export default function AgentDexPage() {
  return (
    <RetroShell eyebrow="Profiles" title="AgentDex">
      <AgentDexGrid />
    </RetroShell>
  );
}

