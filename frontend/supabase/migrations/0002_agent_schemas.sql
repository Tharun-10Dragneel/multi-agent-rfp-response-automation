-- Agent interaction schemas for RFP Automation System

-- Chat sessions table for persisting agent state
CREATE TABLE "chat_sessions" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "session_id" text UNIQUE NOT NULL,
  "current_step" text DEFAULT 'IDLE',
  "next_node" text DEFAULT 'main_agent',
  "rfps_identified" jsonb DEFAULT '[]',
  "selected_rfp" jsonb,
  "user_selected_rfp_id" text,
  "technical_analysis" jsonb,
  "pricing_analysis" jsonb,
  "final_response" text,
  "report_path" text,
  "product_summary" text,
  "test_summary" text,
  "waiting_for_user" boolean DEFAULT false,
  "user_prompt" text,
  "error" text,
  "created_at" timestamp DEFAULT now(),
  "updated_at" timestamp DEFAULT now()
);

-- Chat messages table for conversation history
CREATE TABLE "chat_messages" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "session_id" text NOT NULL,
  "message_type" text NOT NULL, -- 'user' or 'assistant'
  "content" text NOT NULL,
  "metadata" jsonb DEFAULT '{}',
  "created_at" timestamp DEFAULT now()
);

-- Agent interactions table for detailed agent tracking
CREATE TABLE "agent_interactions" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
  "session_id" text NOT NULL,
  "agent_name" text NOT NULL,
  "interaction_type" text DEFAULT 'response',
  "input_data" jsonb DEFAULT '{}',
  "output_data" jsonb DEFAULT '{}',
  "reasoning" text,
  "tool_calls" jsonb DEFAULT '[]',
  "created_at" timestamp DEFAULT now()
);

-- Enhanced RFPs table with analysis fields
ALTER TABLE "rfps_table" 
ADD COLUMN "status" text DEFAULT 'identified',
ADD COLUMN "priority_score" numeric DEFAULT 0,
ADD COLUMN "budget_range" text,
ADD COLUMN "technical_requirements" jsonb DEFAULT '[]',
ADD COLUMN "sales_analysis" jsonb,
ADD COLUMN "technical_analysis" jsonb,
ADD COLUMN "pricing_analysis" jsonb,
ADD COLUMN "updated_at" timestamp DEFAULT now();

-- Indexes for performance
CREATE INDEX "chat_sessions_session_id_idx" ON "chat_sessions"("session_id");
CREATE INDEX "chat_messages_session_id_idx" ON "chat_messages"("session_id");
CREATE INDEX "chat_messages_created_at_idx" ON "chat_messages"("created_at");
CREATE INDEX "agent_interactions_session_id_idx" ON "agent_interactions"("session_id");
CREATE INDEX "agent_interactions_agent_name_idx" ON "agent_interactions"("agent_name");
CREATE INDEX "rfps_table_status_idx" ON "rfps_table"("status");

-- RLS (Row Level Security) policies
ALTER TABLE "chat_sessions" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "chat_messages" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "agent_interactions" ENABLE ROW LEVEL SECURITY;

-- Users can access their own sessions
CREATE POLICY "Users can view own chat sessions" ON "chat_sessions"
  FOR SELECT USING (auth.uid()::text = session_id);

CREATE POLICY "Users can insert own chat sessions" ON "chat_sessions"
  FOR INSERT WITH CHECK (auth.uid()::text = session_id);

CREATE POLICY "Users can update own chat sessions" ON "chat_sessions"
  FOR UPDATE USING (auth.uid()::text = session_id);

-- Users can access their own messages
CREATE POLICY "Users can view own chat messages" ON "chat_messages"
  FOR SELECT USING (auth.uid()::text = session_id);

CREATE POLICY "Users can insert own chat messages" ON "chat_messages"
  FOR INSERT WITH CHECK (auth.uid()::text = session_id);

-- Users can access their own agent interactions
CREATE POLICY "Users can view own agent interactions" ON "agent_interactions"
  FOR SELECT USING (auth.uid()::text = session_id);

CREATE POLICY "Users can insert own agent interactions" ON "agent_interactions"
  FOR INSERT WITH CHECK (auth.uid()::text = session_id);
