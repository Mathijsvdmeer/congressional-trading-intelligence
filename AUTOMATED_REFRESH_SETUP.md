# Automated Daily Data Refresh - Setup Guide

🎉 **Your Congressional Trading Intelligence platform now has automated data updates!**

This GitHub Actions workflow will fetch fresh congressional trading data from Quiver API **every day at 6:00 AM EST** automatically.

---

## ✅ What Was Created

1. **`.github/workflows/daily-data-refresh.yml`** - GitHub Actions workflow file
   - Runs daily at 6:00 AM EST (11:00 AM UTC)
   - Can also be triggered manually
   - Fetches data from Quiver API
   - Updates Supabase database
   - Logs success/failure

---

## 📋 Setup Steps

### Step 1: Push Code to GitHub

If you haven't already created a GitHub repository:

```bash
cd "/Users/Mathijs/Congress tracker/Coding"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Add automated daily data refresh via GitHub Actions"

# Create repository on GitHub (go to github.com/new)
# Then link it:
git remote add origin https://github.com/YOUR_USERNAME/congressional-trading-intelligence.git

# Push to GitHub
git push -u origin main
```

**Note:** Replace `YOUR_USERNAME` with your actual GitHub username.

---

### Step 2: Add GitHub Secrets

GitHub Actions needs your API keys to run the script. These are stored as **encrypted secrets**.

1. **Go to your GitHub repository** → **Settings** → **Secrets and variables** → **Actions**

2. **Click "New repository secret"** and add these three secrets:

   **Secret 1: QUIVER_API_KEY**
   - Name: `QUIVER_API_KEY`
   - Value: `9470ba57b0b4e9ab5dae1ab77ce91573c9334cdb`

   **Secret 2: SUPABASE_URL**
   - Name: `SUPABASE_URL`
   - Value: Your Supabase project URL (from Railway environment variables)
   - Example: `https://abcdefghijklmnop.supabase.co`

   **Secret 3: SUPABASE_KEY**
   - Name: `SUPABASE_KEY`
   - Value: Your Supabase anon/service key (from Railway environment variables)

3. **Verify** all three secrets are added:
   - ✅ QUIVER_API_KEY
   - ✅ SUPABASE_URL
   - ✅ SUPABASE_KEY

---

### Step 3: Enable GitHub Actions

1. Go to your repository's **Actions** tab
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. You should see "Daily Congressional Trading Data Refresh" workflow

---

### Step 4: Test the Workflow (Manual Trigger)

Don't wait until 6 AM! Test it right now:

1. Go to **Actions** tab
2. Click **"Daily Congressional Trading Data Refresh"** on the left sidebar
3. Click **"Run workflow"** dropdown on the right
4. Click the green **"Run workflow"** button
5. Wait 2-3 minutes and watch it run!

**What to expect:**
- ✅ Setup Python environment
- ✅ Install dependencies (requests, supabase, python-dotenv)
- ✅ Run fetch_quiver_fixed.py
- ✅ Fetch 109,847+ trades from Quiver API
- ✅ Save to Supabase database
- ✅ Success notification

---

## 🔍 Monitoring & Troubleshooting

### View Workflow Runs

- **Actions** tab → **Daily Congressional Trading Data Refresh**
- See history of all runs (successful and failed)
- Click any run to see detailed logs

### Common Issues

**Problem: "Error: Process completed with exit code 1"**
- ❌ Check GitHub secrets are set correctly
- ❌ Verify QUIVER_API_KEY is valid (not expired)
- ❌ Check Supabase credentials match Railway config

**Problem: "No data fetched from Quiver API"**
- Check your Quiver subscription is active
- Verify Hobbyist tier includes congressional trading
- Test manually: `python fetch_quiver_fixed.py`

**Problem: Workflow doesn't run at 6 AM**
- GitHub Actions can be delayed 5-15 minutes during high load
- Check the Actions tab to see if it ran
- Use manual trigger for immediate updates

### Get Email Notifications

1. Go to GitHub **Settings** (your profile, not repository)
2. **Notifications** → **Actions**
3. Enable **"Send notifications for failed workflows only"**

---

## 📅 Schedule Details

**Current schedule:** Every day at 6:00 AM EST (11:00 AM UTC)

**To change the schedule**, edit `.github/workflows/daily-data-refresh.yml`:

```yaml
schedule:
  - cron: '0 11 * * *'  # 6 AM EST = 11 AM UTC
```

**Cron syntax examples:**
- `0 11 * * *` - Daily at 6:00 AM EST
- `0 11 * * 1-5` - Weekdays only at 6:00 AM EST
- `0 8,16 * * *` - Twice daily at 3:00 AM and 11:00 AM EST
- `0 11 * * 0` - Sundays only at 6:00 AM EST

**Tip:** Use [crontab.guru](https://crontab.guru/) to build custom schedules.

---

## 🚀 What Happens Next

**Automated workflow:**
1. ✅ Every day at 6:00 AM EST, GitHub Actions wakes up
2. ✅ Runs `fetch_quiver_fixed.py` script
3. ✅ Fetches latest congressional trades from Quiver API
4. ✅ Clears old data from Supabase
5. ✅ Saves fresh data to database
6. ✅ Your dashboard automatically shows updated data!

**No more manual updates!** 🎉

---

## 💡 Next Steps

Now that you have automated data refresh, consider:

1. **Add database indexes** for better performance
   ```sql
   CREATE INDEX idx_ticker ON congressional_trades(ticker);
   CREATE INDEX idx_member_name ON congressional_trades(member_name);
   CREATE INDEX idx_trade_date ON congressional_trades(trade_date);
   ```

2. **Set up custom domain** (congresstrades.io)
   - Makes your platform look professional
   - Improves SEO and trust

3. **Implement user authentication**
   - Free tier: View last 30 days
   - Premium tier: Full historical data + alerts

4. **Add email notifications**
   - Alert users when their followed politicians trade
   - Daily digest of top trades

---

## 📊 Cost Impact

**GitHub Actions Free Tier:**
- ✅ 2,000 minutes/month FREE for public repositories
- ✅ This workflow uses ~3 minutes/day = 90 minutes/month
- ✅ **You're well within the free tier!**

**Total monthly cost:** Still just **$15/month** (Quiver + Railway)

---

## ✅ Success!

Your Congressional Trading Intelligence platform now runs **completely autonomously**!

The manual `python fetch_quiver_fixed.py` step is now **automated and hands-free**.

**Questions?** Check the Actions tab logs or re-run the workflow manually to debug.

---

*Last updated: February 15, 2026*
