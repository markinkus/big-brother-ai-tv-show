import { NewsroomFeed } from "@/components/newsroom-feed";
import { RetroShell } from "@/components/retro-shell";

export default function NewsroomPage() {
  return (
    <RetroShell eyebrow="Narrative Layer" title="Newsroom">
      <NewsroomFeed />
    </RetroShell>
  );
}

