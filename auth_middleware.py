"""
Authentication Middleware for Congressional Trading Intelligence
Handles JWT validation, user identification, and subscription tier enforcement
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client
import os
from dotenv import load_dotenv
from functools import wraps
import jwt
from typing import Optional, Dict, Any

load_dotenv()

# Initialize Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# Security scheme for Bearer tokens
security = HTTPBearer()

class AuthenticationError(HTTPException):
    """Custom exception for authentication failures"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)

class AuthorizationError(HTTPException):
    """Custom exception for authorization failures"""
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=detail)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
    """
    Extract and validate JWT token from request headers
    Returns user data if valid, raises HTTPException if invalid

    Usage:
        @app.get("/protected")
        async def protected_route(user=Depends(get_current_user)):
            return {"user_id": user["id"]}
    """
    token = credentials.credentials

    try:
        # Verify JWT with Supabase
        user_response = supabase.auth.get_user(token)

        if not user_response or not user_response.user:
            raise AuthenticationError("Invalid or expired token")

        user = user_response.user

        # Fetch user profile from database
        profile_response = supabase.table("user_profiles")\
            .select("*")\
            .eq("id", user.id)\
            .single()\
            .execute()

        if not profile_response.data:
            # User authenticated but no profile exists - create one
            profile_data = {
                "id": user.id,
                "email": user.email,
                "subscription_tier": "free",
                "subscription_status": "inactive"
            }
            create_response = supabase.table("user_profiles").insert(profile_data).execute()
            profile = create_response.data[0]
        else:
            profile = profile_response.data

        # Update last_login timestamp
        from datetime import datetime, timezone
        supabase.table("user_profiles")\
            .update({"last_login": datetime.now(timezone.utc).isoformat()})\
            .eq("id", user.id)\
            .execute()

        return {
            "id": user.id,
            "email": user.email,
            "subscription_tier": profile["subscription_tier"],
            "subscription_status": profile["subscription_status"],
            "stripe_customer_id": profile.get("stripe_customer_id")
        }

    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")
    except Exception as e:
        print(f"Auth error: {str(e)}")
        raise AuthenticationError("Authentication failed")

async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security, auto_error=False)) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - doesn't require login but returns user if authenticated
    Useful for endpoints that have different behavior for logged-in users

    Usage:
        @app.get("/trades")
        async def get_trades(user=Depends(get_optional_user)):
            if user:
                # Show real-time trades for paid users
                return get_realtime_trades()
            else:
                # Show delayed trades for anonymous users
                return get_delayed_trades()
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except:
        return None

def require_subscription(required_tier: str):
    """
    Decorator to enforce subscription tier requirements

    Tiers (in order of access):
    - free: No paid features
    - insider: Real-time trades, email alerts, basic analytics
    - elite: + Australian data, advanced analytics, API access

    Usage:
        @app.get("/analytics")
        async def analytics(user=Depends(require_subscription('elite'))):
            return {"analytics": "data"}
    """
    tier_hierarchy = {
        "free": 0,
        "insider": 1,
        "elite": 2
    }

    async def subscription_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_tier = user.get("subscription_tier", "free")
        user_status = user.get("subscription_status", "inactive")

        # Check if subscription is active
        if user_status not in ["active", "trialing"] and user_tier != "free":
            # Subscription expired/canceled - downgrade to free
            user_tier = "free"

        # Check tier access
        user_level = tier_hierarchy.get(user_tier, 0)
        required_level = tier_hierarchy.get(required_tier, 999)

        if user_level < required_level:
            raise AuthorizationError(
                f"This feature requires '{required_tier}' subscription. "
                f"Your current tier: '{user_tier}'. Upgrade at https://congresstracker.com.au/pricing"
            )

        return user

    return subscription_checker

def require_feature(feature_name: str):
    """
    Decorator to check if user has access to a specific feature
    Uses the database function user_has_access()

    Features:
    - realtime_trades: Access to live trade data (Insider+)
    - email_alerts: Email notifications (Insider+)
    - australian_data: Australian MP disclosures (Elite only)
    - analytics: Advanced analytics dashboard (Elite only)
    - api_access: API endpoints (Elite only)

    Usage:
        @app.get("/australian-trades")
        async def au_trades(user=Depends(require_feature('australian_data'))):
            return {"trades": "data"}
    """
    async def feature_checker(user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        # Call database function to check access
        result = supabase.rpc(
            'user_has_access',
            {'p_user_id': user['id'], 'p_feature': feature_name}
        ).execute()

        has_access = result.data

        if not has_access:
            # Determine which tier is needed
            tier_map = {
                'realtime_trades': 'insider',
                'email_alerts': 'insider',
                'australian_data': 'elite',
                'analytics': 'elite',
                'api_access': 'elite'
            }
            required_tier = tier_map.get(feature_name, 'elite')

            raise AuthorizationError(
                f"This feature requires '{required_tier}' subscription. "
                f"Upgrade at https://congresstracker.com.au/pricing"
            )

        return user

    return feature_checker

async def get_user_limits(user_id: str) -> Dict[str, Any]:
    """
    Get subscription tier limits for a user

    Returns:
        {
            "max_watched_politicians": 5,  # -1 = unlimited
            "trade_delay_days": 0,
            "email_alerts": true,
            "australian_data": false,
            "analytics": true,
            "api_calls_per_day": 100
        }
    """
    # Get user's tier
    profile = supabase.table("user_profiles")\
        .select("subscription_tier, subscription_status")\
        .eq("id", user_id)\
        .single()\
        .execute()

    tier = profile.data["subscription_tier"]
    status = profile.data["subscription_status"]

    # If subscription inactive, force free tier
    if status not in ["active", "trialing"]:
        tier = "free"

    # Get limits from database function
    limits = supabase.rpc('get_tier_limits', {'p_tier': tier}).execute()

    return limits.data

def get_api_key_user():
    """
    Alternative authentication using API key (for Elite tier users)
    Useful for programmatic access

    Usage:
        @app.get("/api/trades")
        async def api_trades(user=Depends(get_api_key_user)):
            return {"trades": "data"}

    Header format:
        X-API-Key: your_api_key_here
    """
    from fastapi import Header

    async def api_key_checker(x_api_key: str = Header(None)) -> Dict[str, Any]:
        if not x_api_key:
            raise AuthenticationError("API key required. Include 'X-API-Key' header.")

        # API key authentication not yet implemented — column doesn't exist in schema
        # TODO: Add api_key column to user_profiles and implement key generation
        raise AuthenticationError(
            "API key authentication is not yet available. "
            "Please use Bearer token authentication instead."
        )

    return api_key_checker

# =====================================================
# HELPER FUNCTIONS
# =====================================================

async def check_rate_limit(user_id: str, endpoint: str) -> bool:
    """
    Check if user has exceeded rate limits
    Returns True if allowed, False if rate limit exceeded

    Rate limits by tier:
    - Free: 10 requests/hour
    - Insider: 100 requests/hour
    - Elite: 1000 requests/hour
    """
    # TODO: Implement Redis-based rate limiting
    # For now, always return True
    return True

async def log_api_usage(user_id: str, endpoint: str, response_code: int):
    """
    Log API usage for analytics and billing
    """
    # TODO: Implement usage tracking
    pass

def format_auth_error(tier_required: str, current_tier: str) -> Dict[str, Any]:
    """
    Format a helpful error response for unauthorized access
    """
    return {
        "error": "Insufficient permissions",
        "message": f"This feature requires '{tier_required}' subscription",
        "your_tier": current_tier,
        "upgrade_url": "https://congresstracker.com.au/pricing",
        "tier_comparison": {
            "free": {
                "price": "$0",
                "features": ["7-day delayed trades", "Basic search"]
            },
            "insider": {
                "price": "$29 AUD/month",
                "features": ["Real-time US trades", "Email alerts (5 politicians)", "Sector analytics"]
            },
            "elite": {
                "price": "$79 AUD/month",
                "features": ["Everything in Insider", "Australian MP data", "Advanced analytics", "API access"]
            }
        }
    }

# =====================================================
# USAGE EXAMPLES
# =====================================================

"""
# Example 1: Protected route requiring any authentication
from fastapi import FastAPI, Depends
from auth_middleware import get_current_user

@app.get("/account")
async def get_account(user=Depends(get_current_user)):
    return {
        "email": user["email"],
        "tier": user["subscription_tier"]
    }

# Example 2: Require specific subscription tier
from auth_middleware import require_subscription

@app.get("/analytics")
async def analytics_dashboard(user=Depends(require_subscription('elite'))):
    return {"analytics": "data"}

# Example 3: Optional authentication (different behavior for logged-in users)
from auth_middleware import get_optional_user

@app.get("/trades")
async def get_trades(user=Depends(get_optional_user)):
    if user and user["subscription_tier"] in ["insider", "elite"]:
        return {"trades": "realtime_data"}
    else:
        return {"trades": "delayed_data", "upgrade_prompt": True}

# Example 4: Feature-specific access
from auth_middleware import require_feature

@app.get("/australian-disclosures")
async def au_disclosures(user=Depends(require_feature('australian_data'))):
    return {"disclosures": "data"}

# Example 5: API key authentication (Elite users)
from auth_middleware import get_api_key_user

@app.get("/api/v1/trades")
async def api_trades(user=Depends(get_api_key_user)):
    return {"trades": "api_data"}
"""
