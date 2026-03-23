"use client";

import { useQuery } from "@tanstack/react-query";

import { apiGet } from "@/lib/api";
import { useNeuralHouseStore } from "@/lib/store";
import { Panel } from "@/components/panel";
import { StatusMessage } from "@/components/status-message";

type Contestant = {
  id: number;
  display_name: string;
  archetype: string;
};

type RelationshipRow = {
  id: number;
  season_id: number;
  source_contestant_id: number;
  target_contestant_id: number;
  source_name: string;
  target_name: string;
  trust: number;
  rivalry: number;
  respect: number;
  manipulation: number;
  last_significant_change_at: string | null;
};

type Node = {
  name: string;
  label: string;
  archetype?: string;
  outgoing: number;
  incoming: number;
  netTrust: number;
  netRivalry: number;
};

type PositionedNode = Node & {
  x: number;
  y: number;
};

function clamp(value: number, min: number, max: number) {
  return Math.min(max, Math.max(min, value));
}

function formatValue(value: number) {
  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}`;
}

function relationshipStrength(row: RelationshipRow) {
  return Math.abs(row.trust) * 0.35 + Math.abs(row.rivalry) * 0.3 + Math.abs(row.respect) * 0.2 + Math.abs(row.manipulation) * 0.15;
}

function relationshipTone(row: RelationshipRow) {
  const trust = row.trust - row.rivalry * 0.35 + row.respect * 0.2 - row.manipulation * 0.2;
  return clamp(trust, -1, 1);
}

function buildNetwork(contestants: Contestant[], relationships: RelationshipRow[]) {
  const nodes = new Map<string, Node>();

  const ensureNode = (name: string, label: string, archetype?: string) => {
    const existing = nodes.get(name);
    if (existing) {
      if (!existing.archetype && archetype) {
        existing.archetype = archetype;
      }
      return existing;
    }
    const node: Node = {
      name,
      label,
      archetype,
      outgoing: 0,
      incoming: 0,
      netTrust: 0,
      netRivalry: 0,
    };
    nodes.set(name, node);
    return node;
  };

  contestants.forEach((contestant) => ensureNode(contestant.display_name, contestant.display_name, contestant.archetype));

  relationships.forEach((row) => {
    const source = ensureNode(row.source_name, row.source_name);
    const target = ensureNode(row.target_name, row.target_name);
    source.outgoing += 1;
    target.incoming += 1;
    source.netTrust += row.trust;
    source.netRivalry += row.rivalry;
    target.netTrust += row.trust * 0.6;
    target.netRivalry += row.rivalry * 0.6;
  });

  const nodeList = Array.from(nodes.values()).sort((a, b) => {
    const aScore = Math.abs(a.netTrust) + Math.abs(a.netRivalry) + a.outgoing + a.incoming;
    const bScore = Math.abs(b.netTrust) + Math.abs(b.netRivalry) + b.outgoing + b.incoming;
    return bScore - aScore || a.label.localeCompare(b.label);
  });

  return nodeList;
}

function layoutNodes(nodes: Node[]) {
  if (!nodes.length) {
    return [] as PositionedNode[];
  }

  const radius = nodes.length <= 3 ? 118 : 142;
  const centerX = 220;
  const centerY = 205;

  return nodes.map((node, index) => {
    const angle = nodes.length === 1 ? -Math.PI / 2 : (-Math.PI / 2) + (index / nodes.length) * Math.PI * 2;
    const spread = node.name.length > 8 ? radius + 8 : radius;
    return {
      ...node,
      x: centerX + Math.cos(angle) * spread,
      y: centerY + Math.sin(angle) * spread,
    };
  });
}

function edgeStyle(row: RelationshipRow) {
  const tone = relationshipTone(row);
  const rivalry = clamp(row.rivalry, 0, 1.5);
  const trust = clamp(row.trust, 0, 1.5);

  if (tone >= 0.25) {
    return {
      stroke: "#8fd9b6",
      opacity: 0.35 + trust * 0.35,
      dash: "0",
    };
  }

  if (tone <= -0.2) {
    return {
      stroke: "#ff7f7f",
      opacity: 0.35 + rivalry * 0.35,
      dash: "8 6",
    };
  }

  return {
    stroke: "#f4e6b4",
    opacity: 0.35,
    dash: "4 5",
  };
}

export function RelationshipBoard() {
  const seasonId = useNeuralHouseStore((state) => state.seasonId);
  const contestants = useQuery({
    queryKey: ["contestants", seasonId],
    queryFn: async () => (await apiGet<Contestant[]>(`/api/seasons/${seasonId}/contestants`)).data ?? [],
    refetchInterval: 10_000,
  });
  const relationships = useQuery({
    queryKey: ["relationships", seasonId],
    queryFn: async () => (await apiGet<RelationshipRow[]>(`/api/seasons/${seasonId}/relationships`)).data ?? [],
    refetchInterval: 10_000,
  });

  const network = buildNetwork(contestants.data ?? [], relationships.data ?? []);
  const positionedNodes = layoutNodes(network);
  const strongestTies = [...(relationships.data ?? [])]
    .sort((a, b) => relationshipStrength(b) - relationshipStrength(a))
    .slice(0, 6);

  const hasRows = (relationships.data ?? []).length > 0;
  const hasNodes = positionedNodes.length > 0;

  return (
    <Panel
      title="Relationship Graph"
      subtitle="Deterministic board of trust, rivalry, respect, and manipulation between contestants."
    >
      <StatusMessage
        error={contestants.error ?? relationships.error}
        empty={!relationships.error && !hasRows ? "No relationship rows yet. Generate simulation ticks to populate the graph." : undefined}
      />
      <div className="mt-4 grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-white/10 bg-black/25 p-4">
          <div className="relative h-[440px] overflow-hidden rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_center,_rgba(255,255,255,0.06),_rgba(0,0,0,0.22)_62%,_rgba(0,0,0,0.34)_100%)]">
            <svg className="absolute inset-0 h-full w-full" viewBox="0 0 440 440" aria-hidden="true">
              <defs>
                <marker id="arrow-trust" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L8,3 z" fill="#8fd9b6" />
                </marker>
                <marker id="arrow-rivalry" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto">
                  <path d="M0,0 L0,6 L8,3 z" fill="#ff7f7f" />
                </marker>
              </defs>
              <circle cx="220" cy="205" r="76" fill="rgba(255,255,255,0.03)" stroke="rgba(255,255,255,0.08)" />
              <circle cx="220" cy="205" r="128" fill="none" stroke="rgba(255,255,255,0.05)" strokeDasharray="6 10" />
              {relationships.data?.map((row) => {
                const source = positionedNodes.find((node) => node.name === row.source_name);
                const target = positionedNodes.find((node) => node.name === row.target_name);
                if (!source || !target) {
                  return null;
                }
                const style = edgeStyle(row);
                return (
                  <line
                    key={row.id}
                    x1={source.x}
                    y1={source.y}
                    x2={target.x}
                    y2={target.y}
                    stroke={style.stroke}
                    strokeOpacity={style.opacity}
                    strokeWidth={1.5 + relationshipStrength(row) * 1.6}
                    strokeDasharray={style.dash}
                    markerEnd={style.stroke === "#8fd9b6" ? "url(#arrow-trust)" : style.stroke === "#ff7f7f" ? "url(#arrow-rivalry)" : undefined}
                  />
                );
              })}
            </svg>

            {positionedNodes.map((node) => {
              const pressure = clamp(Math.abs(node.netTrust) + Math.abs(node.netRivalry), 0, 3);
              const glow = node.netTrust >= node.netRivalry ? "rgba(143, 217, 182, 0.18)" : "rgba(255, 127, 127, 0.18)";
              return (
                <div
                  key={node.name}
                  className="absolute -translate-x-1/2 -translate-y-1/2 rounded-2xl border px-3 py-2 text-center shadow-lg backdrop-blur"
                  style={{
                    left: `${node.x}px`,
                    top: `${node.y}px`,
                    minWidth: "112px",
                    borderColor: node.netTrust >= node.netRivalry ? "rgba(143,217,182,0.35)" : "rgba(255,127,127,0.35)",
                    background: `linear-gradient(180deg, ${glow}, rgba(0,0,0,0.72))`,
                    boxShadow: `0 0 ${18 + pressure * 12}px ${glow}`,
                  }}
                >
                  <div className="font-display text-[10px] uppercase tracking-[0.2em] text-accent">{node.label}</div>
                  <div className="mt-1 text-sm font-semibold text-white">{node.name}</div>
                  <div className="mt-1 text-[10px] uppercase tracking-[0.16em] text-white/50">
                    {node.archetype ?? "unknown"} · {node.outgoing + node.incoming} links
                  </div>
                </div>
              );
            })}

            {!hasNodes ? (
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="max-w-sm rounded-3xl border border-white/10 bg-black/50 px-5 py-4 text-center text-sm text-white/65">
                  No contestants available for graph rendering.
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Strongest Ties</p>
            {strongestTies.length ? (
              <ul className="mt-4 space-y-3">
                {strongestTies.map((row) => (
                  <li key={row.id} className="rounded-2xl border border-white/10 bg-white/5 p-3">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="text-sm font-semibold text-white">
                          {row.source_name} to {row.target_name}
                        </div>
                        <div className="mt-1 text-xs uppercase tracking-[0.18em] text-white/45">
                          Last change {row.last_significant_change_at ?? "n/a"}
                        </div>
                      </div>
                      <div className="text-right text-xs uppercase tracking-[0.18em] text-white/55">
                        {relationshipStrength(row).toFixed(2)}
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-4 gap-2 text-[10px] uppercase tracking-[0.18em] text-white/55">
                      <span className="rounded-full border border-white/10 bg-black/20 px-2 py-1 text-center text-success">
                        Trust {formatValue(row.trust)}
                      </span>
                      <span className="rounded-full border border-white/10 bg-black/20 px-2 py-1 text-center text-danger">
                        Rivalry {formatValue(row.rivalry)}
                      </span>
                      <span className="rounded-full border border-white/10 bg-black/20 px-2 py-1 text-center">
                        Respect {formatValue(row.respect)}
                      </span>
                      <span className="rounded-full border border-white/10 bg-black/20 px-2 py-1 text-center">
                        Manip {formatValue(row.manipulation)}
                      </span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <StatusMessage empty="No relationship rows yet. The board will populate once the season emits relationship data." />
            )}
          </div>

          <div className="rounded-3xl border border-white/10 bg-black/20 p-4">
            <p className="font-display text-xs uppercase tracking-[0.2em] text-accent">Legend</p>
            <div className="mt-4 space-y-3 text-sm text-white/70">
              <div className="flex items-center justify-between gap-4">
                <span>Green links</span>
                <span className="text-success">High trust / alliance pressure</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Red links</span>
                <span className="text-danger">High rivalry / friction</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Dotted links</span>
                <span>Mixed or unstable relation</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  );
}
