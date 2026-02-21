# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**What we're building:** A congressional trade tracking platform targeting Australian retail investors. Monetized via subscription tiers (Free / Insider A$19.99/mo / Elite A$49.99/mo). Goal: A$4k MRR.

**Competitors:** Wolf of Washington, Quiver Quantitative. We differentiate via AUD pricing, Australian market focus, and impact scoring.

**Current status (Feb 2026):**
- Working data pipeline (109,847+ trades in Supabase, refreshed daily)
- Frontend live on Netlify, unauthenticated legacy API on Railway
- `api_with_auth.py` built but NOT deployed — subscription enforcement is not live
- No paying users yet

**Live URLs:**
- Frontend: `https://calm-entremet-cf440f.netlify.app`
- Railway API (legacy, unauthenticated): `https://congress-trader-api-production.up.railway.app`
- GitHub repo: `https://github.com/Mathijsvdmeer/congressional-trading-intelligence`
- Supabase dashboard: `https://ujlnghtjnwnjilalazsx.supabase.co`

**Biggest launch blockers:**
1. `api_with_auth.py` not deployed — no paywall, no revenue possible
2. Known bugs in `auth_middleware.py` (see below)
3. No Stripe integration

## Operating Mode: Dual Role

Claude operates in **DUAL MODE** on this project:
1. **Implementation Engineer** — builds features
2. **Critical Product Advisor** — challenges decisions, focuses on revenue impact

After every task, Claude generates a **Critical Review** using the framework in `@CRITICAL_REVIEW_FRAMEWORK.md`.

Core principles:
- Prioritize shipping over perfection
- Challenge scope creep — only build what drives conversions
- Be brutally honest about ROI and launch readiness
- Compare every decision against Wolf of Washington and Quiver Quantitative
- Build for 100 users first, not 100,000

## Repository Layout

The repo root is the project root. Key directories:
- `congress-trades-dashboard/` — Frontend (vanilla HTML/JS), hosted on Netlify
- `congress-trader-api/` — Legacy simpler API
- `.github/workflows/` — GitHub Actions (daily data refresh)

Top-level Python files are the active backend: `fetch_quiver_fixed.py` (data pipeline), `api_with_auth.py` (main API), `auth_middleware.py` (auth helpers).

## Running Things

```bash
# Fetch congressional trades from Quiver API into Supabase
python fetch_quiver_fixed.py

# Run the legacy scraper (supports --source hsw|fin and --dry-run)
python scraper.py

# Start the authenticated API locally (from congress-trader-api/)
cd congress-trader-api && uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Trigger the GitHub Actions data refresh workflow manually
gh workflow run 234503833
```

There are no automated tests in this project.

## Architecture

**Data flow:**
1. GitHub Actions runs `fetch_quiver_fixed.py` daily at 6 AM EST
2. Script fetches from Quiver Quantitative API (auth: `Authorization: Token <key>`, NOT Bearer) and normalizes fields
3. Normalized trades are batch-upserted into Supabase table `congressional_trades`
4. Frontend (`congress-trades-dashboard/index.html`) reads directly from Supabase or via the API
5. `api_with_auth.py` (FastAPI, deployed on Railway) serves authenticated/tiered endpoints

**Quiver API field mapping** (critical — these differ from what you might expect):
- `Name` → `member_name`
- `Traded` → `trade_date`
- `Filed` → `disclosure_date`
- `Trade_Size_USD` → `amount_low` / `amount_high` (parsed via `parse_amount()` using `int(float(...))`)
- `Transaction` → `trade_type`

**Subscription tiers** (enforced in `auth_middleware.py`, defined in `auth_schema.sql`):
- Free (0): 7-day delayed trades, no watchlists
- Insider (1): Real-time trades, up to 5 watched politicians, email alerts
- Elite (2): All features, Australian data, programmatic API access

**Authentication:** Supabase Auth issues JWTs. API validates them via `get_current_user()` in `auth_middleware.py`. Subscription tier is stored in `user_profiles.subscription_tier`. Rate limiting is stubbed (always returns `True`).

**Deployment gap:** The frontend currently calls the legacy unauthenticated `congress-trader-api/api.py` on Railway. `api_with_auth.py` is not yet deployed — subscription enforcement does not run in production until this is swapped.

**Known bugs in `auth_middleware.py`:**
- `last_login` is stored as the string `"NOW()"` instead of a real timestamp (line 79)
- API key auth queries an `api_key` column that doesn't exist in `auth_schema.sql` — will crash if triggered

## Environment Variables

Stored in `congress-trader-api/.env` and as GitHub Secrets:
- `SUPABASE_URL`, `SUPABASE_KEY` — Supabase project credentials
- `QUIVER_API_KEY` — Quiver Quantitative API token
- `FINNHUB_API_KEY` — Finnhub stock data API key

## Database

Supabase (PostgreSQL) at `ujlnghtjnwnjilalazsx.supabase.co`. Schema defined in `auth_schema.sql`. Row-Level Security (RLS) is enabled — users only see their own rows in `user_profiles`, `user_preferences`, and `alert_history`. The `congressional_trades` table is publicly readable.

Key helper functions in the DB: `user_has_access(feature_name)`, `get_tier_limits()`.
