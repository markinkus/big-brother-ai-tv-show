export const pixelBodyPalettes = {
  studio_blue: { body: "#5f8fe3", trim: "#dcecff", shadow: "#254b88" },
  scarlet_nova: { body: "#d86e6a", trim: "#ffd8cd", shadow: "#7a2831" },
  mint_signal: { body: "#6ebfa7", trim: "#d8fff2", shadow: "#1e6c67" },
  noir_gold: { body: "#75624c", trim: "#f7e6ad", shadow: "#242124" },
  orchid_flash: { body: "#b485e3", trim: "#f2deff", shadow: "#65499b" },
} as const;

export const pixelAccentPalettes = {
  gold: "#ffbf4d",
  cyan: "#62d5ff",
  coral: "#ff7b6a",
  violet: "#a98bff",
  lime: "#a8e95e",
} as const;

export type PixelPaletteKey = keyof typeof pixelBodyPalettes;
export type PixelAccentKey = keyof typeof pixelAccentPalettes;
export type PixelFacing = "down" | "up" | "left" | "right";
export type PixelVariant = "topdown" | "portrait";
export type PixelPhase = "stand" | "step";

export type PixelPalette = {
  outline: string;
  hair: string;
  skin: string;
  body: string;
  trim: string;
  accent: string;
  eye: string;
  dark: string;
};

export type PixelCell = {
  x: number;
  y: number;
  color: string;
};

export type RoomTheme = {
  floor: string;
  floorAlt: string;
  wall: string;
  trim: string;
  prop: string;
  accent: string;
  shadow: string;
};

export const hairStyleOptions = ["crown", "crest", "bob", "spikes", "veil"] as const;
export const silhouetteOptions = ["host-ready", "sharp", "soft", "masked", "android"] as const;

const skinTones = ["#f2d2b7", "#e5be9a", "#c78d69", "#9b5f46"] as const;
const hairTones = ["#3d2923", "#805837", "#d6b35f", "#5c2a6d", "#1d313c"] as const;

export const roomThemeMap: Record<string, RoomTheme> = {
  living_room: {
    floor: "#557377",
    floorAlt: "#4a6569",
    wall: "#263c40",
    trim: "#d8c89b",
    prop: "#8a634d",
    accent: "#ffbf4d",
    shadow: "#162426",
  },
  kitchen: {
    floor: "#74604a",
    floorAlt: "#655340",
    wall: "#342921",
    trim: "#f1ddc0",
    prop: "#b58f6b",
    accent: "#92dbe5",
    shadow: "#1e1713",
  },
  garden: {
    floor: "#4e7d55",
    floorAlt: "#426c49",
    wall: "#27432d",
    trim: "#c7d7a3",
    prop: "#7fa15a",
    accent: "#f7f29d",
    shadow: "#17311d",
  },
  bedroom: {
    floor: "#65597d",
    floorAlt: "#584c6d",
    wall: "#2e2840",
    trim: "#e9d9ff",
    prop: "#8f6a93",
    accent: "#f6a9cf",
    shadow: "#1d1827",
  },
  confessional: {
    floor: "#6f3d47",
    floorAlt: "#5f313a",
    wall: "#32171f",
    trim: "#f1d8d1",
    prop: "#a45b5f",
    accent: "#ffdf7e",
    shadow: "#1f0c11",
  },
};

const topdownDown = [
  "....XXXX....",
  "...XHHHHX...",
  "..XHSSSSHX..",
  "..XHSSSSHX..",
  "...XXSSXX...",
  "..XBBBBBBX..",
  ".XBBBAAABBX.",
  ".XBBBTTBBBX.",
  "..XBPPPPBX..",
  "..XP....PX..",
  ".XP......PX.",
  "..X......X..",
];

const topdownUp = [
  "....XXXX....",
  "...XHHHHX...",
  "..XHHHHHHX..",
  "..XHSSSSHX..",
  "...XXSSXX...",
  "..XBBBBBBX..",
  ".XBBBAAABBX.",
  ".XBBBTTBBBX.",
  "..XBPPPPBX..",
  "..XP....PX..",
  ".XP..XX..PX.",
  "..X..XX..X..",
];

const topdownLeftBase = [
  "....XXXX....",
  "...XHHHX....",
  "..XHSSSHX...",
  "..XHSSSSX...",
  "...XXSSX....",
  "..XBBBBBX...",
  ".XBBBAABBX..",
  ".XBBBTTBBX..",
  "..XBPPPBX...",
  "..XP...PX...",
  ".XP.....PX..",
  "..X.....X...",
];

const portraitFront = [
  "....XXXX....",
  "...XHHHHX...",
  "..XHSSSSHX..",
  "..XHSEESHX..",
  "..XSSSSSSX..",
  "...XXSSXX...",
  "...XBBBBX...",
  "..XBBBBBBX..",
  ".XBBTBBTBBX.",
  ".XBBBBBBBBX.",
  ".XBBBAAABBX.",
  "..XBBPPBBX..",
  "..XPP..PPX..",
  ".XP......PX.",
  "..X......X..",
  "...XXXXXX...",
];

function hashSeed(seed: number, salt: number) {
  const value = Math.imul(seed ^ (salt * 2654435761), 1597334677);
  return Math.abs(value);
}

function pick<T>(items: readonly T[], seed: number, salt: number) {
  return items[hashSeed(seed, salt) % items.length];
}

function mirrorPattern(pattern: readonly string[]) {
  return pattern.map((row) => row.split("").reverse().join(""));
}

function darken(hex: string, factor: number) {
  const clean = hex.replace("#", "");
  const value = Number.parseInt(clean, 16);
  const r = Math.max(0, Math.min(255, Math.round(((value >> 16) & 255) * factor)));
  const g = Math.max(0, Math.min(255, Math.round(((value >> 8) & 255) * factor)));
  const b = Math.max(0, Math.min(255, Math.round((value & 255) * factor)));
  return `#${[r, g, b].map((channel) => channel.toString(16).padStart(2, "0")).join("")}`;
}

export function buildSpritePalette({
  paletteKey,
  accentKey,
  seed,
}: {
  paletteKey: string;
  accentKey: string;
  seed: number;
}) {
  const palette = pixelBodyPalettes[(paletteKey in pixelBodyPalettes ? paletteKey : "studio_blue") as PixelPaletteKey];
  const accent = pixelAccentPalettes[(accentKey in pixelAccentPalettes ? accentKey : "gold") as PixelAccentKey];
  const skin = pick(skinTones, seed, 11);
  const hair = pick(hairTones, seed, 19);
  return {
    outline: "#1c1a18",
    hair,
    skin,
    body: palette.body,
    trim: palette.trim,
    accent,
    eye: "#f7f6ef",
    dark: darken(palette.shadow, 0.84),
  } satisfies PixelPalette;
}

export function getPixelPattern(variant: PixelVariant, facing: PixelFacing = "down") {
  if (variant === "portrait") {
    return portraitFront;
  }
  if (facing === "up") {
    return topdownUp;
  }
  if (facing === "left") {
    return topdownLeftBase;
  }
  if (facing === "right") {
    return mirrorPattern(topdownLeftBase);
  }
  return topdownDown;
}

function setCell(cells: PixelCell[], x: number, y: number, color: string) {
  const existing = cells.find((cell) => cell.x === x && cell.y === y);
  if (existing) {
    existing.color = color;
    return;
  }
  cells.push({ x, y, color });
}

function removeCell(cells: PixelCell[], x: number, y: number) {
  const index = cells.findIndex((cell) => cell.x === x && cell.y === y);
  if (index >= 0) {
    cells.splice(index, 1);
  }
}

function applyHairStyle(cells: PixelCell[], palette: PixelPalette, variant: PixelVariant, hairStyle: string) {
  if (variant === "portrait") {
    if (hairStyle === "crest") {
      setCell(cells, 5, 0, palette.hair);
      setCell(cells, 6, 0, palette.hair);
      setCell(cells, 5, 1, palette.hair);
    } else if (hairStyle === "bob") {
      setCell(cells, 2, 2, palette.hair);
      setCell(cells, 9, 2, palette.hair);
      setCell(cells, 2, 3, palette.hair);
      setCell(cells, 9, 3, palette.hair);
    } else if (hairStyle === "spikes") {
      setCell(cells, 3, 0, palette.hair);
      setCell(cells, 5, 0, palette.hair);
      setCell(cells, 7, 0, palette.hair);
      setCell(cells, 8, 1, palette.hair);
    } else if (hairStyle === "veil") {
      setCell(cells, 1, 4, palette.hair);
      setCell(cells, 10, 4, palette.hair);
      setCell(cells, 2, 5, palette.hair);
      setCell(cells, 9, 5, palette.hair);
    }
    return;
  }

  if (hairStyle === "crest") {
    setCell(cells, 5, 0, palette.hair);
    setCell(cells, 6, 0, palette.hair);
  } else if (hairStyle === "bob") {
    setCell(cells, 2, 2, palette.hair);
    setCell(cells, 9, 2, palette.hair);
  } else if (hairStyle === "spikes") {
    setCell(cells, 3, 0, palette.hair);
    setCell(cells, 8, 0, palette.hair);
  } else if (hairStyle === "veil") {
    setCell(cells, 2, 4, palette.hair);
    setCell(cells, 9, 4, palette.hair);
  }
}

function applySilhouette(cells: PixelCell[], palette: PixelPalette, variant: PixelVariant, silhouette: string) {
  if (silhouette === "sharp") {
    setCell(cells, 1, variant === "portrait" ? 10 : 8, palette.accent);
    setCell(cells, 10, variant === "portrait" ? 10 : 8, palette.accent);
  } else if (silhouette === "soft") {
    setCell(cells, 4, variant === "portrait" ? 11 : 9, palette.trim);
    setCell(cells, 7, variant === "portrait" ? 11 : 9, palette.trim);
  } else if (silhouette === "masked") {
    setCell(cells, 4, variant === "portrait" ? 3 : 2, palette.dark);
    setCell(cells, 7, variant === "portrait" ? 3 : 2, palette.dark);
    setCell(cells, 5, variant === "portrait" ? 4 : 3, palette.eye);
    setCell(cells, 6, variant === "portrait" ? 4 : 3, palette.eye);
  } else if (silhouette === "android") {
    setCell(cells, 5, variant === "portrait" ? 8 : 6, palette.accent);
    setCell(cells, 6, variant === "portrait" ? 8 : 6, palette.accent);
    setCell(cells, 5, variant === "portrait" ? 9 : 7, palette.trim);
  }
}

function applyPhase(cells: PixelCell[], palette: PixelPalette, variant: PixelVariant, phase: PixelPhase, facing: PixelFacing) {
  if (variant !== "topdown" || phase !== "step") {
    return;
  }
  if (facing === "down" || facing === "up") {
    removeCell(cells, 4, 10);
    removeCell(cells, 7, 10);
    setCell(cells, 3, 10, palette.dark);
    setCell(cells, 8, 10, palette.dark);
    setCell(cells, 2, 11, palette.outline);
    setCell(cells, 9, 11, palette.outline);
  } else if (facing === "left") {
    removeCell(cells, 2, 10);
    setCell(cells, 1, 10, palette.dark);
    setCell(cells, 1, 11, palette.outline);
  } else if (facing === "right") {
    removeCell(cells, 9, 10);
    setCell(cells, 10, 10, palette.dark);
    setCell(cells, 10, 11, palette.outline);
  }
}

export function buildPixelCells({
  palette,
  variant,
  facing,
  hairStyle = "crown",
  silhouette = "host-ready",
  phase = "stand",
}: {
  palette: PixelPalette;
  variant: PixelVariant;
  facing?: PixelFacing;
  hairStyle?: string;
  silhouette?: string;
  phase?: PixelPhase;
}) {
  const pattern = getPixelPattern(variant, facing);
  const colorMap: Record<string, string> = {
    X: palette.outline,
    H: palette.hair,
    S: palette.skin,
    E: palette.eye,
    B: palette.body,
    T: palette.trim,
    A: palette.accent,
    P: palette.dark,
  };
  const cells: PixelCell[] = [];
  pattern.forEach((row, y) => {
    row.split("").forEach((token, x) => {
      const color = colorMap[token];
      if (color) {
        cells.push({ x, y, color });
      }
    });
  });
  applyHairStyle(cells, palette, variant, hairStyle);
  applySilhouette(cells, palette, variant, silhouette);
  applyPhase(cells, palette, variant, phase, facing ?? "down");
  return {
    width: pattern[0]?.length ?? 0,
    height: pattern.length,
    cells,
  };
}
