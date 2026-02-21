# Authentication System Setup Guide
## User Authentication & Subscriptions for Congressional Trading Intelligence

---

## 📋 Overview

This guide walks you through implementing the complete authentication and subscription system for your Congressional Trading Intelligence platform.

**What you're building:**
- ✅ User registration and login (email/password + Google OAuth)
- ✅ Subscription tier management (Free, Insider $29, Elite $79)
- ✅ Protected API endpoints based on subscription level
- ✅ User preferences and watchlists
- ✅ Alert history tracking

**Files created:**
1. `auth_schema.sql` - Database schema for users, preferences, alerts
2. `auth_middleware.py` - Python authentication decorators and helpers
3. `api_with_auth.py` - Updated API with protected routes
4. `auth.html` - Beautiful login/signup page

---

## 🚀 Step-by-Step Implementation

### Step 1: Set Up Supabase Authentication

**1.1 Enable Email Authentication**

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project: `congressional-trading-intelligence`
3. Navigate to **Authentication → Providers**
4. Enable **Email** provider (should be enabled by default)
5. Configure email templates:
   - Click **Email Templates**
   - Customize "Confirm signup" email:
     ```
     Subject: Confirm Your Congressional Trading Intelligence Account

     Hi {{ .Email }},

     Welcome to Congressional Trading Intelligence! You're one step away from tracking congressional trades like never before.

     Click here to confirm your email: {{ .ConfirmationURL }}

     Once confirmed, you'll be able to:
     ✓ Track 109,847+ congressional trades
     ✓ Get real-time trade alerts
     ✓ Access exclusive Australian MP data

     Questions? Reply to this email.

     Beat the market by copying Congress!
     The Congressional Trading Intelligence Team
     ```

**1.2 Enable Google OAuth (Optional but Recommended)**

1. In **Authentication → Providers**, click **Google**
2. Click "Enable Google provider"
3. You need to create a Google OAuth app:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project: "Congressional Trading Intelligence"
   - Enable "Google+ API"
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Application type: "Web application"
   - Authorized redirect URIs: Add your Supabase callback URL:
     ```
     https://ujlnghtjnwnjilalazsx.supabase.co/auth/v1/callback
     ```
   - Copy Client ID and Client Secret
4. Paste credentials into Supabase Google provider settings
5. Save

**1.3 Configure Auth Settings**

1. Go to **Authentication → URL Configuration**
2. Set Site URL: `https://your-netlify-domain.netlify.app` (or your actual domain)
3. Add Redirect URLs:
   ```
   https://your-netlify-domain.netlify.app/dashboard.html
   https://your-netlify-domain.netlify.app/auth.html
   http://localhost:3000/dashboard.html (for local testing)
   ```

---

### Step 2: Create Database Tables

**2.1 Run SQL Schema**

1. Open Supabase SQL Editor: **Database → SQL Editor**
2. Click "New query"
3. Copy the entire contents of `auth_schema.sql`
4. Paste into the SQL editor
5. Click "Run" (or Cmd+Enter)
6. Verify success - you should see:
   ```
   Success. No rows returned
   ```

**2.2 Verify Tables Created**

Run this verification query:
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
AND (
    table_name LIKE 'user_%'
    OR table_name LIKE '%_events'
    OR table_name LIKE 'alert_%'
)
ORDER BY table_name;
```

Expected output:
- `alert_history`
- `subscription_events`
- `user_preferences`
- `user_profiles`

**2.3 Test Helper Functions**

Test the tier limits function:
```sql
SELECT get_tier_limits('insider');
```

Expected output:
```json
{
  "max_watched_politicians": 5,
  "trade_delay_days": 0,
  "email_alerts": true,
  "australian_data": false,
  "analytics": true,
  "api_calls_per_day": 100
}
```

---

### Step 3: Deploy Updated Backend

**3.1 Update Railway Deployment**

You need to replace your current `api.py` with the new `api_with_auth.py`.

**Option A: Rename and Deploy**
```bash
cd "/Users/Mathijs/Documents/Claude Projects/Congress tracker/Coding"

# Backup old API
mv api.py api_old.py

# Use new authenticated API
mv api_with_auth.py api.py

# Also copy auth middleware
# (it's already there - auth_middleware.py)

# Commit and push
git add api.py auth_middleware.py
git commit -m "Add user authentication and subscription tiers"
git push origin main
```

**Option B: Gradual Migration**
Keep both APIs running and test the new one first:
```bash
# Deploy new API on different route or subdomain
# Test it thoroughly
# Then switch when ready
```

**3.2 Update Railway Environment Variables**

Your Railway environment already has:
- `SUPABASE_URL` ✅
- `SUPABASE_KEY` ✅

You need to add your **Supabase ANON key** for public access:

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Click **Project Settings** → **API**
3. Copy the `anon` `public` key (not the `service_role` key!)
4. Go to [Railway Dashboard](https://railway.app)
5. Select your project: `congressional-trading-api`
6. Go to **Variables**
7. Add new variable:
   ```
   SUPABASE_ANON_KEY=your_anon_key_here
   ```
8. Redeploy

---

### Step 4: Deploy Frontend Authentication

**4.1 Configure auth.html**

1. Open `auth.html`
2. Find the configuration section (around line 390):
   ```javascript
   const SUPABASE_URL = 'YOUR_SUPABASE_URL_HERE'
   const SUPABASE_ANON_KEY = 'YOUR_SUPABASE_ANON_KEY_HERE'
   ```
3. Replace with your actual values:
   ```javascript
   const SUPABASE_URL = 'https://ujlnghtjnwnjilalazsx.supabase.co'
   const SUPABASE_ANON_KEY = 'your_anon_key_from_supabase_dashboard'
   ```
4. Save the file

**4.2 Deploy to Netlify**

```bash
cd congress-trades-dashboard

# Copy the new auth page
cp ../auth.html ./auth.html

# Commit and push (this should auto-deploy to Netlify)
git add auth.html
git commit -m "Add authentication page"
git push origin main
```

**4.3 Update Your Main Dashboard**

You need to protect the dashboard so only logged-in users can access it.

Add this to the top of your `index.html` (after the `<script>` tag for Supabase):

```html
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
<script>
    // Initialize Supabase
    const supabase = window.supabase.createClient(
        'https://ujlnghtjnwnjilalazsx.supabase.co',
        'YOUR_ANON_KEY_HERE'
    )

    // Check authentication on page load
    async function checkAuth() {
        const { data: { session } } = await supabase.auth.getSession()

        if (!session) {
            // Not logged in - redirect to login page
            window.location.href = '/auth.html'
            return
        }

        // Logged in - fetch user profile and show tier-appropriate features
        const user = session.user
        displayUserInfo(user)
    }

    function displayUserInfo(user) {
        // Add user email to navbar
        const userMenu = document.createElement('div')
        userMenu.innerHTML = `
            <div style="position: fixed; top: 20px; right: 20px; background: white; padding: 10px 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                <span style="margin-right: 10px;">${user.email}</span>
                <button onclick="handleLogout()" style="background: #667eea; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">Log Out</button>
            </div>
        `
        document.body.appendChild(userMenu)
    }

    async function handleLogout() {
        await supabase.auth.signOut()
        window.location.href = '/auth.html'
    }

    // Run auth check
    checkAuth()
</script>
```

---

### Step 5: Test Authentication Flow

**5.1 Test Signup**

1. Visit `https://your-app.netlify.app/auth.html`
2. Click "Sign Up" tab
3. Enter email and password
4. Click "Create Account"
5. Check email for confirmation link
6. Click confirmation link
7. Should redirect to dashboard

**5.2 Test Login**

1. Visit `/auth.html`
2. Enter email and password
3. Click "Log In"
4. Should redirect to dashboard
5. Verify user email shows in top right

**5.3 Test API Authentication**

Test with curl:

```bash
# 1. Sign up and get JWT token from browser DevTools
# In browser console after login, run:
# supabase.auth.getSession().then(d => console.log(d.session.access_token))

# 2. Test protected endpoint
curl -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE" \
  https://your-railway-api.up.railway.app/account

# Expected: User account information
# If not logged in: {"detail": "Authentication failed"}
```

**5.4 Test Subscription Tiers**

```bash
# Try accessing Insider endpoint with free account
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://your-api.up.railway.app/trades/realtime

# Expected (if free tier):
# {
#   "detail": "This feature requires 'insider' subscription. Your current tier: 'free'. Upgrade at ..."
# }
```

---

### Step 6: Create Your First Paid User (Manual)

Since you don't have Stripe integrated yet, manually upgrade your account:

**6.1 Create Test Account**

1. Sign up at `/auth.html` with your personal email
2. Confirm email
3. Log in

**6.2 Manually Upgrade to Elite (via Supabase)**

1. Go to Supabase Dashboard → **Table Editor**
2. Open `user_profiles` table
3. Find your account (by email)
4. Edit the row:
   - `subscription_tier`: Change from `free` to `elite`
   - `subscription_status`: Change from `inactive` to `active`
   - `subscription_start_date`: Set to today's date
5. Save

**6.3 Verify Access**

1. Refresh your dashboard
2. Try accessing Elite features:
   - `/australian-disclosures`
   - `/analytics/leaderboard`
   - `/analytics/sector-rotation`
3. Should work! 🎉

---

## 🔐 Security Best Practices

### Environment Variables

**NEVER commit these to Git:**
- `SUPABASE_URL` - Safe to expose (it's public)
- `SUPABASE_ANON_KEY` - Safe to expose (it's public, has RLS protection)
- `SUPABASE_KEY` (Service Role) - **SECRET! NEVER EXPOSE!** Backend only!

**Where to store:**
- Frontend: `SUPABASE_URL` and `SUPABASE_ANON_KEY` (hardcoded in HTML is OK for now)
- Backend: All three (stored in Railway environment variables)

### Row Level Security (RLS)

The schema automatically enables RLS on all user tables:
- Users can only read/update their own data
- Even with the anon key, users can't access other users' info
- This is why it's safe to expose `SUPABASE_ANON_KEY` in frontend

### JWT Token Security

- Tokens expire after 1 hour by default
- Refresh tokens last 30 days
- Supabase handles refresh automatically
- Never store tokens in localStorage in production (Supabase handles this)

---

## 🎯 Next Steps

Now that authentication is working, you can:

### Week 1 Completed ✅
- [x] User registration and login
- [x] Subscription tier management
- [x] Protected API endpoints
- [x] User preferences table

### Week 2: Stripe Integration
1. Create Stripe account
2. Create products (Insider $29, Elite $79)
3. Implement checkout flow
4. Set up webhooks to update subscription_tier
5. Test payment flow

See `IMPLEMENTATION_ROADMAP.md` for full details.

---

## 🐛 Troubleshooting

### "Invalid API key" error
- Check that you're using the `anon` key, not `service_role` key
- Verify the key is correctly copied (no extra spaces)

### "Not authenticated" even after login
- Check browser console for errors
- Verify JWT token exists: `supabase.auth.getSession()`
- Check that API URL is correct (Railway URL)
- Verify CORS is enabled in API

### User profile not created after signup
- Check Supabase logs: **Authentication → Logs**
- Verify `auth_schema.sql` was run successfully
- Check trigger: `on_user_profile_created` exists

### Google OAuth not working
- Verify redirect URL matches exactly (including https://)
- Check Google Cloud Console for errors
- Ensure Google+ API is enabled

### Redirect after login goes to 404
- Update `emailRedirectTo` in `auth.html`
- Add redirect URL to Supabase **Auth → URL Configuration**

---

## 📊 Monitoring & Analytics

### Check Auth Events

```sql
-- View all signups in last 7 days
SELECT
    created_at,
    email,
    confirmed_at,
    last_sign_in_at
FROM auth.users
WHERE created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

### Check Subscription Distribution

```sql
-- See how many users in each tier
SELECT
    subscription_tier,
    COUNT(*) as user_count
FROM user_profiles
GROUP BY subscription_tier
ORDER BY user_count DESC;
```

### Monitor Alert Delivery

```sql
-- Check alert success rate
SELECT
    alert_type,
    delivery_status,
    COUNT(*) as count
FROM alert_history
WHERE sent_at >= NOW() - INTERVAL '7 days'
GROUP BY alert_type, delivery_status;
```

---

## ✅ Verification Checklist

Before moving to Week 2 (Stripe), verify:

- [ ] Users can sign up with email/password
- [ ] Confirmation email is sent
- [ ] Users can log in after confirming
- [ ] Dashboard shows user email in top right
- [ ] Logout works and redirects to login
- [ ] Google OAuth works (if enabled)
- [ ] Free users see "Upgrade" messages on premium endpoints
- [ ] Manually upgraded Elite user can access all endpoints
- [ ] Database has `user_profiles`, `user_preferences`, `alert_history` tables
- [ ] RLS policies are active (test by trying to access other users' data)
- [ ] JWT tokens are validated correctly
- [ ] 401 errors for invalid/missing tokens
- [ ] 403 errors for insufficient permissions

---

## 🎉 Success!

You now have a fully functional authentication system!

**What you can do now:**
1. Accept user registrations
2. Protect premium features
3. Track user preferences
4. Ready to integrate payments (Week 2)

**Current capabilities:**
- ✅ 3 subscription tiers (Free, Insider, Elite)
- ✅ Email/password + Google OAuth
- ✅ Protected API endpoints
- ✅ User watchlists (up to 5 politicians for Insider)
- ✅ Alert preferences
- ✅ Subscription event tracking

**Next milestone:** Add Stripe to start collecting payments! 💰

---

*Questions? Issues? Check the troubleshooting section or review the code comments in `auth_middleware.py` for detailed examples.*
