#!/usr/bin/env python3
"""
Quiver Quantitative API - Congressional Trading Data Fetcher (FIXED)
Uses correct authentication: 'Token' not 'Bearer'
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
    Correct authentication: Authorization: Token <your_token>
    """

    QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

    if not QUIVER_API_KEY:
        print("❌ No QUIVER_API_KEY found in .env file!")
        return []

    print("🔍 Fetching congressional trades from Quiver API...")

    all_trades = []

    # Try different endpoint patterns based on Quiver's API structure
    endpoints_to_try = [
        "https://api.quiverquant.com/beta/bulk/congresstrading",
        "https://api.quiverquant.com/beta/historical/congresstrading",
        "https://api.quiverquant.com/beta/live/congresstrading",
    ]

    # Correct authentication headers (Token, not Bearer!)
    headers = {
        "Authorization": f"Token {QUIVER_API_KEY}",
        "Accept": "application/json"
    }

    for endpoint in endpoints_to_try:
        try:
            print(f"  Trying: {endpoint}")
            response = requests.get(endpoint, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    print(f"✅ Successfully fetched {len(data)} trades from {endpoint}")
                    all_trades.extend(data)
                    break  # Success! Stop trying other endpoints
                elif isinstance(data, dict) and 'data' in data:
                    trades = data['data']
                    print(f"✅ Successfully fetched {len(trades)} trades from {endpoint}")
                    all_trades.extend(trades)
                    break
                else:
                    print(f"⚠️  Got response but no data: {str(data)[:100]}")
            elif response.status_code == 401:
                print("❌ Invalid API key! Check QUIVER_API_KEY in .env")
            elif response.status_code == 403:
                print("⚠️  Forbidden - might need different endpoint or subscription tier")
            elif response.status_code == 404:
                print(f"⚠️  Endpoint not found, trying next...")
            else:
                print(f"⚠️  Status {response.status_code}: {response.text[:200]}")

        except Exception as e:
            print(f"⚠️  Error: {e}")
            continue

    return all_trades

def normalize_quiver_data(raw_trades):
    """
    Convert Quiver API format to our database schema
    """
    normalized = []

    print(f"🔄 Normalizing {len(raw_trades)} trades...")

    # DEBUG: Print first trade to see actual field names
    if raw_trades:
        print("\n" + "="*80)
        print("🔍 DEBUG: First trade from Quiver API (actual field names):")
        print("="*80)
        print(json.dumps(raw_trades[0], indent=2))
        print("="*80)
        print("\n📋 Available fields:", list(raw_trades[0].keys()))
        print("="*80 + "\n")

    for trade in raw_trades:
        try:
            # FIXED: Using actual Quiver API field names
            member_name = trade.get("Name") or "Unknown"

            ticker = (trade.get("Ticker") or "").upper()

            trade_type = trade.get("Transaction") or "Unknown"

            normalized_trade = {
                "member_name": member_name,
                "trade_date": trade.get("Traded"),  # FIXED: Quiver uses "Traded"
                "disclosure_date": trade.get("Filed"),  # FIXED: Quiver uses "Filed"
                "ticker": ticker,
                "trade_type": trade_type,
                "amount_low": parse_amount(trade.get("Trade_Size_USD"), is_high=False),  # FIXED: "Trade_Size_USD"
                "amount_high": parse_amount(trade.get("Trade_Size_USD"), is_high=True),  # FIXED: "Trade_Size_USD"
                "party": trade.get("Party"),
                "chamber": trade.get("Chamber"),
                "company_name": trade.get("Company") or trade.get("Description")
            }

            # Only add if we have essential data (MUST have trade_date!)
            if not normalized_trade["trade_date"]:
                continue  # Skip trades without date
            if not normalized_trade["ticker"] or normalized_trade["member_name"] == "Unknown":
                continue  # Skip trades without ticker or member

            normalized.append(normalized_trade)

        except Exception as e:
            print(f"⚠️  Skipping trade: {e}")
            continue

    print(f"✅ Normalized {len(normalized)} valid trades")
    return normalized

def parse_amount(amount_str, is_high=False):
    """Parse amount range"""
    if not amount_str:
        return None

    try:
        amount_str = str(amount_str).replace("$", "").replace(",", "")

        if "-" in amount_str:
            parts = amount_str.split("-")
            return int(parts[1].strip()) if is_high else int(parts[0].strip())
        else:
            return int(amount_str.strip())
    except:
        return None

def clear_old_data():
    """Clear existing trades"""
    try:
        supabase.table("congressional_trades").delete().neq("id", "").execute()
        print("✅ Cleared old data")
        return True
    except Exception as e:
        print(f"⚠️  Error clearing data: {e}")
        return False

def save_to_database(trades):
    """Save trades to Supabase"""
    if not trades:
        print("\n❌ No trades to save!")
        return

    print(f"\n💾 Saving {len(trades)} trades to database...")

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
    print("📊 QUIVER API - CONGRESSIONAL TRADING FETCHER")
    print("=" * 60)

    # Fetch from Quiver
    raw_trades = fetch_quiver_congressional_trades()

    if not raw_trades:
        print("\n❌ No data fetched from Quiver API")
        print("\n💡 Troubleshooting:")
        print("1. Verify API key is correct in .env")
        print("2. Check your Quiver subscription is active")
        print("3. Ensure Hobbyist tier includes congressional trading")
        print("4. Try logging into Quiver dashboard to confirm access")
        return

    # Normalize data
    normalized_trades = normalize_quiver_data(raw_trades)

    if normalized_trades:
        print("\n" + "=" * 60)
        print(f"📈 TOTAL TRADES FETCHED: {len(normalized_trades)}")
        print("=" * 60)

        # Clear and save
        clear_old_data()
        saved_count = save_to_database(normalized_trades)

        if saved_count > 0:
            print("\n📋 Sample trades:")
            for trade in normalized_trades[:5]:
                print(f"  • {trade['member_name']}: {trade['ticker']} ({trade['trade_type']})")

            print("\n✅ SUCCESS! Your dashboard now has REAL data!")
            print(f"🌐 View at: https://steady-salamander-7871c8.netlify.app/")
    else:
        print("\n❌ Failed to normalize data")

if __name__ == "__main__":
    main()
