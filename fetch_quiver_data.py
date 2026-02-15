#!/usr/bin/env python3
"""
Quiver Quantitative API - Congressional Trading Data Fetcher
Fetches real congressional trading data using Quiver API
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

def fetch_quiver_congressional_trades():
    """
    Fetch congressional trading data from Quiver API
    API Docs: https://api.quiverquant.com/docs/
    """

    QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

    if not QUIVER_API_KEY:
        print("❌ No QUIVER_API_KEY found in .env file!")
        print("\n📝 To get your API key:")
        print("1. Go to: https://www.quiverquant.com/")
        print("2. Sign up / Log in")
        print("3. Go to: https://www.quiverquant.com/congresstrading/")
        print("4. Click on your profile → API")
        print("5. Copy your API key")
        print("6. Add to .env: QUIVER_API_KEY=your_key_here")
        return []

    print("🔍 Fetching congressional trades from Quiver API...")

    try:
        # Quiver API endpoint for congressional trading
        # Method 1: Direct API call
        url = "https://api.quiverquant.com/beta/historical/congresstrading"

        headers = {
            "Authorization": f"Bearer {QUIVER_API_KEY}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully fetched {len(data)} trades from Quiver!")
            return data
        elif response.status_code == 401:
            print("❌ Invalid API key! Please check your QUIVER_API_KEY in .env")
            return []
        elif response.status_code == 403:
            print("❌ Access forbidden. Your API key might not have access to congressional trading data.")
            print("💡 Try upgrading your Quiver subscription or contact support.")
            return []
        else:
            print(f"❌ Quiver API error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return []

    except Exception as e:
        print(f"❌ Error fetching from Quiver API: {e}")
        return []

def normalize_quiver_data(raw_trades):
    """
    Convert Quiver API format to our database schema
    """
    normalized = []

    print("🔄 Normalizing data...")

    for trade in raw_trades:
        try:
            # Quiver API typical fields (adjust based on actual response)
            normalized_trade = {
                "member_name": trade.get("Representative", trade.get("Senator", "Unknown")),
                "trade_date": trade.get("TransactionDate"),
                "disclosure_date": trade.get("ReportDate"),
                "ticker": trade.get("Ticker", "").upper(),
                "trade_type": trade.get("Transaction", "Unknown"),
                "amount_low": parse_quiver_amount(trade.get("Amount", ""), is_high=False),
                "amount_high": parse_quiver_amount(trade.get("Amount", ""), is_high=True),
                "party": trade.get("Party"),
                "chamber": trade.get("House", "House") if "Representative" in str(trade) else "Senate",
                "company_name": trade.get("Company")
            }

            # Only add if we have essential data
            if normalized_trade["ticker"] and normalized_trade["trade_date"]:
                normalized.append(normalized_trade)

        except Exception as e:
            print(f"⚠️  Skipping malformed trade: {e}")
            continue

    print(f"✅ Normalized {len(normalized)} valid trades")
    return normalized

def parse_quiver_amount(amount_str, is_high=False):
    """
    Parse Quiver amount format
    Examples: "$1,001 - $15,000" or "1001-15000"
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

def clear_old_data():
    """Clear existing trades from database"""
    try:
        result = supabase.table("congressional_trades").delete().neq("id", "").execute()
        print("✅ Cleared old data from database")
        return True
    except Exception as e:
        print(f"⚠️  Error clearing old data: {e}")
        return False

def save_to_database(trades):
    """
    Save trades to Supabase database
    """
    if not trades:
        print("\n❌ No trades to save!")
        return

    print(f"\n💾 Saving {len(trades)} trades to database...")

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
    return success_count

def main():
    print("=" * 60)
    print("📊 QUIVER QUANTITATIVE - CONGRESSIONAL TRADING FETCHER")
    print("=" * 60)

    # Fetch from Quiver
    raw_trades = fetch_quiver_congressional_trades()

    if not raw_trades:
        print("\n❌ No data fetched from Quiver API")
        print("\n💡 Make sure you:")
        print("1. Have a Quiver API subscription")
        print("2. Added your API key to .env file")
        print("3. Your subscription includes congressional trading data")
        return

    # Normalize data
    normalized_trades = normalize_quiver_data(raw_trades)

    if normalized_trades:
        print("\n" + "=" * 60)
        print(f"📈 TOTAL TRADES FETCHED: {len(normalized_trades)}")
        print("=" * 60)

        # Clear old data and save new
        clear_old_data()
        saved_count = save_to_database(normalized_trades)

        if saved_count > 0:
            # Show sample
            print("\n📋 Sample trades:")
            for trade in normalized_trades[:5]:
                print(f"  • {trade['member_name']}: {trade['ticker']} ({trade['trade_type']}) on {trade['trade_date']}")

            print("\n✅ SUCCESS! Your dashboard now has REAL data!")
            print(f"🌐 View it at: https://steady-salamander-7871c8.netlify.app/")
    else:
        print("\n❌ Failed to normalize data")

if __name__ == "__main__":
    main()
