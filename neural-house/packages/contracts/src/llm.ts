import { z } from "zod";
import { articlePayloadSchema } from "./article.js";
import { contestantPayloadSchema } from "./contestant.js";
import { personaPayloadSchema } from "./persona.js";
import { seasonPayloadSchema } from "./season.js";
import { strictObject } from "./common.js";
import { vipPayloadSchema } from "./vip.js";

export const llmBigBrotherHouseSchema = strictObject({
  season: seasonPayloadSchema,
  contestants: z.array(contestantPayloadSchema),
  personas: z.array(personaPayloadSchema),
  articles: z.array(articlePayloadSchema),
  vips: z.array(vipPayloadSchema)
});

export const llmSeasonBundleSchema = strictObject({
  season: seasonPayloadSchema,
  contestants: z.array(contestantPayloadSchema).default([]),
  personas: z.array(personaPayloadSchema).default([]),
  articles: z.array(articlePayloadSchema).default([]),
  vips: z.array(vipPayloadSchema).default([])
});

export const llmEntityMapSchema = strictObject({
  season: seasonPayloadSchema.optional(),
  contestants: z.array(contestantPayloadSchema).optional(),
  personas: z.array(personaPayloadSchema).optional(),
  articles: z.array(articlePayloadSchema).optional(),
  vips: z.array(vipPayloadSchema).optional()
});

export type LlmBigBrotherHouse = z.infer<typeof llmBigBrotherHouseSchema>;
export type LlmSeasonBundle = z.infer<typeof llmSeasonBundleSchema>;
export type LlmEntityMap = z.infer<typeof llmEntityMapSchema>;
