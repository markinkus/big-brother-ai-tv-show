import { z } from "zod";
import {
  contactHandleSchema,
  descriptionSchema,
  idSchema,
  safeNumberSchema,
  strictObject,
  summarySchema
} from "./common.js";

export const contestantStatusSchema = z.enum([
  "applicant",
  "active",
  "nominee",
  "evicted",
  "walked",
  "winner"
]);

export const contestantArchetypeSchema = z.enum([
  "strategist",
  "socialite",
  "chaos-agent",
  "underdog",
  "wildcard",
  "comp-legend",
  "villain",
  "heart"
]);

export const contestantPayloadSchema = strictObject({
  id: idSchema,
  seasonId: idSchema,
  fullName: z.string().trim().min(1).max(120),
  displayName: z.string().trim().min(1).max(120).optional(),
  age: safeNumberSchema.int().min(18).max(120).optional(),
  hometown: z.string().trim().min(1).max(160).optional(),
  occupation: z.string().trim().min(1).max(160).optional(),
  status: contestantStatusSchema,
  archetype: contestantArchetypeSchema,
  bio: summarySchema,
  backstory: descriptionSchema.optional(),
  strengths: z.array(z.string().trim().min(1).max(120)).default([]),
  weaknesses: z.array(z.string().trim().min(1).max(120)).default([]),
  alliances: z.array(idSchema).default([]),
  rivals: z.array(idSchema).default([]),
  mentions: z.array(contactHandleSchema).default([]),
  notes: z.array(z.string().trim().min(1).max(280)).default([])
});

export type ContestantStatus = z.infer<typeof contestantStatusSchema>;
export type ContestantArchetype = z.infer<typeof contestantArchetypeSchema>;
export type ContestantPayload = z.infer<typeof contestantPayloadSchema>;
