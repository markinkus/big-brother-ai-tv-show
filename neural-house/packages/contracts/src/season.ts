import { z } from "zod";
import {
  descriptionSchema,
  idSchema,
  isoDateSchema,
  localeSchema,
  nonEmptyListSchema,
  safeNumberSchema,
  slugSchema,
  strictObject,
  summarySchema,
  titleSchema
} from "./common.js";

export const seasonStatusSchema = z.enum([
  "planning",
  "casting",
  "airing",
  "completed",
  "archived"
]);

export const seasonToneSchema = z.enum([
  "camp",
  "competitive",
  "strategic",
  "surreal",
  "dramatic"
]);

export const seasonPayloadSchema = strictObject({
  id: idSchema,
  slug: slugSchema,
  number: safeNumberSchema.int().positive(),
  title: titleSchema,
  subtitle: z.string().trim().min(1).max(180).optional(),
  summary: summarySchema,
  description: descriptionSchema.optional(),
  year: safeNumberSchema.int().min(2000).max(2100),
  status: seasonStatusSchema,
  tone: seasonToneSchema,
  locale: localeSchema.default("en-US"),
  premiereDate: isoDateSchema.optional(),
  finaleDate: isoDateSchema.optional(),
  hostIds: z.array(idSchema).default([]),
  contestantIds: z.array(idSchema),
  vipIds: z.array(idSchema).default([]),
  themes: nonEmptyListSchema(z.string().trim().min(1).max(120)),
  rules: z.array(z.string().trim().min(1).max(240)),
  storyBeats: z.array(z.string().trim().min(1).max(400)).default([])
});

export type SeasonStatus = z.infer<typeof seasonStatusSchema>;
export type SeasonTone = z.infer<typeof seasonToneSchema>;
export type SeasonPayload = z.infer<typeof seasonPayloadSchema>;
