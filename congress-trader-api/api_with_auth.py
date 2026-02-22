"""
Congressional Trading Intelligence API v2.0
Now with Authentication, Subscription Tiers, and Premium Features!
"""

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Import our authentication middleware
from auth_middleware import (
    get_current_user,
    get_optional_user,
    require_subscription,
    require_feature,
    get_user_limits
)

load_dotenv()

app = FastAPI(
    title="Congressional Trading Intelligence API",
    description="Track congressional stock trades and beat the market",
    version="2.0.0"
)

# Enable CORS for frontend
ALLOWED_ORIGINS = [
    "https://calm-entremet-cf440f.netlify.app",  # current Netlify domain
    "http://localhost:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# =====================================================
# PYDANTIC MODELS (Request/Response schemas)
# =====================================================

class UserPreferencesUpdate(BaseModel):
    """User preference update request"""
    email_alerts_enabled: Optional[bool] = None
    alert_frequency: Optional[str] = None
    watched_politicians: Optional[List[str]] = None
    watched_tickers: Optional[List[str]] = None
    min_trade_amount: Optional[int] = None

class WatchlistAdd(BaseModel):
    """Add politician or ticker to watchlist"""
    type: str  # "politician" or "ticker"
    value: str  # Name or ticker symbol

# =====================================================
# PUBLIC ENDPOINTS (No authentication required)
# =====================================================

@app.get("/")
def home():
    """API health check"""
    return {
        "status": "API is running",
        "version": "2.0.0",
        "features": ["Authentication", "Subscriptions", "Premium Analytics"],
        "endpoints": {
            "public": ["/", "/stats", "/health"],
            "free": ["/trades (delayed)", "/politician/{name}", "/ticker/{ticker}"],
            "insider": ["/trades (realtime)", "/alerts/config", "/analytics/basic"],
            "elite": ["/australian-disclosures", "/analytics/advanced", "/api/v1/*"]
        }
    }

@app.get("/health")
def health_check():
    """Detailed health check with database connection test"""
    try:
        # Test database connection
        result = supabase.table("congressional_trades").select("id").limit(1).execute()
        db_status = "connected" if result.data else "empty"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/stats")
async def get_stats(user: Optional[Dict] = Depends(get_optional_user)):
    """
    Get dashboard statistics
    Free users: Basic stats only
    Paid users: Enhanced stats with real-time data
    """
    # Basic stats for everyone — use count="exact" with head=True to avoid fetching rows
    total_result = supabase.table("congressional_trades").select("id", count="exact").execute()
    total_trades = total_result.count

    # Use SQL via RPC for efficient distinct counts
    try:
        pol_result = supabase.rpc("count_distinct_politicians").execute()
        unique_politicians = pol_result.data or 0
    except Exception:
        pol_result = supabase.table("congressional_trades").select("member_name").execute()
        unique_politicians = len(set(t["member_name"] for t in pol_result.data))

    try:
        tick_result = supabase.rpc("count_distinct_tickers").execute()
        unique_tickers = tick_result.data or 0
    except Exception:
        tick_result = supabase.table("congressional_trades").select("ticker").execute()
        unique_tickers = len(set(t["ticker"] for t in tick_result.data))

    stats = {
        "total_trades": total_trades,
        "unique_politicians": unique_politicians,
        "unique_tickers": unique_tickers,
    }

    # Enhanced stats for paid users
    if user and user["subscription_tier"] in ["insider", "elite"]:
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date().isoformat()
        recent_result = supabase.table("congressional_trades")\
            .select("id", count="exact")\
            .gte("trade_date", thirty_days_ago)\
            .execute()

        stats["recent_trades_30d"] = recent_result.count
        stats["premium_features_unlocked"] = True

    return stats

# =====================================================
# FREE TIER ENDPOINTS (7-day delayed data)
# =====================================================

@app.get("/trades")
async def get_trades(
    limit: int = 100,
    offset: int = 0,
    user: Optional[Dict] = Depends(get_optional_user)
):
    """
    Get congressional trades
    Free: 7-day delayed
    Insider/Elite: Real-time
    """
    # Apply delay for free users
    if not user or user["subscription_tier"] == "free":
        delay_date = (datetime.now() - timedelta(days=7)).date().isoformat()
        # Sort by amount DESC for free tier — surfaces big historical trades (Pelosi $1M+)
        # rather than the most recent tiny trades which are unimpressive
        query = supabase.table("congressional_trades")\
            .select("*")\
            .lte("trade_date", delay_date)\
            .order("amount_low", desc=True, nullsfirst=False)
        delayed = True
    else:
        # Paid users get real-time sorted by date (newest first)
        query = supabase.table("congressional_trades")\
            .select("*")\
            .order("trade_date", desc=True)
        delayed = False

    result = query.limit(limit).range(offset, offset + limit - 1).execute()

    return {
        "trades": result.data,
        "count": len(result.data),
        "delayed": delayed,
        "upgrade_message": "Upgrade to Insider for real-time trades" if delayed else None
    }

@app.get("/politician/{name}")
async def get_politician_profile(name: str):
    """
    Get politician trading profile (public data)
    """
    result = supabase.table("congressional_trades")\
        .select("*")\
        .ilike("member_name", f"%{name}%")\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail=f"No trades found for {name}")

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

@app.get("/politician/{name}/trades")
async def get_politician_trades(name: str):
    """
    Get all trades for a politician by name — flat list format.
    Used by the dashboard search feature.
    """
    result = supabase.table("congressional_trades")\
        .select("*")\
        .ilike("member_name", f"%{name}%")\
        .order("trade_date", desc=True)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail=f"No trades found for {name}")

    return result.data

@app.get("/ticker/{ticker}")
async def get_trades_by_ticker(ticker: str):
    """Get all trades for a specific stock ticker"""
    result = supabase.table("congressional_trades")\
        .select("*")\
        .ilike("ticker", ticker)\
        .order("trade_date", desc=True)\
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail=f"No trades found for {ticker}")

    return {
        "ticker": ticker.upper(),
        "trade_count": len(result.data),
        "trades": result.data
    }

@app.get("/signal-scores")
async def get_signal_scores():
    """
    Return pre-computed signal scores per politician.
    Calculates from trade history: trade count + avg disclosure lag.
    Public endpoint — star ratings shown to all users (detail locked for free tier in UI).
    """
    result = supabase.table("congressional_trades")\
        .select("member_name, trade_date, disclosure_date")\
        .execute()

    # Aggregate per politician
    stats: Dict[str, Any] = {}
    for t in result.data:
        name = t["member_name"]
        if name not in stats:
            stats[name] = {"trade_count": 0, "lags": []}
        stats[name]["trade_count"] += 1

        # Calculate disclosure lag if both dates present
        if t.get("trade_date") and t.get("disclosure_date"):
            try:
                td = datetime.strptime(t["trade_date"], "%Y-%m-%d")
                dd = datetime.strptime(t["disclosure_date"], "%Y-%m-%d")
                lag = (dd - td).days
                if lag >= 0:
                    stats[name]["lags"].append(lag)
            except (ValueError, TypeError):
                pass

    scores = []
    for name, s in stats.items():
        count = s["trade_count"]
        avg_lag = round(sum(s["lags"]) / len(s["lags"])) if s["lags"] else None

        # Score 1-5: more trades + lower lag = higher score
        score = 1
        if count >= 50:  score += 1
        if count >= 100: score += 1
        if avg_lag is not None and avg_lag <= 30: score += 1
        if avg_lag is not None and avg_lag <= 14: score += 1

        scores.append({
            "member_name": name,
            "trade_count": count,
            "avg_disclosure_lag_days": avg_lag,
            "signal_score": min(score, 5)
        })

    return scores

# =====================================================
# AUTHENTICATED ENDPOINTS (Login required)
# =====================================================

@app.get("/account")
async def get_account(user: Dict = Depends(get_current_user)):
    """
    Get current user's account information
    Requires: Authentication
    """
    # Get user preferences
    prefs = supabase.table("user_preferences")\
        .select("*")\
        .eq("user_id", user["id"])\
        .maybe_single()\
        .execute()

    # Get tier limits
    limits = await get_user_limits(user["id"])

    return {
        "user": {
            "email": user["email"],
            "subscription_tier": user["subscription_tier"],
            "subscription_status": user["subscription_status"],
        },
        "preferences": prefs.data if prefs.data else {},
        "tier_limits": limits,
        "upgrade_available": user["subscription_tier"] != "elite"
    }

@app.put("/account/preferences")
async def update_preferences(
    preferences: UserPreferencesUpdate,
    user: Dict = Depends(get_current_user)
):
    """
    Update user notification preferences
    Requires: Authentication
    """
    update_data = preferences.dict(exclude_none=True)

    # Update preferences
    result = supabase.table("user_preferences")\
        .update(update_data)\
        .eq("user_id", user["id"])\
        .execute()

    return {
        "message": "Preferences updated successfully",
        "preferences": result.data[0] if result.data else {}
    }

@app.get("/watchlist")
async def get_watchlist(user: Dict = Depends(get_current_user)):
    """
    Get user's watched politicians and tickers
    Requires: Authentication
    """
    prefs = supabase.table("user_preferences")\
        .select("watched_politicians, watched_tickers")\
        .eq("user_id", user["id"])\
        .maybe_single()\
        .execute()

    data = prefs.data or {}
    return {
        "politicians": data.get("watched_politicians") or [],
        "tickers": data.get("watched_tickers") or []
    }

@app.post("/watchlist/add")
async def add_to_watchlist(
    item: WatchlistAdd,
    user: Dict = Depends(get_current_user)
):
    """
    Add politician or ticker to watchlist
    Requires: Insider tier (limits apply)
    """
    # Get current watchlist
    prefs = supabase.table("user_preferences")\
        .select("*")\
        .eq("user_id", user["id"])\
        .maybe_single()\
        .execute()

    # Check tier limits
    limits = await get_user_limits(user["id"])
    max_politicians = limits["max_watched_politicians"]

    prefs_data = prefs.data or {}
    if item.type == "politician":
        current_list = prefs_data.get("watched_politicians", [])

        # Check limit (unless unlimited)
        if max_politicians != -1 and len(current_list) >= max_politicians:
            raise HTTPException(
                status_code=403,
                detail=f"Watchlist limit reached ({max_politicians}). Upgrade to Elite for unlimited."
            )

        if item.value not in current_list:
            current_list.append(item.value)
            supabase.table("user_preferences")\
                .update({"watched_politicians": current_list})\
                .eq("user_id", user["id"])\
                .execute()

    elif item.type == "ticker":
        current_list = prefs_data.get("watched_tickers", [])
        if item.value.upper() not in current_list:
            current_list.append(item.value.upper())
            supabase.table("user_preferences")\
                .update({"watched_tickers": current_list})\
                .eq("user_id", user["id"])\
                .execute()

    return {"message": f"Added {item.value} to watchlist"}

# =====================================================
# INSIDER TIER ENDPOINTS ($29/month)
# =====================================================

@app.get("/trades/realtime")
async def get_realtime_trades(
    limit: int = 100,
    user: Dict = Depends(require_subscription('insider'))
):
    """
    Get real-time congressional trades (no delay)
    Requires: Insider or Elite subscription
    """
    result = supabase.table("congressional_trades")\
        .select("*")\
        .order("trade_date", desc=True)\
        .limit(limit)\
        .execute()

    return {
        "trades": result.data,
        "count": len(result.data),
        "realtime": True
    }

@app.get("/alerts/history")
async def get_alert_history(
    limit: int = 50,
    user: Dict = Depends(require_subscription('insider'))
):
    """
    Get user's alert delivery history
    Requires: Insider or Elite subscription
    """
    result = supabase.table("alert_history")\
        .select("*")\
        .eq("user_id", user["id"])\
        .order("sent_at", desc=True)\
        .limit(limit)\
        .execute()

    return {
        "alerts": result.data,
        "count": len(result.data)
    }

@app.get("/analytics/trending")
async def get_trending_stocks(
    days: int = 7,
    user: Dict = Depends(require_subscription('insider'))
):
    """
    Get most-traded stocks by politicians
    Requires: Insider or Elite subscription
    """
    cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()

    result = supabase.table("congressional_trades")\
        .select("ticker, trade_type")\
        .gte("trade_date", cutoff_date)\
        .execute()

    # Count by ticker
    ticker_counts = {}
    ticker_sentiment = {}

    for trade in result.data:
        ticker = trade["ticker"]
        if ticker not in ticker_counts:
            ticker_counts[ticker] = 0
            ticker_sentiment[ticker] = {"buys": 0, "sells": 0}

        ticker_counts[ticker] += 1

        if trade["trade_type"] == "Purchase":
            ticker_sentiment[ticker]["buys"] += 1
        else:
            ticker_sentiment[ticker]["sells"] += 1

    # Sort by count
    trending = []
    for ticker, count in sorted(ticker_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        sentiment = ticker_sentiment[ticker]
        net_buys = sentiment["buys"] - sentiment["sells"]

        trending.append({
            "ticker": ticker,
            "trade_count": count,
            "buys": sentiment["buys"],
            "sells": sentiment["sells"],
            "sentiment": "Bullish" if net_buys > 0 else "Bearish" if net_buys < 0 else "Neutral"
        })

    return {
        "period_days": days,
        "trending_stocks": trending
    }

# =====================================================
# ELITE TIER ENDPOINTS ($79/month)
# =====================================================

@app.get("/australian-disclosures")
async def get_australian_disclosures(
    limit: int = 100,
    user: Dict = Depends(require_feature('australian_data'))
):
    """
    Get Australian MP financial disclosures
    Requires: Elite subscription
    """
    result = supabase.table("australian_disclosures")\
        .select("*")\
        .order("disclosure_date", desc=True)\
        .limit(limit)\
        .execute()

    return {
        "disclosures": result.data,
        "count": len(result.data),
        "exclusive": True
    }

@app.get("/analytics/leaderboard")
async def get_politician_leaderboard(
    user: Dict = Depends(require_subscription('elite'))
):
    """
    Get politician trading leaderboard with advanced analytics
    Requires: Elite subscription
    """
    result = supabase.table("congressional_trades")\
        .select("member_name, party, ticker, sector")\
        .limit(5000)\
        .execute()

    # Calculate stats per politician
    politician_stats = {}

    for trade in result.data:
        name = trade["member_name"]
        if name not in politician_stats:
            politician_stats[name] = {
                "name": name,
                "party": trade.get("party"),
                "total_trades": 0,
                "unique_stocks": set(),
                "sectors": set()
            }

        stats = politician_stats[name]
        stats["total_trades"] += 1
        stats["unique_stocks"].add(trade["ticker"])
        if trade.get("sector"):
            stats["sectors"].add(trade["sector"])

    # Format and sort
    leaderboard = []
    for name, stats in politician_stats.items():
        leaderboard.append({
            "politician": name,
            "party": stats["party"],
            "total_trades": stats["total_trades"],
            "unique_stocks": len(stats["unique_stocks"]),
            "sectors_traded": len(stats["sectors"])
        })

    leaderboard.sort(key=lambda x: x["total_trades"], reverse=True)

    return {
        "leaderboard": leaderboard[:50],
        "total_politicians": len(leaderboard)
    }

@app.get("/analytics/sector-rotation")
async def get_sector_rotation(
    days: int = 30,
    user: Dict = Depends(require_subscription('elite'))
):
    """
    Get sector buying/selling trends
    Requires: Elite subscription
    """
    cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()

    result = supabase.table("congressional_trades")\
        .select("sector, trade_type")\
        .gte("trade_date", cutoff_date)\
        .execute()

    # Count by sector
    sector_stats = {}

    for trade in result.data:
        sector = trade.get("sector", "Unknown")
        if sector not in sector_stats:
            sector_stats[sector] = {"buys": 0, "sells": 0}

        if trade["trade_type"] == "Purchase":
            sector_stats[sector]["buys"] += 1
        else:
            sector_stats[sector]["sells"] += 1

    # Format results
    sectors = []
    for sector, stats in sector_stats.items():
        net = stats["buys"] - stats["sells"]
        sectors.append({
            "sector": sector,
            "total_trades": stats["buys"] + stats["sells"],
            "buys": stats["buys"],
            "sells": stats["sells"],
            "net_position": net,
            "sentiment": "Bullish" if net > 5 else "Bearish" if net < -5 else "Neutral"
        })

    sectors.sort(key=lambda x: x["total_trades"], reverse=True)

    return {
        "period_days": days,
        "sectors": sectors
    }

# =====================================================
# API v1 ENDPOINTS (Elite only - for programmatic access)
# =====================================================

@app.get("/api/v1/trades")
async def api_get_trades(
    limit: int = 1000,
    offset: int = 0,
    politician: Optional[str] = None,
    ticker: Optional[str] = None,
    user: Dict = Depends(require_feature('api_access'))
):
    """
    Programmatic API access to trade data
    Requires: Elite subscription
    Rate limit: 1000 requests/hour
    """
    query = supabase.table("congressional_trades").select("*")

    if politician:
        query = query.ilike("member_name", f"%{politician}%")
    if ticker:
        query = query.ilike("ticker", ticker)

    result = query.order("trade_date", desc=True).limit(limit).range(offset, offset + limit - 1).execute()

    return {
        "data": result.data,
        "count": len(result.data),
        "limit": limit,
        "offset": offset
    }

# =====================================================
# ADMIN ENDPOINTS (Future: Admin panel)
# =====================================================

# TODO: Add admin authentication and endpoints for:
# - User management
# - Subscription management
# - Analytics dashboard
# - System health monitoring

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
