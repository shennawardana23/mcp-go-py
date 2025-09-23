-- Initial schema migration for MCP-PBA-TUNNEL
-- Creates all required tables for the prompt engineering system

-- Create prompt_templates table
CREATE TABLE IF NOT EXISTS prompt_templates (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    template_content TEXT NOT NULL,
    variables JSON,
    version VARCHAR(20) DEFAULT '1.0.0',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100)
);

-- Create indexes for prompt_templates
CREATE INDEX IF NOT EXISTS idx_prompt_templates_name ON prompt_templates(name);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_category ON prompt_templates(category);
CREATE INDEX IF NOT EXISTS idx_prompt_templates_active ON prompt_templates(is_active);

-- Create prompt_usage table
CREATE TABLE IF NOT EXISTS prompt_usage (
    id VARCHAR(36) PRIMARY KEY,
    prompt_id VARCHAR(36) REFERENCES prompt_templates(id),
    ai_model VARCHAR(100),
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    avg_response_time INTEGER DEFAULT 0,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for prompt_usage
CREATE INDEX IF NOT EXISTS idx_prompt_usage_prompt_id ON prompt_usage(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_ai_model ON prompt_usage(ai_model);
CREATE INDEX IF NOT EXISTS idx_prompt_usage_last_used ON prompt_usage(last_used_at);

-- Create ai_configurations table
CREATE TABLE IF NOT EXISTS ai_configurations (
    id VARCHAR(36) PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    provider VARCHAR(100) NOT NULL,
    api_base_url VARCHAR(500),
    max_tokens INTEGER DEFAULT 4000,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for ai_configurations
CREATE INDEX IF NOT EXISTS idx_ai_configurations_model_name ON ai_configurations(model_name);
CREATE INDEX IF NOT EXISTS idx_ai_configurations_provider ON ai_configurations(provider);
CREATE INDEX IF NOT EXISTS idx_ai_configurations_active ON ai_configurations(is_active);

-- Create generated_content table
CREATE TABLE IF NOT EXISTS generated_content (
    id VARCHAR(36) PRIMARY KEY,
    prompt_id VARCHAR(36) REFERENCES prompt_templates(id),
    ai_model VARCHAR(100),
    input_variables JSON,
    generated_content TEXT,
    tokens_used INTEGER,
    response_time INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for generated_content
CREATE INDEX IF NOT EXISTS idx_generated_content_prompt_id ON generated_content(prompt_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_ai_model ON generated_content(ai_model);
CREATE INDEX IF NOT EXISTS idx_generated_content_created_at ON generated_content(created_at);

-- Create memory_entries table
CREATE TABLE IF NOT EXISTS memory_entries (
    id VARCHAR(36) PRIMARY KEY,
    conversation_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    entry_metadata JSON,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ttl_seconds INTEGER DEFAULT 3600
);

-- Create indexes for memory_entries
CREATE INDEX IF NOT EXISTS idx_memory_entries_conversation_id ON memory_entries(conversation_id);
CREATE INDEX IF NOT EXISTS idx_memory_entries_session_id ON memory_entries(session_id);
CREATE INDEX IF NOT EXISTS idx_memory_entries_timestamp ON memory_entries(timestamp);

-- Create prompt_chains table
CREATE TABLE IF NOT EXISTS prompt_chains (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    steps JSON,
    inputs JSON,
    outputs JSON,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for prompt_chains
CREATE INDEX IF NOT EXISTS idx_prompt_chains_name ON prompt_chains(name);
CREATE INDEX IF NOT EXISTS idx_prompt_chains_status ON prompt_chains(status);

-- Create prompt_chain_executions table
CREATE TABLE IF NOT EXISTS prompt_chain_executions (
    id VARCHAR(36) PRIMARY KEY,
    chain_id VARCHAR(36) REFERENCES prompt_chains(id),
    execution_id VARCHAR(255),
    step_number INTEGER,
    prompt_id VARCHAR(36) REFERENCES prompt_templates(id),
    input_data JSON,
    output_data JSON,
    execution_time INTEGER,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for prompt_chain_executions
CREATE INDEX IF NOT EXISTS idx_prompt_chain_executions_chain_id ON prompt_chain_executions(chain_id);
CREATE INDEX IF NOT EXISTS idx_prompt_chain_executions_execution_id ON prompt_chain_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_prompt_chain_executions_prompt_id ON prompt_chain_executions(prompt_id);
CREATE INDEX IF NOT EXISTS idx_prompt_chain_executions_status ON prompt_chain_executions(status);

-- Create migration tracking table
CREATE TABLE IF NOT EXISTS schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert default AI configurations
INSERT INTO ai_configurations (id, model_name, provider, api_base_url, max_tokens, temperature)
VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'gpt-4', 'openai', 'https://api.openai.com/v1', 4000, 0.7),
    ('550e8400-e29b-41d4-a716-446655440002', 'gpt-3.5-turbo', 'openai', 'https://api.openai.com/v1', 4000, 0.7),
    ('550e8400-e29b-41d4-a716-446655440003', 'claude-3-sonnet', 'anthropic', 'https://api.anthropic.com', 4000, 0.7)
ON CONFLICT (model_name) DO NOTHING;
