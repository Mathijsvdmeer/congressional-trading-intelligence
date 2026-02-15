-- Create congressional_trades table in Supabase
CREATE TABLE IF NOT EXISTS public.congressional_trades (
    id BIGSERIAL PRIMARY KEY,
    member_name TEXT NOT NULL,
    trade_date DATE NOT NULL,
    disclosure_date DATE,
    ticker TEXT NOT NULL,
    trade_type TEXT NOT NULL,
    amount_low NUMERIC,
    amount_high NUMERIC,
    party TEXT,
    chamber TEXT,
    company_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_ticker ON public.congressional_trades(ticker);
CREATE INDEX IF NOT EXISTS idx_trade_date ON public.congressional_trades(trade_date);
CREATE INDEX IF NOT EXISTS idx_member_name ON public.congressional_trades(member_name);
CREATE INDEX IF NOT EXISTS idx_trade_type ON public.congressional_trades(trade_type);

-- Enable Row Level Security (optional, but recommended)
ALTER TABLE public.congressional_trades ENABLE ROW LEVEL SECURITY;

-- Create policy to allow public read access (for your API)
CREATE POLICY "Allow public read access" ON public.congressional_trades
    FOR SELECT USING (true);
