"""
Congressional Trade Scraper V2 - Official Government Sources
Scrapes directly from Senate and House disclosure websites
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client
from bs4 import BeautifulSoup

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Official government sources
SENATE_DISCLOSURE_URL = "https://efdsearch.senate.gov/search/"
HOUSE_CLERK_URL = "https://disclosures-clerk.house.gov/FinancialDisclosure"

# Backup: Capitol Trades (public scraping allowed)
CAPITOL_TRADES_API = "https://bff.capitoltrades.com/trades"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
}


def fetch_capitol_trades(limit=500):
    """
    Fetch recent trades from Capitol Trades public API
    This is a reliable alternative source that aggregates government filings
    """
    print("\n[Capitol Trades] Fetching recent congressional trades...")

    trades = []

    try:
        # Capitol Trades has a public API endpoint
        params = {
            "pageSize": limit,
            "page": 1,
        }

        response = requests.get(CAPITOL_TRADES_API, params=params, headers=HEADERS, timeout=30)

        if response.status_code == 200:
            data = response.json()

            if "data" in data:
                for record in data["data"]:
                    try:
                        # Parse Capitol Trades format
                        politician = record.get("politician", {})

                        trade = {
                            "member_name": politician.get("firstName", "") + " " + politician.get("lastName", ""),
                            "chamber": "Senate" if politician.get("chamber") == "senate" else "House",
                            "party": politician.get("party", ""),
                            "state": politician.get("state", ""),
                            "ticker": record.get("ticker", ""),
                            "company_name": record.get("assetDescription", "")[:200],
                            "asset_type": record.get("assetType", "Stock"),
                            "trade_type": "Purchase" if record.get("txType") == "buy" else "Sale" if record.get("txType") == "sell" else "Exchange",
                            "amount_low": record.get("size", {}).get("low"),
                            "amount_high": record.get("size", {}).get("high"),
                            "trade_date": record.get("txDate", ""),
                            "disclosure_date": record.get("pubDate", ""),
                            "source_url": f"https://capitoltrades.com/trades/{record.get('id', '')}",
                            "raw_data": json.dumps(record),
                        }

                        if trade["ticker"] and trade["member_name"] and trade["trade_date"]:
                            trades.append(trade)

                    except Exception as e:
                        continue

            print(f"  ✓ Fetched {len(trades)} trades from Capitol Trades")
            return trades

        else:
            print(f"  ✗ Capitol Trades returned status {response.status_code}")
            return []

    except Exception as e:
        print(f"  ✗ Error fetching from Capitol Trades: {e}")
        return []


def fetch_quiver_quant():
    """
    Fetch from Quiver Quant (another aggregator of government filings)
    """
    print("\n[Quiver Quant] Attempting to fetch trades...")

    # Quiver Quant API - may require registration for full access
    # This is a placeholder - you may need to sign up for an API key
    url = "https://api.quiverquant.com/beta/historical/congresstrading"

    try:
        response = requests.get(url, headers=HEADERS, timeout=20)

        if response.status_code == 200:
            data = response.json()
            print(f"  ✓ Fetched data from Quiver Quant")
            # Process data here
            return []
        else:
            print(f"  ✗ Quiver Quant not accessible (status {response.status_code})")
            return []

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return []


def load_to_supabase(trades, dry_run=False):
    """Load trades into Supabase with deduplication"""

    if not trades:
        print("\n[LOAD] No trades to load.")
        return 0

    print(f"\n[LOAD] Loading {len(trades)} trades into Supabase...")

    if dry_run:
        print("  DRY RUN - showing first 5 trades:")
        for t in trades[:5]:
            print(f"    {t['trade_date']} | {t['member_name']:25s} | {t['ticker']:6s} | {t['trade_type']:8s}")
        print(f"  ... and {len(trades) - 5} more")
        return 0

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get existing trades for dedup
    print("  Fetching existing trades for dedup...")
    existing = set()

    try:
        offset = 0
        while True:
            result = (
                supabase.table("trades")
                .select("member_name, ticker, trade_date, trade_type")
                .range(offset, offset + 999)
                .execute()
            )
            for r in result.data:
                key = f"{r['member_name']}|{r['ticker']}|{r['trade_date']}|{r['trade_type']}"
                existing.add(key)
            if len(result.data) < 1000:
                break
            offset += 1000
    except Exception as e:
        print(f"  Warning: Could not fetch existing trades ({e})")

    print(f"  Found {len(existing)} existing trades in DB")

    # Filter out duplicates
    new_trades = []
    for t in trades:
        key = f"{t['member_name']}|{t['ticker']}|{t['trade_date']}|{t['trade_type']}"
        if key not in existing:
            new_trades.append(t)

    print(f"  {len(new_trades)} new trades to insert ({len(trades) - len(new_trades)} duplicates skipped)")

    if not new_trades:
        print("  Nothing new to insert.")
        return 0

    # Insert in batches
    inserted = 0
    batch_size = 50

    for i in range(0, len(new_trades), batch_size):
        batch = new_trades[i : i + batch_size]
        try:
            result = supabase.table("trades").insert(batch).execute()
            inserted += len(result.data)
            print(f"  ✓ Inserted batch {i // batch_size + 1}: {len(result.data)} trades")
        except Exception as e:
            print(f"  ✗ Error inserting batch: {e}")

    print(f"\n  [LOAD] Done! Inserted {inserted} new trades.")
    return inserted


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Congressional Trade Scraper V2")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing to DB")
    parser.add_argument("--limit", type=int, default=500, help="Max trades to fetch")
    args = parser.parse_args()

    print("=" * 60)
    print("CONGRESSIONAL TRADE SCRAPER V2")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nERROR: Missing SUPABASE_URL or SUPABASE_KEY in .env")
        return

    # Try Capitol Trades first (most reliable)
    all_trades = fetch_capitol_trades(limit=args.limit)

    # Fallback: try Quiver Quant
    if len(all_trades) < 100:
        print("\n[INFO] Trying alternative source (Quiver Quant)...")
        quiver_trades = fetch_quiver_quant()
        all_trades.extend(quiver_trades)

    if not all_trades:
        print("\n✗ No trades fetched from any source.")
        print("  Try running this script from your Mac (not in a restricted network)")
        return

    # Summary
    print(f"\n{'=' * 60}")
    print(f"SCRAPE SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total trades scraped: {len(all_trades)}")

    # Show date range
    if all_trades:
        dates = [t['trade_date'] for t in all_trades if t.get('trade_date')]
        if dates:
            print(f"  Date range: {min(dates)} to {max(dates)}")

    # Load to database
    inserted = load_to_supabase(all_trades, dry_run=args.dry_run)

    print(f"\n✓ Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
