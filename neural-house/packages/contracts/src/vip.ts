import { z } from "zod";
import {
  contactHandleSchema,
  idSchema,
  isoDateSchema,
  strictObject,
  summarySchema
} from "./common.js";

export const vipRoleSchema = z.enum([
  "guest",
  "host",
  "judge",
  "sponsor",
  "press",
  "family",
  "alumni"
]);

export const vipAccessSchema = z.enum([
  "public",
  "greenroom",
  "backstage",
  "production",
  "restricted"
]);

export const vipPayloadSchema = strictObject({
  id: idSchema,
  seasonId: idSchema.optional(),
  fullName: z.string().trim().min(1).max(120),
  displayName: z.string().trim().min(1).max(120).optional(),
  role: vipRoleSchema,
  access: vipAccessSchema,
  status: z.enum(["invited", "confirmed", "arrived", "departed", "cancelled"]),
  contactHandle: contactHandleSchema.optional(),
  appearanceDate: isoDateSchema.optional(),
  notes: summarySchema.optional(),
  references: z.array(idSchema).default([])
});

export type VipRole = z.infer<typeof vipRoleSchema>;
export type VipAccess = z.infer<typeof vipAccessSchema>;
export type VipPayload = z.infer<typeof vipPayloadSchema>;
