import { RetroShell } from "@/components/retro-shell";
import { VipLivePanel } from "@/components/vip-live-panel";

export default function VipPage() {
  return (
    <RetroShell eyebrow="Premium" title="VIP Live">
      <VipLivePanel />
    </RetroShell>
  );
}

