"""
Generate realistic 2026 congressional trade sample data
"""

import random
from datetime import datetime, timedelta
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Real politicians who actively trade
POLITICIANS = [
    {"name": "Nancy Pelosi", "party": "D", "chamber": "House", "state": "CA"},
    {"name": "Tommy Tuberville", "party": "R", "chamber": "Senate", "state": "AL"},
    {"name": "Dan Crenshaw", "party": "R", "chamber": "House", "state": "TX"},
    {"name": "Mark Green", "party": "R", "chamber": "House", "state": "TN"},
    {"name": "Josh Gottheimer", "party": "D", "chamber": "House", "state": "NJ"},
    {"name": "Marjorie Taylor Greene", "party": "R", "chamber": "House", "state": "GA"},
    {"name": "Michael McCaul", "party": "R", "chamber": "House", "state": "TX"},
    {"name": "Debbie Wasserman Schultz", "party": "D", "chamber": "House", "state": "FL"},
    {"name": "Virginia Foxx", "party": "R", "chamber": "House", "state": "NC"},
    {"name": "Ro Khanna", "party": "D", "chamber": "House", "state": "CA"},
    {"name": "Austin Scott", "party": "R", "chamber": "House", "state": "GA"},
    {"name": "John Curtis", "party": "R", "chamber": "House", "state": "UT"},
    {"name": "Susie Lee", "party": "D", "chamber": "House", "state": "NV"},
    {"name": "Kathy Manning", "party": "D", "chamber": "House", "state": "NC"},
    {"name": "Pete Sessions", "party": "R", "chamber": "House", "state": "TX"},
]

# Hot stocks in 2026
STOCKS = [
    {"ticker": "NVDA", "company": "NVIDIA Corporation"},
    {"ticker": "TSLA", "company": "Tesla Inc"},
    {"ticker": "AAPL", "company": "Apple Inc"},
    {"ticker": "MSFT", "company": "Microsoft Corporation"},
    {"ticker": "GOOGL", "company": "Alphabet Inc Class A"},
    {"ticker": "META", "company": "Meta Platforms Inc"},
    {"ticker": "AMD", "company": "Advanced Micro Devices"},
    {"ticker": "AMZN", "company": "Amazon.com Inc"},
    {"ticker": "PLTR", "company": "Palantir Technologies"},
    {"ticker": "COIN", "company": "Coinbase Global Inc"},
    {"ticker": "SHOP", "company": "Shopify Inc"},
    {"ticker": "RBLX", "company": "Roblox Corporation"},
    {"ticker": "CRWD", "company": "CrowdStrike Holdings"},
    {"ticker": "SNOW", "company": "Snowflake Inc"},
    {"ticker": "NET", "company": "Cloudflare Inc"},
    {"ticker": "JPM", "company": "JPMorgan Chase & Co"},
    {"ticker": "BAC", "company": "Bank of America Corp"},
    {"ticker": "GS", "company": "Goldman Sachs Group"},
    {"ticker": "V", "company": "Visa Inc"},
    {"ticker": "MA", "company": "Mastercard Inc"},
    {"ticker": "LMT", "company": "Lockheed Martin Corp"},
    {"ticker": "RTX", "company": "RTX Corporation"},
    {"ticker": "BA", "company": "Boeing Company"},
    {"ticker": "XOM", "company": "Exxon Mobil Corporation"},
    {"ticker": "CVX", "company": "Chevron Corporation"},
]

# Amount ranges (realistic for congress members)
AMOUNT_RANGES = [
    (1001, 15000),
    (15001, 50000),
    (50001, 100000),
    (100001, 250000),
    (250001, 500000),
    (500001, 1000000),
    (1000001, 5000000),
]


def generate_trade_date():
    """Generate random date in Jan-Feb 2026"""
    start = datetime(2026, 1, 1)
    end = datetime(2026, 2, 13)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).date()


def generate_trades(count=400):
    """Generate realistic congressional trades"""
    trades = []

    for _ in range(count):
        politician = random.choice(POLITICIANS)
        stock = random.choice(STOCKS)
        trade_type = random.choices(["Purchase", "Sale"], weights=[70, 30])[0]  # More purchases
        amount_range = random.choice(AMOUNT_RANGES)

        trade_date = generate_trade_date()
        disclosure_date = trade_date + timedelta(days=random.randint(1, 45))

        trade = {
            "member_name": politician["name"],
            "chamber": politician["chamber"],
            "party": politician["party"],
            "state": politician["state"],
            "ticker": stock["ticker"],
            "company_name": stock["company"],
            "asset_type": "Stock",
            "trade_type": trade_type,
            "amount_low": amount_range[0],
            "amount_high": amount_range[1],
            "trade_date": str(trade_date),
            "disclosure_date": str(disclosure_date),
            "source_url": "https://efdsearch.senate.gov/search/",
            "raw_data": "{}",
        }

        trades.append(trade)

    # Sort by date (most recent first)
    trades.sort(key=lambda x: x["trade_date"], reverse=True)

    return trades


def load_to_database(trades):
    """Load generated trades to Supabase"""
    print(f"\nGenerating {len(trades)} fresh 2026 trades...")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Clear old test data first (optional - comment out to keep old data)
    print("Clearing old 2024 test data...")
    try:
        # Delete trades from 2024
        supabase.table("trades").delete().lt("trade_date", "2026-01-01").execute()
        print("✓ Old data cleared")
    except Exception as e:
        print(f"Warning: Could not clear old data: {e}")

    # Insert new trades in batches
    batch_size = 50
    inserted = 0

    for i in range(0, len(trades), batch_size):
        batch = trades[i : i + batch_size]
        try:
            result = supabase.table("trades").insert(batch).execute()
            inserted += len(result.data)
            print(f"✓ Inserted batch {i // batch_size + 1}: {len(result.data)} trades")
        except Exception as e:
            print(f"✗ Error: {e}")

    print(f"\n{'='*60}")
    print(f"SUCCESS! Inserted {inserted} fresh 2026 trades")
    print(f"{'='*60}")

    # Show sample
    print("\nSample of recent trades:")
    for trade in trades[:5]:
        print(f"  {trade['trade_date']} | {trade['member_name']:25s} | {trade['ticker']:6s} | ${trade['amount_low']:>8,} - ${trade['amount_high']:>8,}")


if __name__ == "__main__":
    trades = generate_trades(400)  # Generate 400 trades
    load_to_database(trades)
    print("\n✓ Done! Refresh your dashboard to see the new data!")
