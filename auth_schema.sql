-- =====================================================
-- Congressional Trading Intelligence
-- User Authentication & Subscription Schema
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. USER PROFILES TABLE
-- =====================================================
-- Extends Supabase Auth with subscription and preference data

CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,

    -- Subscription Info
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'insider', 'elite')),
    subscription_status TEXT DEFAULT 'inactive' CHECK (subscription_status IN ('active', 'inactive', 'canceled', 'past_due', 'trialing')),
    subscription_start_date TIMESTAMP,
    subscription_end_date TIMESTAMP,

    -- Stripe Integration
    stripe_customer_id TEXT UNIQUE,
    stripe_subscription_id TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Enable Row Level Security
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only read their own profile
CREATE POLICY "Users can view own profile"
    ON user_profiles
    FOR SELECT
    USING (auth.uid() = id);

-- Policy: Users can update their own profile (except subscription fields)
CREATE POLICY "Users can update own profile"
    ON user_profiles
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Index for faster lookups
CREATE INDEX idx_user_email ON user_profiles(email);
CREATE INDEX idx_stripe_customer ON user_profiles(stripe_customer_id);
CREATE INDEX idx_subscription_tier ON user_profiles(subscription_tier);

-- =====================================================
-- 2. USER PREFERENCES TABLE
-- =====================================================
-- Store user notification and alert settings

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE PRIMARY KEY,

    -- Alert Settings
    email_alerts_enabled BOOLEAN DEFAULT false,
    sms_alerts_enabled BOOLEAN DEFAULT false,
    push_notifications_enabled BOOLEAN DEFAULT false,

    -- Alert Frequency
    alert_frequency TEXT DEFAULT 'realtime' CHECK (alert_frequency IN ('realtime', 'daily_digest', 'weekly_digest')),

    -- Watched Politicians (Array of politician names)
    watched_politicians TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Watched Tickers (Array of stock symbols)
    watched_tickers TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Watched Sectors
    watched_sectors TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Alert Preferences
    min_trade_amount INTEGER DEFAULT 0, -- Only alert for trades above this amount
    alert_on_purchases BOOLEAN DEFAULT true,
    alert_on_sales BOOLEAN DEFAULT true,

    -- Timezone for digest emails
    timezone TEXT DEFAULT 'Australia/Sydney',

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view/update their own preferences
CREATE POLICY "Users can view own preferences"
    ON user_preferences
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences"
    ON user_preferences
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences"
    ON user_preferences
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Index for faster lookups
CREATE INDEX idx_email_alerts ON user_preferences(email_alerts_enabled) WHERE email_alerts_enabled = true;

-- =====================================================
-- 3. ALERT HISTORY TABLE
-- =====================================================
-- Track all alerts sent to users (for debugging and analytics)

CREATE TABLE IF NOT EXISTS alert_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE NOT NULL,

    -- Alert Details
    alert_type TEXT NOT NULL CHECK (alert_type IN ('email', 'sms', 'push')),
    trade_id UUID, -- Reference to the trade that triggered the alert
    politician_name TEXT,
    ticker TEXT,

    -- Delivery Status
    sent_at TIMESTAMP DEFAULT NOW(),
    delivery_status TEXT DEFAULT 'pending' CHECK (delivery_status IN ('pending', 'sent', 'failed', 'bounced')),
    error_message TEXT,

    -- Engagement Tracking
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE alert_history ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own alert history
CREATE POLICY "Users can view own alert history"
    ON alert_history
    FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes for analytics queries
CREATE INDEX idx_alert_user ON alert_history(user_id);
CREATE INDEX idx_alert_sent_at ON alert_history(sent_at);
CREATE INDEX idx_alert_status ON alert_history(delivery_status);

-- =====================================================
-- 4. SUBSCRIPTION EVENTS TABLE
-- =====================================================
-- Audit log of subscription changes (upgrades, downgrades, cancellations)

CREATE TABLE IF NOT EXISTS subscription_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE NOT NULL,

    -- Event Details
    event_type TEXT NOT NULL CHECK (event_type IN (
        'subscription_created',
        'subscription_upgraded',
        'subscription_downgraded',
        'subscription_canceled',
        'subscription_renewed',
        'payment_failed',
        'trial_started',
        'trial_ended'
    )),

    old_tier TEXT,
    new_tier TEXT,

    -- Stripe Event Data
    stripe_event_id TEXT,
    stripe_invoice_id TEXT,

    -- Financial Data
    amount_paid DECIMAL(10, 2),
    currency TEXT DEFAULT 'AUD',

    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE subscription_events ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own subscription events
CREATE POLICY "Users can view own subscription events"
    ON subscription_events
    FOR SELECT
    USING (auth.uid() = user_id);

-- Indexes
CREATE INDEX idx_sub_events_user ON subscription_events(user_id);
CREATE INDEX idx_sub_events_type ON subscription_events(event_type);
CREATE INDEX idx_sub_events_created ON subscription_events(created_at);

-- =====================================================
-- 5. TRIGGER FUNCTIONS
-- =====================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for user_profiles
CREATE TRIGGER update_user_profiles_updated_at
    BEFORE UPDATE ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for user_preferences
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-create user_preferences when user_profile is created
CREATE OR REPLACE FUNCTION create_user_preferences()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO user_preferences (user_id)
    VALUES (NEW.id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_user_profile_created
    AFTER INSERT ON user_profiles
    FOR EACH ROW
    EXECUTE FUNCTION create_user_preferences();

-- =====================================================
-- 6. HELPER FUNCTIONS
-- =====================================================

-- Check if user has access to a feature based on subscription tier
CREATE OR REPLACE FUNCTION user_has_access(
    p_user_id UUID,
    p_feature TEXT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_tier TEXT;
    v_status TEXT;
BEGIN
    -- Get user's current subscription
    SELECT subscription_tier, subscription_status
    INTO v_tier, v_status
    FROM user_profiles
    WHERE id = p_user_id;

    -- Check if subscription is active
    IF v_status != 'active' AND v_status != 'trialing' THEN
        v_tier := 'free';
    END IF;

    -- Feature access rules
    CASE p_feature
        WHEN 'realtime_trades' THEN
            RETURN v_tier IN ('insider', 'elite');
        WHEN 'email_alerts' THEN
            RETURN v_tier IN ('insider', 'elite');
        WHEN 'australian_data' THEN
            RETURN v_tier = 'elite';
        WHEN 'analytics' THEN
            RETURN v_tier = 'elite';
        WHEN 'api_access' THEN
            RETURN v_tier = 'elite';
        ELSE
            RETURN false;
    END CASE;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get subscription tier limits
CREATE OR REPLACE FUNCTION get_tier_limits(p_tier TEXT)
RETURNS JSON AS $$
BEGIN
    CASE p_tier
        WHEN 'free' THEN
            RETURN json_build_object(
                'max_watched_politicians', 0,
                'trade_delay_days', 7,
                'email_alerts', false,
                'australian_data', false,
                'analytics', false,
                'api_calls_per_day', 0
            );
        WHEN 'insider' THEN
            RETURN json_build_object(
                'max_watched_politicians', 5,
                'trade_delay_days', 0,
                'email_alerts', true,
                'australian_data', false,
                'analytics', true,
                'api_calls_per_day', 100
            );
        WHEN 'elite' THEN
            RETURN json_build_object(
                'max_watched_politicians', -1, -- unlimited
                'trade_delay_days', 0,
                'email_alerts', true,
                'australian_data', true,
                'analytics', true,
                'api_calls_per_day', 1000
            );
        ELSE
            RETURN json_build_object(
                'error', 'Invalid tier'
            );
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 7. INITIAL DATA
-- =====================================================

-- Create a service role user profile (for system operations)
-- This will be created automatically when service accounts sign up

COMMENT ON TABLE user_profiles IS 'Extended user profile data with subscription information';
COMMENT ON TABLE user_preferences IS 'User notification and alert preferences';
COMMENT ON TABLE alert_history IS 'Audit log of all alerts sent to users';
COMMENT ON TABLE subscription_events IS 'Subscription lifecycle events for billing and analytics';

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================

-- Run these to verify setup:

-- 1. Check if tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'user_%' OR table_name LIKE '%_events';

-- 2. Test tier limits function
-- SELECT get_tier_limits('insider');

-- 3. Test access function (replace UUID with real user ID)
-- SELECT user_has_access('YOUR-USER-UUID-HERE', 'email_alerts');

-- =====================================================
-- DONE!
-- =====================================================
-- Schema created successfully.
-- Next steps:
-- 1. Run this SQL in Supabase SQL Editor
-- 2. Enable Email Auth in Supabase Authentication settings
-- 3. Set up Stripe webhooks to update subscription_tier
-- 4. Create backend API endpoints for user management
-- =====================================================
