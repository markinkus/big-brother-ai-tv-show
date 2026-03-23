import { z } from "zod";

import { safeNumberSchema, strictObject, summarySchema, titleSchema, urlSchema } from "./common.js";
import { providerNameSchema } from "./provider.js";

export const auditionStatusSchema = z.enum(["draft", "queued", "running", "completed", "failed"]);
export const auditionZoneSchema = z.enum([
  "entrance",
  "host_mark",
  "camera_lane",
  "spotlight",
  "confessional_cam",
  "exit_mark"
]);

export const auditionAgentSkinSchema = strictObject({
  palette: z.string().trim().min(1).max(40),
  accent: z.string().trim().min(1).max(40),
  silhouette: z.enum(["host-ready", "sharp", "soft", "masked", "android"]),
});

export const auditionProviderConfigSchema = strictObject({
  provider: providerNameSchema,
  apiBaseUrl: urlSchema.optional().or(z.literal("")).transform((value) => value || undefined),
  modelName: titleSchema,
  enabled: z.boolean().default(false),
});

export const auditionAgentConfigSchema = strictObject({
  characterName: titleSchema,
  archetype: z.string().trim().min(1).max(80),
  speechStyle: summarySchema,
  publicHook: summarySchema,
  traits: z.array(z.string().trim().min(1).max(60)).min(1).max(8),
  strengths: z.array(z.string().trim().min(1).max(80)).default([]),
  weaknesses: z.array(z.string().trim().min(1).max(80)).default([]),
  skin: auditionAgentSkinSchema,
});

export const auditionCreateRequestSchema = strictObject({
  providerConfig: auditionProviderConfigSchema,
  agentConfig: auditionAgentConfigSchema,
  simulatedMinutes: safeNumberSchema.int().min(2).max(12).default(6),
  playbackMsPerBeat: safeNumberSchema.int().min(500).max(15000).default(5000),
});

export const auditionEventSchema = strictObject({
  id: safeNumberSchema.int().positive(),
  sessionId: safeNumberSchema.int().positive(),
  tickNumber: safeNumberSchema.int().nonnegative(),
  simulatedSecond: safeNumberSchema.int().nonnegative(),
  zone: auditionZoneSchema,
  actionType: z.string().trim().min(1).max(80),
  summary: summarySchema,
  dialogue: summarySchema.optional(),
  stateSnapshot: strictObject({
    confidence: safeNumberSchema.min(0).max(100),
    stress: safeNumberSchema.min(0).max(100),
    cameraHeat: safeNumberSchema.min(0).max(100),
  }),
});

export const auditionSessionSchema = strictObject({
  id: safeNumberSchema.int().positive(),
  status: auditionStatusSchema,
  environmentLabel: z.string().trim().min(1).max(120),
  providerConfig: auditionProviderConfigSchema,
  agentConfig: auditionAgentConfigSchema,
  simulatedMinutes: safeNumberSchema.int().positive(),
  playbackMsPerBeat: safeNumberSchema.int().positive(),
  totalBeats: safeNumberSchema.int().positive(),
  currentBeat: safeNumberSchema.int().nonnegative(),
  summary: summarySchema,
  createdAt: z.string().datetime({ offset: true }),
  startedAt: z.string().datetime({ offset: true }).optional(),
  endedAt: z.string().datetime({ offset: true }).optional(),
});

export type AuditionStatus = z.infer<typeof auditionStatusSchema>;
export type AuditionZone = z.infer<typeof auditionZoneSchema>;
export type AuditionProviderConfig = z.infer<typeof auditionProviderConfigSchema>;
export type AuditionAgentConfig = z.infer<typeof auditionAgentConfigSchema>;
export type AuditionCreateRequest = z.infer<typeof auditionCreateRequestSchema>;
export type AuditionEvent = z.infer<typeof auditionEventSchema>;
export type AuditionSession = z.infer<typeof auditionSessionSchema>;
