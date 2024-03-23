CREATE INDEX IF NOT EXISTS idx_name ON token_data (name);
CREATE INDEX IF NOT EXISTS idx_date ON token_data (date);
CREATE INDEX IF NOT EXISTS idx_ai_degen ON token_data (ai_degen);
CREATE INDEX IF NOT EXISTS idx_ai_price ON token_data (price);
CREATE INDEX IF NOT EXISTS idx_ai_memeability ON token_data (memeability);