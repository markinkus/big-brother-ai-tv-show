import { AuditionStudio } from "@/components/audition-studio";
import { RetroShell } from "@/components/retro-shell";

export default function AuditionPage() {
  return (
    <RetroShell eyebrow="Provino" title="TV Audition Studio">
      <AuditionStudio />
    </RetroShell>
  );
}
