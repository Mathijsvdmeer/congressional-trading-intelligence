from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@app.get("/")
def home():
    return {"status": "API is running"}

@app.get("/stats")
def get_stats():
    """
    Get dashboard statistics efficiently without fetching all trade data
    """
    from datetime import datetime, timedelta

    # Get total count
    total_result = supabase.table("congressional_trades").select("id", count="exact").execute()
    total_trades = total_result.count

    # Get unique politicians
    politicians_result = supabase.table("congressional_trades").select("member_name").execute()
    unique_politicians = len(set([t["member_name"] for t in politicians_result.data]))

    # Get unique tickers
    tickers_result = supabase.table("congressional_trades").select("ticker").execute()
    unique_tickers = len(set([t["ticker"] for t in tickers_result.data]))

    # Get recent trades count (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()
    recent_result = supabase.table("congressional_trades").select("id", count="exact").gte("trade_date", thirty_days_ago).execute()
    recent_trades = recent_result.count

    return {
        "total_trades": total_trades,
        "unique_politicians": unique_politicians,
        "unique_tickers": unique_tickers,
        "recent_trades": recent_trades
    }

@app.get("/trades")
def get_trades(limit: int = 1000):
    """
    Get recent trades (default 1000 for performance)
    Use /stats endpoint for statistics
    """
    query = supabase.table("congressional_trades").select("*").order("trade_date", desc=True).limit(limit)
    result = query.execute()
    return result.data

@app.get("/top-traders")
def top_traders():
    result = supabase.table("congressional_trades").select("*").execute()
    
    traders = {}
    for trade in result.data:
        name = trade["member_name"]
        if name not in traders:
            traders[name] = 0
        traders[name] += 1
    
    sorted_traders = sorted(traders.items(), key=lambda x: x[1], reverse=True)
    
    return [{"name": name, "trade_count": count} for name, count in sorted_traders[:10]]

@app.get("/trades/ticker/{ticker}")
def get_trades_by_ticker(ticker: str):
    result = supabase.table("congressional_trades").select("*").ilike("ticker", ticker).execute()
    
    if not result.data:
        return {"message": f"No trades found for {ticker}", "trades": []}
    
    return {
        "ticker": ticker.upper(),
        "trade_count": len(result.data),
        "trades": result.data
    }

@app.get("/trades/recent")
def get_recent_trades(days: int = 30):
    from datetime import datetime, timedelta

    cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
    result = supabase.table("congressional_trades").select("*").gte("trade_date", cutoff_date).order("trade_date", desc=True).execute()
    
    return {
        "period_days": days,
        "trade_count": len(result.data),
        "trades": result.data
    }

@app.get("/signal-scores")
def get_all_signal_scores():
    """
    Historical pattern analysis scores for all politicians.
    Score (1-5) based on trade volume and disclosure timing patterns.
    Factual information only — not financial advice.
    """
    result = supabase.table("politician_signal_scores")\
        .select("*")\
        .order("trade_count", desc=True)\
        .execute()
    return result.data

@app.get("/politician/{name}/signal-score")
def get_politician_signal_score(name: str):
    """
    Historical pattern analysis score for a specific politician.
    Factual information only — not financial advice.
    """
    result = supabase.table("politician_signal_scores")\
        .select("*")\
        .ilike("member_name", f"%{name}%")\
        .execute()
    if not result.data:
        return {"error": f"No pattern data found for {name}"}
    row = result.data[0]
    return {
        **row,
        "score_explanation": {
            "signal_score": row["signal_score"],
            "basis": "Historical pattern analysis based on trade volume and disclosure timing",
            "trade_count": row["trade_count"],
            "avg_disclosure_lag_days": row["avg_disclosure_lag_days"],
            "disclaimer": "Factual information only. Not financial advice."
        }
    }

@app.get("/politician/{name}/trades")
def get_politician_trades(name: str, limit: int = 500):
    """Return all trades for a politician — used for profile charts."""
    result = supabase.table("congressional_trades")\
        .select("*")\
        .ilike("member_name", f"%{name}%")\
        .order("trade_date", desc=True)\
        .limit(limit)\
        .execute()
    return result.data

@app.get("/politician/{name}")
def get_politician_profile(name: str):
    result = supabase.table("congressional_trades").select("*").ilike("member_name", f"%{name}%").execute()
    
    if not result.data:
        return {"message": f"No trades found for {name}"}
    
    trades = result.data
    tickers = list(set([t["ticker"] for t in trades]))
    purchases = len([t for t in trades if t["trade_type"] == "Purchase"])
    sales = len([t for t in trades if t["trade_type"] == "Sale"])
    
    return {
        "politician": trades[0]["member_name"],
        "party": trades[0].get("party"),
        "chamber": trades[0].get("chamber"),
        "state": trades[0].get("state"),
        "total_trades": len(trades),
        "purchases": purchases,
        "sales": sales,
        "unique_tickers": len(tickers),
        "tickers": sorted(tickers),
        "recent_trades": trades[:10]
    }
