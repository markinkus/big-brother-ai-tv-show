import { z } from "zod";
import {
  descriptionSchema,
  idSchema,
  nonEmptyListSchema,
  strictObject,
  summarySchema
} from "./common.js";

export const personaModeSchema = z.enum([
  "casting",
  "confessional",
  "live-feed",
  "recap",
  "social",
  "production"
]);

export const personaPayloadSchema = strictObject({
  id: idSchema,
  seasonId: idSchema,
  contestantId: idSchema.optional(),
  mode: personaModeSchema,
  label: z.string().trim().min(1).max(120),
  voice: summarySchema,
  prompt: descriptionSchema,
  systemInstructions: descriptionSchema,
  traits: nonEmptyListSchema(z.string().trim().min(1).max(120)),
  guardrails: z.array(z.string().trim().min(1).max(200)).default([]),
  goals: z.array(z.string().trim().min(1).max(200)).default([]),
  relationships: z
    .array(
      strictObject({
        subjectId: idSchema,
        relation: z.string().trim().min(1).max(120),
        intensity: z.enum(["low", "medium", "high"])
      })
    )
    .default([]),
  notes: z.array(z.string().trim().min(1).max(280)).default([])
});

export type PersonaMode = z.infer<typeof personaModeSchema>;
export type PersonaPayload = z.infer<typeof personaPayloadSchema>;
