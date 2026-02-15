#!/usr/bin/env python3
"""
Congressional Trading Data Fetcher
Uses multiple free APIs to get real congressional trading data
"""

import requests
import json
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

# Initialize Supabase
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def fetch_from_finnhub():
    """
    Fetch from Finnhub API (you already have API key!)
    Endpoint: https://finnhub.io/api/v1/stock/congress-trading
    """
    API_KEY = os.getenv("FINNHUB_API_KEY")

    print("🔍 Trying Finnhub API...")

    # Get trades for popular tickers
    tickers = ["NVDA", "TSLA", "AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    all_trades = []

    for ticker in tickers:
        try:
            url = f"https://finnhub.io/api/v1/stock/congress-trading?symbol={ticker}&token={API_KEY}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    all_trades.extend(data['data'])
                    print(f"✅ Got {len(data.get('data', []))} trades for {ticker}")
            else:
                print(f"❌ Finnhub error for {ticker}: {response.status_code}")
        except Exception as e:
            print(f"❌ Finnhub failed for {ticker}: {e}")

    return all_trades

def fetch_from_house_stock_watcher():
    """
    Fetch from House Stock Watcher public S3 bucket
    """
    print("\n🔍 Trying House Stock Watcher...")

    try:
        url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"
        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data)} trades from House Stock Watcher")
            return data
        else:
            print(f"❌ House Stock Watcher error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ House Stock Watcher failed: {e}")
        return []

def fetch_from_fmp():
    """
    Fetch from Financial Modeling Prep (free tier)
    Register at: https://site.financialmodelingprep.com/
    """
    print("\n🔍 Trying Financial Modeling Prep...")

    # You'll need to register for a free API key
    FMP_KEY = os.getenv("FMP_API_KEY", "")

    if not FMP_KEY:
        print("⚠️  No FMP_API_KEY found. Get one free at: https://site.financialmodelingprep.com/")
        return []

    try:
        # Senate trades
        url = f"https://financialmodelingprep.com/api/v4/senate-trading?apikey={FMP_KEY}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Got {len(data)} Senate trades from FMP")

            # House trades
            url2 = f"https://financialmodelingprep.com/api/v4/senate-disclosure?apikey={FMP_KEY}"
            response2 = requests.get(url2, timeout=10)

            if response2.status_code == 200:
                house_data = response2.json()
                print(f"✅ Got {len(house_data)} House trades from FMP")
                return data + house_data

            return data
        else:
            print(f"❌ FMP error: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ FMP failed: {e}")
        return []

def normalize_trade_data(raw_data, source):
    """
    Convert different API formats to our database schema
    """
    normalized = []

    for trade in raw_data:
        try:
            # Different sources have different field names
            if source == "finnhub":
                normalized_trade = {
                    "member_name": trade.get("name", "Unknown"),
                    "trade_date": trade.get("transactionDate"),
                    "disclosure_date": trade.get("filingDate"),
                    "ticker": trade.get("symbol", "").upper(),
                    "trade_type": trade.get("type", "Unknown"),
                    "amount_low": parse_amount(trade.get("amount", "")),
                    "amount_high": parse_amount(trade.get("amount", ""), is_high=True),
                    "party": None,  # Finnhub doesn't provide this
                    "chamber": "Unknown",
                    "company_name": None
                }

            elif source == "house_stock_watcher":
                normalized_trade = {
                    "member_name": trade.get("representative", "Unknown"),
                    "trade_date": trade.get("transaction_date"),
                    "disclosure_date": trade.get("disclosure_date"),
                    "ticker": trade.get("ticker", "").upper(),
                    "trade_type": trade.get("type", "Unknown"),
                    "amount_low": parse_amount(trade.get("amount", "")),
                    "amount_high": parse_amount(trade.get("amount", ""), is_high=True),
                    "party": trade.get("party"),
                    "chamber": "House",
                    "company_name": trade.get("asset_description")
                }

            elif source == "fmp":
                normalized_trade = {
                    "member_name": f"{trade.get('firstName', '')} {trade.get('lastName', '')}".strip(),
                    "trade_date": trade.get("transactionDate"),
                    "disclosure_date": trade.get("disclosureDate"),
                    "ticker": trade.get("ticker", "").upper(),
                    "trade_type": trade.get("type", "Unknown"),
                    "amount_low": trade.get("amount"),
                    "amount_high": trade.get("amount"),
                    "party": None,
                    "chamber": "Senate" if "senate" in source.lower() else "House",
                    "company_name": trade.get("assetDescription")
                }

            normalized.append(normalized_trade)
        except Exception as e:
            print(f"⚠️  Skipping malformed trade: {e}")
            continue

    return normalized

def parse_amount(amount_str, is_high=False):
    """
    Parse amount ranges like "$1,001 - $15,000"
    """
    if not amount_str:
        return None

    try:
        # Remove $ and commas
        amount_str = str(amount_str).replace("$", "").replace(",", "")

        # Check for range
        if "-" in amount_str:
            parts = amount_str.split("-")
            return int(parts[1].strip()) if is_high else int(parts[0].strip())
        else:
            # Single value
            return int(amount_str.strip())
    except:
        return None

def save_to_database(trades):
    """
    Save trades to Supabase
    """
    if not trades:
        print("\n❌ No trades to save!")
        return

    print(f"\n💾 Saving {len(trades)} trades to database...")

    # Clear old test data
    try:
        supabase.table("congressional_trades").delete().neq("id", "").execute()
        print("✅ Cleared old data")
    except Exception as e:
        print(f"⚠️  Error clearing old data: {e}")

    # Insert new data in batches
    batch_size = 100
    success_count = 0

    for i in range(0, len(trades), batch_size):
        batch = trades[i:i + batch_size]
        try:
            supabase.table("congressional_trades").insert(batch).execute()
            success_count += len(batch)
            print(f"✅ Saved batch {i//batch_size + 1} ({len(batch)} trades)")
        except Exception as e:
            print(f"❌ Error saving batch: {e}")

    print(f"\n🎉 Successfully saved {success_count}/{len(trades)} trades!")

def main():
    print("=" * 60)
    print("📊 CONGRESSIONAL TRADING DATA FETCHER")
    print("=" * 60)

    all_trades = []

    # Try all sources
    finnhub_data = fetch_from_finnhub()
    if finnhub_data:
        all_trades.extend(normalize_trade_data(finnhub_data, "finnhub"))

    hsw_data = fetch_from_house_stock_watcher()
    if hsw_data:
        all_trades.extend(normalize_trade_data(hsw_data, "house_stock_watcher"))

    fmp_data = fetch_from_fmp()
    if fmp_data:
        all_trades.extend(normalize_trade_data(fmp_data, "fmp"))

    print("\n" + "=" * 60)
    print(f"📈 TOTAL TRADES COLLECTED: {len(all_trades)}")
    print("=" * 60)

    if all_trades:
        save_to_database(all_trades)

        # Show sample
        print("\n📋 Sample trades:")
        for trade in all_trades[:3]:
            print(f"  • {trade['member_name']}: {trade['ticker']} ({trade['trade_type']})")
    else:
        print("\n❌ No data collected from any source!")
        print("\n💡 Next steps:")
        print("1. Check your internet connection")
        print("2. Verify your Finnhub API key in .env")
        print("3. Consider signing up for FMP free tier: https://site.financialmodelingprep.com/")

if __name__ == "__main__":
    main()
