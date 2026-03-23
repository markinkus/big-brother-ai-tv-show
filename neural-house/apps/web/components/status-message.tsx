export function StatusMessage({ error, empty }: { error?: string | Error | null; empty?: string }) {
  if (error) {
    return (
      <p className="rounded-2xl border border-danger/40 bg-danger/10 px-4 py-3 text-sm text-red-100">
        {typeof error === "string" ? error : error.message}
      </p>
    );
  }
  if (empty) {
    return <p className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-white/60">{empty}</p>;
  }
  return null;
}
