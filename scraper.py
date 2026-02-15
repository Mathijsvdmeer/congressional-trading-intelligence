"""
Congressional Trade Scraper
Pulls real trade data from multiple sources and loads into Supabase.

Sources:
  1. House Stock Watcher (housestockwatcher.com) - House trades, no auth needed
  2. Finnhub API (finnhub.io) - Both chambers, free API key

Usage:
  python scraper.py              # Run full scrape from all sources
  python scraper.py --source hsw # House Stock Watcher only
  python scraper.py --source fin # Finnhub only
  python scraper.py --dry-run    # Preview without writing to DB
"""

import os
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# ============================================
# CONFIG
# ============================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
FINNHUB_KEY = os.getenv("FINNHUB_API_KEY")

# Top traded tickers by congress members - we'll query Finnhub for each
# (Finnhub requires a symbol parameter)
POPULAR_TICKERS = [
    "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "NVDA", "TSLA",
    "AMD", "INTC", "AVGO", "QCOM", "CRM", "NFLX", "DIS", "CMCSA",
    "JPM", "BAC", "WFC", "GS", "MS", "V", "MA", "AXP",
    "XOM", "CVX", "COP", "OXY", "HAL", "SLB", "VLO", "PSX", "MPC",
    "LMT", "RTX", "NOC", "GD", "BA", "HII", "LHX",
    "UNH", "JNJ", "PFE", "MRK", "ABT", "TMO", "ISRG", "DXCM",
    "ABBV", "LLY", "BMY", "AMGN", "GILD", "REGN", "MRNA", "BNTX",
    "WMT", "COST", "TGT", "HD", "LOW", "SBUX", "MCD", "NKE",
    "BRK.B", "SPY", "QQQ", "IWM", "DIA",
    "RIVN", "RBLX", "PLTR", "SNOW", "NET", "CRWD", "ZS", "PANW",
    "F", "GM", "UBER", "ABNB", "SQ", "PYPL", "SHOP", "COIN",
    "T", "VZ", "TMUS",
    "SO", "NEE", "DUK", "AEP",
    "PG", "KO", "PEP",
    "CI", "HCA", "ELV",
    "CAT", "DE", "HON", "MMM", "GE",
]

HEADERS = {
    "User-Agent": "CongressTradeTracker/1.0 (research project)",
    "Accept": "application/json",
}

# Amount string -> (low, high) mapping
AMOUNT_RANGES = {
    "$1,001 - $15,000": (1001, 15000),
    "$1,001 -": (1001, 15000),
    "$15,001 - $50,000": (15001, 50000),
    "$15,001 -": (15001, 50000),
    "$50,001 - $100,000": (50001, 100000),
    "$50,001 -": (50001, 100000),
    "$100,001 - $250,000": (100001, 250000),
    "$100,001 -": (100001, 250000),
    "$250,001 - $500,000": (250001, 500000),
    "$250,001 -": (250001, 500000),
    "$500,001 - $1,000,000": (500001, 1000000),
    "$500,001 -": (500001, 1000000),
    "$1,000,001 - $5,000,000": (1000001, 5000000),
    "$1,000,001 -": (1000001, 5000000),
    "$5,000,001 - $25,000,000": (5000001, 25000000),
    "$5,000,001 -": (5000001, 25000000),
    "$25,000,001 - $50,000,000": (25000001, 50000000),
    "$50,000,001 and Over": (50000001, 100000000),
    "Over $50,000,000": (50000001, 100000000),
}

# State lookup from district code (e.g. "CA12" -> "CA")
def extract_state(district):
    if district and len(district) >= 2:
        return district[:2].upper()
    return None


# ============================================
# AMOUNT PARSING
# ============================================

def parse_amount(amount_str):
    """Parse STOCK Act amount range string into (low, high) integers."""
    if not amount_str:
        return None, None

    amount_str = amount_str.strip()

    # Direct lookup
    if amount_str in AMOUNT_RANGES:
        return AMOUNT_RANGES[amount_str]

    # Try partial match
    for key, (low, high) in AMOUNT_RANGES.items():
        if key in amount_str or amount_str in key:
            return low, high

    # Try to extract numbers
    import re
    numbers = re.findall(r'[\d,]+', amount_str)
    if len(numbers) >= 2:
        try:
            low = int(numbers[0].replace(',', ''))
            high = int(numbers[1].replace(',', ''))
            return low, high
        except ValueError:
            pass
    elif len(numbers) == 1:
        try:
            val = int(numbers[0].replace(',', ''))
            return val, val
        except ValueError:
            pass

    return None, None


def normalize_trade_type(raw_type):
    """Normalize trade type to match DB constraint: Purchase, Sale, Exchange."""
    if not raw_type:
        return None
    raw = raw_type.lower().strip()
    if "purchase" in raw or "buy" in raw:
        return "Purchase"
    elif "sale" in raw or "sell" in raw:
        return "Sale"
    elif "exchange" in raw or "swap" in raw:
        return "Exchange"
    return None


def normalize_chamber(position):
    """Normalize chamber from various formats."""
    if not position:
        return None
    pos = position.lower().strip()
    if "senator" in pos or "senate" in pos:
        return "Senate"
    elif "representative" in pos or "house" in pos or "rep" in pos:
        return "House"
    return None


# ============================================
# SOURCE 1: HOUSE STOCK WATCHER
# ============================================

def fetch_house_stock_watcher():
    """
    Fetch all House trades from housestockwatcher.com.
    Returns list of normalized trade dicts.
    """
    print("\n[HSW] Fetching House Stock Watcher data...")

    trades = []
    urls_to_try = [
        "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json",
        "https://housestockwatcher.com/api",
    ]

    raw_data = None
    for url in urls_to_try:
        try:
            print(f"  Trying: {url}")
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                raw_data = resp.json()
                print(f"  Success! Got {len(raw_data) if isinstance(raw_data, list) else '?'} records")
                break
            else:
                print(f"  Got status {resp.status_code}, trying next...")
        except Exception as e:
            print(f"  Error: {e}, trying next...")

    if not raw_data:
        print("  [HSW] All URLs failed. Skipping House Stock Watcher.")
        return []

    # Handle both list format and dict-with-data format
    if isinstance(raw_data, dict):
        raw_data = raw_data.get("data", raw_data.get("transactions", []))

    for record in raw_data:
        try:
            # Skip if no ticker
            ticker = record.get("ticker", "").strip()
            if not ticker or ticker == "--" or ticker == "N/A" or len(ticker) > 10:
                continue

            trade_type = normalize_trade_type(
                record.get("type", record.get("transaction_type", ""))
            )
            if not trade_type:
                continue

            # Parse amount
            amount_str = record.get("amount", "")
            amount_low, amount_high = parse_amount(amount_str)

            # Parse dates
            trade_date = record.get("transaction_date", record.get("trade_date"))
            disclosure_date = record.get("disclosure_date")

            if not trade_date:
                continue

            # Extract member name
            member_name = record.get("representative", record.get("politician", "")).strip()
            if not member_name:
                continue

            # Build normalized trade
            trade = {
                "member_name": member_name,
                "chamber": "House",
                "party": record.get("party", None),
                "state": extract_state(record.get("district", "")),
                "ticker": ticker.upper(),
                "company_name": record.get("asset_description", record.get("asset", ""))[:200],
                "asset_type": "Stock",
                "trade_type": trade_type,
                "amount_low": amount_low,
                "amount_high": amount_high,
                "trade_date": trade_date,
                "disclosure_date": disclosure_date,
                "source_url": record.get("ptr_link", record.get("source_url", "")),
                "raw_data": json.dumps(record),
            }
            trades.append(trade)

        except Exception as e:
            continue  # Skip malformed records silently

    print(f"  [HSW] Parsed {len(trades)} valid House trades")
    return trades


# ============================================
# SOURCE 2: FINNHUB
# ============================================

def fetch_finnhub_trades():
    """
    Fetch congressional trades from Finnhub API.
    Queries per-ticker (API requires symbol param).
    Returns list of normalized trade dicts.
    """
    if not FINNHUB_KEY:
        print("\n[FINNHUB] No API key found. Set FINNHUB_API_KEY in .env")
        return []

    print(f"\n[FINNHUB] Fetching trades for {len(POPULAR_TICKERS)} tickers...")
    print(f"  (Free tier: 60 req/min — this will take ~{len(POPULAR_TICKERS) // 60 + 2} minutes)")

    trades = []
    seen = set()  # Dedupe within Finnhub results

    # Date range: last 2 years to get plenty of data
    date_from = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
    date_to = datetime.now().strftime("%Y-%m-%d")

    for i, ticker in enumerate(POPULAR_TICKERS):
        try:
            url = f"https://finnhub.io/api/v1/stock/congressional-trading"
            params = {
                "symbol": ticker,
                "from": date_from,
                "to": date_to,
                "token": FINNHUB_KEY,
            }

            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)

            if resp.status_code == 429:
                # Rate limited - wait and retry
                print(f"  Rate limited at {ticker}. Waiting 60s...")
                time.sleep(62)
                resp = requests.get(url, params=params, headers=HEADERS, timeout=15)

            if resp.status_code != 200:
                if i % 20 == 0:
                    print(f"  [{i}/{len(POPULAR_TICKERS)}] {ticker}: HTTP {resp.status_code}")
                continue

            data = resp.json()
            records = data.get("data", [])

            for record in records:
                try:
                    name = record.get("name", "").strip()
                    txn_date = record.get("transactionDate", "")
                    txn_type = normalize_trade_type(record.get("transactionType", ""))

                    if not name or not txn_date or not txn_type:
                        continue

                    # Dedupe key
                    key = f"{name}|{ticker}|{txn_date}|{txn_type}"
                    if key in seen:
                        continue
                    seen.add(key)

                    # Parse amounts - Finnhub provides amountFrom/amountTo directly
                    amount_low = record.get("amountFrom")
                    amount_high = record.get("amountTo")
                    if not amount_low or not amount_high:
                        amount_low, amount_high = parse_amount(
                            record.get("transactionAmount", "")
                        )

                    chamber = normalize_chamber(record.get("position", ""))

                    trade = {
                        "member_name": name,
                        "chamber": chamber,
                        "party": None,  # Finnhub doesn't reliably provide party
                        "state": None,  # Finnhub doesn't provide state
                        "ticker": ticker.upper(),
                        "company_name": record.get("assetName", "")[:200],
                        "asset_type": "Stock",
                        "trade_type": txn_type,
                        "amount_low": amount_low,
                        "amount_high": amount_high,
                        "trade_date": txn_date,
                        "disclosure_date": record.get("filingDate"),
                        "source_url": record.get("sourceUrl", ""),
                        "raw_data": json.dumps(record),
                    }
                    trades.append(trade)

                except Exception:
                    continue

            if i % 10 == 0:
                print(f"  [{i}/{len(POPULAR_TICKERS)}] {ticker}: {len(records)} trades found | Total: {len(trades)}")

            # Rate limiting: ~55 requests per minute to stay safe
            time.sleep(1.1)

        except Exception as e:
            print(f"  [{i}] {ticker}: Error - {e}")
            continue

    print(f"  [FINNHUB] Total: {len(trades)} unique trades")
    return trades


# ============================================
# SUPABASE LOADER
# ============================================

def load_to_supabase(trades, dry_run=False):
    """
    Load trades into Supabase, skipping duplicates.
    Dedupes on (member_name, ticker, trade_date, trade_type).
    """
    if not trades:
        print("\n[LOAD] No trades to load.")
        return 0

    print(f"\n[LOAD] Loading {len(trades)} trades into Supabase...")

    if dry_run:
        print("  DRY RUN - showing first 5 trades:")
        for t in trades[:5]:
            print(f"    {t['trade_date']} | {t['member_name']:25s} | {t['ticker']:6s} | {t['trade_type']:8s} | ${t.get('amount_low', '?'):>10} - ${t.get('amount_high', '?'):>10}")
        print(f"  ... and {len(trades) - 5} more")
        return 0

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Get existing trades for dedup
    print("  Fetching existing trades for dedup check...")
    existing = set()
    try:
        # Fetch in batches (Supabase default limit is 1000)
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
        print(f"  Warning: Could not fetch existing trades ({e}). May insert duplicates.")

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

    # Insert in batches of 50
    inserted = 0
    batch_size = 50
    for i in range(0, len(new_trades), batch_size):
        batch = new_trades[i : i + batch_size]
        try:
            result = supabase.table("trades").insert(batch).execute()
            inserted += len(result.data)
            print(f"  Inserted batch {i // batch_size + 1}: {len(result.data)} trades")
        except Exception as e:
            print(f"  Error inserting batch {i // batch_size + 1}: {e}")
            # Try inserting one by one to find the bad record
            for trade in batch:
                try:
                    supabase.table("trades").insert(trade).execute()
                    inserted += 1
                except Exception as e2:
                    print(f"    Skipped: {trade['member_name']} {trade['ticker']} {trade['trade_date']} - {e2}")

    print(f"\n  [LOAD] Done! Inserted {inserted} new trades.")
    return inserted


# ============================================
# STATS
# ============================================

def print_stats():
    """Print current database stats."""
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    print("\n" + "=" * 60)
    print("DATABASE STATS")
    print("=" * 60)

    # Total trades
    result = supabase.table("trades").select("id", count="exact").execute()
    print(f"  Total trades:   {result.count}")

    # By chamber
    for chamber in ["House", "Senate"]:
        result = supabase.table("trades").select("id", count="exact").eq("chamber", chamber).execute()
        print(f"  {chamber} trades: {result.count}")

    # Date range
    oldest = supabase.table("trades").select("trade_date").order("trade_date").limit(1).execute()
    newest = supabase.table("trades").select("trade_date").order("trade_date", desc=True).limit(1).execute()
    if oldest.data and newest.data:
        print(f"  Date range:     {oldest.data[0]['trade_date']} to {newest.data[0]['trade_date']}")

    # Unique members
    result = supabase.table("trades").select("member_name").execute()
    unique_members = set(r["member_name"] for r in result.data)
    print(f"  Unique members: {len(unique_members)}")

    # Unique tickers
    result = supabase.table("trades").select("ticker").execute()
    unique_tickers = set(r["ticker"] for r in result.data)
    print(f"  Unique tickers: {len(unique_tickers)}")

    print("=" * 60)


# ============================================
# MAIN
# ============================================

def main():
    parser = argparse.ArgumentParser(description="Congressional Trade Scraper")
    parser.add_argument("--source", choices=["hsw", "fin", "all"], default="all",
                        help="Data source: hsw=House Stock Watcher, fin=Finnhub, all=both")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview trades without writing to DB")
    parser.add_argument("--stats", action="store_true",
                        help="Print DB stats and exit")
    args = parser.parse_args()

    print("=" * 60)
    print("CONGRESSIONAL TRADE SCRAPER")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Check config
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nERROR: Missing SUPABASE_URL or SUPABASE_KEY in .env")
        print("Create a .env file with:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_KEY=your_service_role_key")
        return

    if args.stats:
        print_stats()
        return

    # Scrape
    all_trades = []

    if args.source in ("hsw", "all"):
        hsw_trades = fetch_house_stock_watcher()
        all_trades.extend(hsw_trades)

    if args.source in ("fin", "all"):
        fin_trades = fetch_finnhub_trades()
        all_trades.extend(fin_trades)

    if not all_trades:
        print("\nNo trades fetched from any source.")
        print("Check your internet connection and API keys.")
        return

    # Summary before loading
    print(f"\n{'=' * 60}")
    print(f"SCRAPE SUMMARY")
    print(f"{'=' * 60}")
    print(f"  Total trades scraped: {len(all_trades)}")

    chambers = {}
    for t in all_trades:
        c = t.get("chamber", "Unknown")
        chambers[c] = chambers.get(c, 0) + 1
    for c, count in sorted(chambers.items()):
        print(f"  {c}: {count}")

    types = {}
    for t in all_trades:
        tt = t.get("trade_type", "Unknown")
        types[tt] = types.get(tt, 0) + 1
    for tt, count in sorted(types.items()):
        print(f"  {tt}: {count}")

    # Load
    inserted = load_to_supabase(all_trades, dry_run=args.dry_run)

    # Final stats
    if not args.dry_run:
        print_stats()

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
