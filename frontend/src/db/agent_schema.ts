/**
 * Drizzle schema for agent interactions and chat functionality
 * Extends the existing schema with RFP automation specific tables
 */
import {
  pgEnum,
  pgTable,
  text,
  uuid,
  timestamp,
  boolean,
  json,
  integer,
} from "drizzle-orm/pg-core";
import { usersTable, rfpsTable } from "./schema";

/**
 * ENUMS
 */
export const messageTypeEnum = pgEnum("message_type", [
  "user",
  "assistant",
]);

export const interactionTypeEnum = pgEnum("interaction_type", [
  "response",
  "tool_call",
  "error",
]);

/**
 * CHAT SESSIONS TABLE
 * Stores agent state and workflow progress
 */
export const chatSessionsTable = pgTable("chat_sessions", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: text("session_id").unique().notNull(),
  currentStep: text("current_step").default("IDLE"),
  nextNode: text("next_node").default("main_agent"),
  rfpsIdentified: json("rfps_identified").$default(() => []),
  selectedRfp: json("selected_rfp"),
  userSelectedRfpId: text("user_selected_rfp_id"),
  technicalAnalysis: json("technical_analysis"),
  pricingAnalysis: json("pricing_analysis"),
  finalResponse: text("final_response"),
  reportPath: text("report_path"),
  productSummary: text("product_summary"),
  testSummary: text("test_summary"),
  waitingForUser: boolean("waiting_for_user").default(false),
  userPrompt: text("user_prompt"),
  error: text("error"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

export type InsertChatSession = typeof chatSessionsTable.$inferInsert;
export type SelectChatSession = typeof chatSessionsTable.$inferSelect;

/**
 * CHAT MESSAGES TABLE
 * Stores conversation history
 */
export const chatMessagesTable = pgTable("chat_messages", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: text("session_id").notNull(),
  messageType: messageTypeEnum("message_type").notNull(),
  content: text("content").notNull(),
  metadata: json("metadata").$default(() => ({})),
  createdAt: timestamp("created_at").defaultNow(),
});

export type InsertChatMessage = typeof chatMessagesTable.$inferInsert;
export type SelectChatMessage = typeof chatMessagesTable.$inferSelect;

/**
 * AGENT INTERACTIONS TABLE
 * Stores detailed agent interaction logs
 */
export const agentInteractionsTable = pgTable("agent_interactions", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: text("session_id").notNull(),
  agentName: text("agent_name").notNull(),
  interactionType: interactionTypeEnum("interaction_type").default("response"),
  inputData: json("input_data").$default(() => ({})),
  outputData: json("output_data").$default(() => ({})),
  reasoning: text("reasoning"),
  toolCalls: json("tool_calls").$default(() => []),
  createdAt: timestamp("created_at").defaultNow(),
});

export type InsertAgentInteraction = typeof agentInteractionsTable.$inferInsert;
export type SelectAgentInteraction = typeof agentInteractionsTable.$inferSelect;

/**
 * ENHANCED RFPs TABLE
 * Add analysis fields to existing RFPs table
 */
export const enhancedRfpsTable = rfpsTable; // This will be enhanced via migration
