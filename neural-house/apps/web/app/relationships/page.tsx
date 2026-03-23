import { RelationshipBoard } from "@/components/relationship-board";
import { RetroShell } from "@/components/retro-shell";

export default function RelationshipsPage() {
  return (
    <RetroShell eyebrow="Social Graph" title="Relationships">
      <RelationshipBoard />
    </RetroShell>
  );
}

