import { PersonaCardStudio } from "@/components/persona-card-studio";
import { RetroShell } from "@/components/retro-shell";

export default function PersonaCardsPage() {
  return (
    <RetroShell eyebrow="Casting" title="Persona Card Generator">
      <PersonaCardStudio />
    </RetroShell>
  );
}

