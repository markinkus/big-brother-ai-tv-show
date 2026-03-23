import { z } from "zod";
import {
  idSchema,
  strictObject,
  titleSchema,
  urlSchema
} from "./common.js";

export const providerNameSchema = z.enum([
  "local_stub",
  "ollama",
  "openai_compatible",
  "anthropic_compatible"
]);

export const jsonContractEnvelopeSchema = strictObject({
  provider: providerNameSchema,
  model: titleSchema,
  requestId: idSchema.optional(),
  contract: z.string().trim().min(1),
  source: urlSchema.optional()
});

export const llmResponseEnvelopeSchema = strictObject({
  provider: providerNameSchema,
  model: titleSchema,
  contract: z.string().trim().min(1),
  payload: z.unknown(),
  rawText: z.string().trim().min(1).optional()
});

export type ProviderName = z.infer<typeof providerNameSchema>;
export type JsonContractEnvelope = z.infer<typeof jsonContractEnvelopeSchema>;
export type LlmResponseEnvelope = z.infer<typeof llmResponseEnvelopeSchema>;
