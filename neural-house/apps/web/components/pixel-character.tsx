"use client";

import { useMemo } from "react";

import { buildPixelCells, buildSpritePalette, type PixelFacing, type PixelPhase, type PixelVariant } from "@/lib/pixel-art";

export function PixelCharacter({
  seed,
  paletteKey,
  accentKey,
  variant,
  facing,
  hairStyle = "crown",
  silhouette = "host-ready",
  phase = "stand",
  scale = 4,
  className,
  shadow = true,
}: {
  seed: number;
  paletteKey: string;
  accentKey: string;
  variant: PixelVariant;
  facing?: PixelFacing;
  hairStyle?: string;
  silhouette?: string;
  phase?: PixelPhase;
  scale?: number;
  className?: string;
  shadow?: boolean;
}) {
  const sprite = useMemo(
    () =>
      buildPixelCells({
        palette: buildSpritePalette({ paletteKey, accentKey, seed }),
        variant,
        facing,
        hairStyle,
        silhouette,
        phase,
      }),
    [accentKey, facing, hairStyle, paletteKey, phase, seed, silhouette, variant],
  );

  return (
    <div
      className={`relative ${className ?? ""}`.trim()}
      style={{
        width: sprite.width * scale,
        height: sprite.height * scale + (shadow ? scale * 2 : 0),
        imageRendering: "pixelated",
      }}
    >
      {shadow ? (
        <div
          className="absolute left-1/2 rounded-full bg-black/35"
          style={{
            bottom: scale * 0.4,
            width: sprite.width * scale * 0.72,
            height: scale * 1.6,
            transform: "translateX(-50%)",
            filter: "blur(1px)",
          }}
        />
      ) : null}
      <div
        className="relative"
        style={{
          width: sprite.width * scale,
          height: sprite.height * scale,
        }}
      >
        {sprite.cells.map((cell) => (
          <span
            key={`${cell.x}-${cell.y}-${cell.color}`}
            className="absolute"
            style={{
              left: cell.x * scale,
              top: cell.y * scale,
              width: scale,
              height: scale,
              backgroundColor: cell.color,
            }}
          />
        ))}
      </div>
    </div>
  );
}
