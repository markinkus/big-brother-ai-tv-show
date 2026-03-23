import { z } from "zod";
import {
  idSchema,
  isoDateTimeSchema,
  slugSchema,
  strictObject,
  summarySchema,
  titleSchema,
  urlSchema
} from "./common.js";

export const articleKindSchema = z.enum([
  "news",
  "recap",
  "analysis",
  "interview",
  "feature",
  "announcement"
]);

export const articlePayloadSchema = strictObject({
  id: idSchema,
  seasonId: idSchema.optional(),
  contestantId: idSchema.optional(),
  slug: slugSchema,
  title: titleSchema,
  dek: summarySchema.optional(),
  kind: articleKindSchema,
  canonicalUrl: urlSchema.optional(),
  excerpt: summarySchema.optional(),
  author: z.string().trim().min(1).max(120),
  publishedAt: isoDateTimeSchema,
  updatedAt: isoDateTimeSchema.optional(),
  tags: z.array(z.string().trim().min(1).max(80)).default([]),
  bodyBlocks: z
    .array(
      strictObject({
        heading: z.string().trim().min(1).max(120).optional(),
        body: z.string().trim().min(1).max(6_000)
      })
    )
    .default([])
});

export type ArticleKind = z.infer<typeof articleKindSchema>;
export type ArticlePayload = z.infer<typeof articlePayloadSchema>;
