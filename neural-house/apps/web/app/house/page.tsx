import { HouseDashboard } from "@/components/house-dashboard";
import { RetroShell } from "@/components/retro-shell";

export default function HousePage() {
  return (
    <RetroShell eyebrow="Simulation View" title="House Map">
      <HouseDashboard />
    </RetroShell>
  );
}

