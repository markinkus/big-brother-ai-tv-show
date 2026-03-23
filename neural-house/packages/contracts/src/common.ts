import { z } from "zod";

export const idSchema = z.string().trim().min(1);
export const slugSchema = z
  .string()
  .trim()
  .min(1)
  .regex(/^[a-z0-9]+(?:-[a-z0-9]+)*$/u, "Expected a kebab-case slug");
export const titleSchema = z.string().trim().min(1).max(160);
export const summarySchema = z.string().trim().min(1).max(2_000);
export const descriptionSchema = z.string().trim().min(1).max(10_000);
export const isoDateTimeSchema = z.string().datetime({ offset: true });
export const isoDateSchema = z.string().date();
export const urlSchema = z.string().url();
export const nonEmptyListSchema = <T extends z.ZodTypeAny>(itemSchema: T) =>
  z.array(itemSchema).min(1);

export const contactHandleSchema = z
  .string()
  .trim()
  .min(1)
  .max(64)
  .regex(/^[a-z0-9._-]+$/iu, "Expected a social or contact handle");

export const safeNumberSchema = z.number().finite();

export const localeSchema = z
  .string()
  .trim()
  .min(2)
  .max(35)
  .regex(/^[a-z]{2,3}(?:-[a-z0-9]{2,8})*$/iu, "Expected a locale tag");

export const strictObject = <T extends z.ZodRawShape>(shape: T) =>
  z.object(shape).strict();

export type Id = z.infer<typeof idSchema>;
export type Slug = z.infer<typeof slugSchema>;
export type IsoDateTime = z.infer<typeof isoDateTimeSchema>;
