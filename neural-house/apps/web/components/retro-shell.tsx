import Link from "next/link";

const navItems = [
  ["Title", "/"],
  ["House", "/house"],
  ["Persona Cards", "/persona-cards"],
  ["Audition", "/audition"],
  ["Contestants", "/contestants"],
  ["AgentDex", "/agentdex"],
  ["Relationships", "/relationships"],
  ["Newsroom", "/newsroom"],
  ["VIP", "/vip"],
  ["Live", "/live"],
  ["Recap", "/recap"],
] as const;

export function RetroShell({
  title,
  eyebrow,
  children,
}: {
  title: string;
  eyebrow: string;
  children: any;
}) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,#203136_0%,#0b1213_58%)] text-ink">
      <div className="mx-auto flex max-w-7xl gap-6 px-4 py-6 lg:px-6">
        <aside className="hidden w-64 shrink-0 rounded-3xl border border-white/10 bg-surface/90 p-4 shadow-panel lg:block">
          <div className="mb-6 rounded-2xl border border-accent/40 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.3em] text-accent">Neural House</p>
            <h1 className="mt-3 font-display text-2xl text-ink">AI Reality Show Simulator</h1>
          </div>
          <nav className="space-y-2">
            {navItems.map(([label, href]) => (
              <Link
                key={href}
                href={href}
                className="block rounded-2xl border border-white/5 bg-white/5 px-4 py-3 font-display text-xs uppercase tracking-[0.16em] text-white/80 transition hover:border-accent/40 hover:text-accent"
              >
                {label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="flex-1">
          <header className="mb-6 rounded-3xl border border-white/10 bg-surface/80 p-5 shadow-panel">
            <p className="font-display text-xs uppercase tracking-[0.24em] text-accent">{eyebrow}</p>
            <h2 className="mt-3 font-display text-3xl leading-tight">{title}</h2>
          </header>
          <div className="space-y-6">{children}</div>
        </main>
      </div>
    </div>
  );
}
