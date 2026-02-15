#!/usr/bin/env python3
"""
Setup Supabase database table for congressional trades
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def setup_database():
    """Create the congressional_trades table"""
    print("🔧 Setting up Supabase database...")

    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # SQL to create table
    create_table_sql = """
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
    """

    try:
        # Execute SQL using Supabase's RPC or direct SQL execution
        result = supabase.rpc('exec_sql', {'sql': create_table_sql}).execute()
        print("✅ Database table created successfully!")
        return True
    except Exception as e:
        print(f"⚠️  Could not create table via RPC: {e}")
        print("\n📋 Please create the table manually:")
        print("1. Go to: https://supabase.com/dashboard/project/ujlnghtjnwnjilalazsx/editor")
        print("2. Click 'SQL Editor' in the left sidebar")
        print("3. Click 'New Query'")
        print("4. Copy and paste the SQL from 'create_table.sql'")
        print("5. Click 'Run' to execute")
        return False

if __name__ == "__main__":
    setup_database()
