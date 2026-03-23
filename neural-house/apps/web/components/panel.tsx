export function Panel({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: any;
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-surface/80 p-5 shadow-panel">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h3 className="font-display text-lg uppercase tracking-[0.16em] text-accent">{title}</h3>
          {subtitle ? <p className="mt-2 text-sm text-white/65">{subtitle}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}
