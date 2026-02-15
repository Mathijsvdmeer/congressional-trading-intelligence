#!/usr/bin/env python3
"""
Debug script to see actual Quiver API response structure
"""

import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

QUIVER_API_KEY = os.getenv("QUIVER_API_KEY")

headers = {
    "Authorization": f"Token {QUIVER_API_KEY}",
    "Accept": "application/json"
}

endpoint = "https://api.quiverquant.com/beta/bulk/congresstrading"

print("🔍 Fetching sample data from Quiver API...")
response = requests.get(endpoint, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()

    if isinstance(data, list) and len(data) > 0:
        print(f"\n✅ Got {len(data)} trades")
        print("\n" + "="*80)
        print("FIRST TRADE OBJECT (showing actual field names):")
        print("="*80)
        print(json.dumps(data[0], indent=2))

        print("\n" + "="*80)
        print("FIELD NAMES IN FIRST TRADE:")
        print("="*80)
        for key in data[0].keys():
            print(f"  • {key}: {data[0][key]}")
    else:
        print("⚠️ No data in response")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
