export function StatStrip({
  items,
}: {
  items: Array<{ label: string; value: string | number; tone?: "neutral" | "danger" | "success" }>;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-4">
      {items.map((item) => (
        <div
          key={item.label}
          className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3"
        >
          <p className="font-display text-[10px] uppercase tracking-[0.24em] text-white/55">{item.label}</p>
          <p
            className={
              item.tone === "danger"
                ? "mt-2 font-display text-xl text-danger"
                : item.tone === "success"
                  ? "mt-2 font-display text-xl text-success"
                  : "mt-2 font-display text-xl text-ink"
            }
          >
            {item.value}
          </p>
        </div>
      ))}
    </div>
  );
}

