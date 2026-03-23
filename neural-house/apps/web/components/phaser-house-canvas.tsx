"use client";

import { useEffect, useRef } from "react";

import {
  buildPixelCells,
  buildSpritePalette,
  pixelBodyPalettes,
  pixelAccentPalettes,
  roomThemeMap,
  type PixelFacing,
} from "@/lib/pixel-art";

type Room = {
  code: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
};

type Contestant = {
  id: number;
  display_name: string;
  avatar_seed: number;
  skin_palette: string;
  skin_accent: string;
  skin_silhouette: string;
  hair_style: string;
};

const tileSize = 16;
const facingCycle: PixelFacing[] = ["down", "left", "right", "up"];

function createSpriteTexture(scene: any, contestant: Contestant, facing: PixelFacing, phase: "stand" | "step") {
  const bodyPaletteKeys = Object.keys(pixelBodyPalettes);
  const accentPaletteKeys = Object.keys(pixelAccentPalettes);
  const paletteKey =
    contestant.skin_palette in pixelBodyPalettes
      ? contestant.skin_palette
      : bodyPaletteKeys[Math.abs(contestant.avatar_seed || contestant.id) % bodyPaletteKeys.length] ?? "studio_blue";
  const accentKey =
    contestant.skin_accent in pixelAccentPalettes
      ? contestant.skin_accent
      : accentPaletteKeys[Math.abs((contestant.avatar_seed || contestant.id * 11) + contestant.id) % accentPaletteKeys.length] ?? "gold";
  const key = `contestant-${contestant.id}-${facing}-${phase}-${paletteKey}-${accentKey}-${contestant.hair_style}-${contestant.skin_silhouette}`;
  if (scene.textures.exists(key)) {
    return key;
  }

  const texture = scene.textures.createCanvas(key, 12, 12);
  const context = texture.getContext();
  context.imageSmoothingEnabled = false;
  context.clearRect(0, 0, 12, 12);

  const sprite = buildPixelCells({
    palette: buildSpritePalette({
      paletteKey,
      accentKey,
      seed: contestant.avatar_seed || contestant.id * 97,
    }),
    variant: "topdown",
    facing,
    hairStyle: contestant.hair_style,
    silhouette: contestant.skin_silhouette,
    phase,
  });

  sprite.cells.forEach((cell) => {
    context.fillStyle = cell.color;
    context.fillRect(cell.x, cell.y, 1, 1);
  });
  texture.refresh();
  return key;
}

function drawRoom(graphics: any, room: Room, focused: boolean) {
  const theme = roomThemeMap[room.code] ?? roomThemeMap.living_room;
  const roomX = room.x * tileSize;
  const roomY = room.y * tileSize;
  const roomWidth = room.width * tileSize;
  const roomHeight = room.height * tileSize;

  for (let tileY = 0; tileY < room.height; tileY += 1) {
    for (let tileX = 0; tileX < room.width; tileX += 1) {
      const x = roomX + tileX * tileSize;
      const y = roomY + tileY * tileSize;
      const floor = (tileX + tileY) % 2 === 0 ? theme.floor : theme.floorAlt;
      graphics.fillStyle(Number.parseInt(floor.replace("#", ""), 16), 1);
      graphics.fillRect(x, y, tileSize, tileSize);
      graphics.fillStyle(Number.parseInt(theme.shadow.replace("#", ""), 16), 0.15);
      graphics.fillRect(x, y + tileSize - 2, tileSize, 2);
    }
  }

  graphics.fillStyle(Number.parseInt(theme.wall.replace("#", ""), 16), 1);
  graphics.fillRect(roomX, roomY, roomWidth, 4);
  graphics.fillRect(roomX, roomY + roomHeight - 4, roomWidth, 4);
  graphics.fillRect(roomX, roomY, 4, roomHeight);
  graphics.fillRect(roomX + roomWidth - 4, roomY, 4, roomHeight);

  graphics.fillStyle(Number.parseInt(theme.trim.replace("#", ""), 16), focused ? 1 : 0.5);
  graphics.fillRect(roomX + 4, roomY + 4, roomWidth - 8, 2);
  graphics.fillRect(roomX + 4, roomY + roomHeight - 6, roomWidth - 8, 2);
  graphics.fillRect(roomX + 4, roomY + roomHeight - 4, 18, 4);
  graphics.fillRect(roomX + roomWidth - 22, roomY + roomHeight - 4, 18, 4);

  graphics.lineStyle(focused ? 3 : 2, Number.parseInt(theme.trim.replace("#", ""), 16), focused ? 0.8 : 0.18);
  graphics.strokeRect(roomX, roomY, roomWidth, roomHeight);

  switch (room.code) {
    case "living_room":
      graphics.fillStyle(Number.parseInt(theme.prop.replace("#", ""), 16), 1);
      graphics.fillRect(roomX + 18, roomY + 18, 42, 14);
      graphics.fillRect(roomX + 28, roomY + 34, 48, 12);
      graphics.fillStyle(Number.parseInt(theme.accent.replace("#", ""), 16), 0.85);
      graphics.fillRect(roomX + roomWidth - 38, roomY + 18, 20, 16);
      graphics.fillRect(roomX + 18, roomY + roomHeight - 22, 18, 8);
      graphics.fillRect(roomX + roomWidth - 30, roomY + roomHeight - 22, 14, 8);
      break;
    case "kitchen":
      graphics.fillStyle(Number.parseInt(theme.prop.replace("#", ""), 16), 1);
      graphics.fillRect(roomX + 14, roomY + 18, roomWidth - 28, 12);
      graphics.fillRect(roomX + roomWidth - 34, roomY + 34, 18, 18);
      graphics.fillStyle(Number.parseInt(theme.accent.replace("#", ""), 16), 0.85);
      graphics.fillRect(roomX + 20, roomY + 20, 12, 8);
      graphics.fillRect(roomX + 18, roomY + roomHeight - 22, 14, 10);
      graphics.fillRect(roomX + roomWidth - 54, roomY + roomHeight - 20, 20, 8);
      break;
    case "garden":
      graphics.fillStyle(Number.parseInt(theme.prop.replace("#", ""), 16), 1);
      graphics.fillRect(roomX + 16, roomY + 14, 16, 16);
      graphics.fillRect(roomX + roomWidth - 34, roomY + 16, 14, 18);
      graphics.fillStyle(Number.parseInt(theme.accent.replace("#", ""), 16), 0.8);
      graphics.fillRect(roomX + 20, roomY + 18, 8, 8);
      graphics.fillRect(roomX + roomWidth - 30, roomY + 22, 6, 6);
      graphics.fillRect(roomX + roomWidth / 2 - 10, roomY + roomHeight - 24, 20, 10);
      break;
    case "bedroom":
      graphics.fillStyle(Number.parseInt(theme.prop.replace("#", ""), 16), 1);
      graphics.fillRect(roomX + 16, roomY + 18, 28, 18);
      graphics.fillRect(roomX + roomWidth - 44, roomY + 18, 28, 18);
      graphics.fillStyle(Number.parseInt(theme.accent.replace("#", ""), 16), 0.9);
      graphics.fillRect(roomX + 20, roomY + 20, 20, 8);
      graphics.fillRect(roomX + roomWidth - 40, roomY + 20, 20, 8);
      graphics.fillRect(roomX + roomWidth / 2 - 8, roomY + roomHeight - 20, 16, 8);
      break;
    case "confessional":
      graphics.fillStyle(Number.parseInt(theme.prop.replace("#", ""), 16), 1);
      graphics.fillRect(roomX + 18, roomY + 18, roomWidth - 36, roomHeight - 34);
      graphics.fillStyle(Number.parseInt(theme.accent.replace("#", ""), 16), 0.9);
      graphics.fillRect(roomX + roomWidth / 2 - 6, roomY + 20, 12, 12);
      graphics.fillRect(roomX + roomWidth / 2 - 12, roomY + roomHeight - 26, 24, 8);
      break;
    default:
      break;
  }
}

function roomSpots(room: Room, count: number) {
  if (count <= 0) {
    return [];
  }
  const roomX = room.x * tileSize;
  const roomY = room.y * tileSize;
  const roomWidth = room.width * tileSize;
  const roomHeight = room.height * tileSize;
  const columns = Math.min(2, count);
  const rows = Math.ceil(count / columns);
  const spots: Array<{ x: number; y: number }> = [];

  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      if (spots.length >= count) {
        return spots;
      }
      spots.push({
        x: roomX + ((column + 1) * roomWidth) / (columns + 1),
        y: roomY + roomHeight - 18 - row * 26,
      });
    }
  }
  return spots;
}

export function PhaserHouseCanvas({
  rooms,
  contestants,
  activeRoomCode,
  activeActorIds,
}: {
  rooms: Room[];
  contestants: Contestant[];
  activeRoomCode?: string | null;
  activeActorIds?: number[];
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let game: any;

    async function boot() {
      if (!containerRef.current) {
        return;
      }
      const Phaser = (await import("phaser")).default;

      class HouseScene extends Phaser.Scene {
        create() {
          this.cameras.main.setBackgroundColor("#091011");
          const graphics = this.add.graphics();
          const activeIds = new Set(activeActorIds ?? []);
          const activeActors = contestants.filter((contestant) => activeIds.has(contestant.id));
          const passiveActors = contestants.filter((contestant) => !activeIds.has(contestant.id));

          rooms.forEach((room, index) => {
            const focused = room.code === activeRoomCode;
            drawRoom(graphics, room, focused);

            const roomX = room.x * tileSize;
            const roomY = room.y * tileSize;
            const panelWidth = Math.max(44, room.name.length * 7 + 10);
            this.add
              .rectangle(roomX + panelWidth / 2 + 8, roomY + 12, panelWidth, 16, 0x111a1c, 0.9)
              .setStrokeStyle(2, focused ? 0xf4e6b4 : 0x8aa8ad, 0.6)
              .setOrigin(0.5, 0.5);
            this.add.text(roomX + 10, roomY + 7, room.name.toUpperCase(), {
              fontFamily: "monospace",
              fontSize: "9px",
              color: focused ? "#f4e6b4" : "#d7e8eb",
            });

            const offset = passiveActors.length ? index % passiveActors.length : 0;
            const people = focused ? activeActors.slice(0, 4) : passiveActors.slice(offset, offset + 2);
            const spots = roomSpots(room, people.length);

            people.forEach((contestant, personIndex) => {
              const spot = spots[personIndex];
              if (!spot) {
                return;
              }
              const facing = focused ? facingCycle[personIndex % facingCycle.length] : facingCycle[(index + personIndex) % facingCycle.length];
              const standTexture = createSpriteTexture(this, contestant, facing, "stand");
              const stepTexture = createSpriteTexture(this, contestant, facing, "step");
              this.add.ellipse(spot.x, spot.y + 2, 22, 10, 0x000000, 0.34);
              const sprite = this.add.image(spot.x, spot.y, standTexture).setOrigin(0.5, 1).setScale(2);
              if (focused || activeIds.has(contestant.id)) {
                this.tweens.add({
                  targets: sprite,
                  y: spot.y - 2,
                  duration: 900 + personIndex * 80,
                  yoyo: true,
                  repeat: -1,
                  ease: "Sine.easeInOut",
                });
                let stepping = false;
                this.time.addEvent({
                  delay: 220 + personIndex * 40,
                  loop: true,
                  callback: () => {
                    stepping = !stepping;
                    sprite.setTexture(stepping ? stepTexture : standTexture);
                  },
                });
              }

              const label = contestant.display_name.slice(0, 3).toUpperCase();
              this.add
                .rectangle(spot.x, spot.y + 12, 30, 12, focused ? 0x121212 : 0x0f1416, 0.95)
                .setStrokeStyle(1, focused ? 0xf4e6b4 : 0x9cb8be, 0.55);
              this.add.text(spot.x - 10, spot.y + 8, label, {
                fontFamily: "monospace",
                fontSize: "8px",
                color: focused ? "#f4e6b4" : "#dcebed",
              });
            });
          });
        }
      }

      game = new Phaser.Game({
        type: Phaser.AUTO,
        parent: containerRef.current,
        width: 540,
        height: 324,
        transparent: true,
        pixelArt: true,
        scene: HouseScene,
      });
    }

    void boot();

    return () => {
      game?.destroy(true);
    };
  }, [rooms, contestants, activeRoomCode, activeActorIds]);

  return <div ref={containerRef} className="pixel-frame overflow-hidden rounded-2xl border border-white/10 bg-black/30 p-3" />;
}
