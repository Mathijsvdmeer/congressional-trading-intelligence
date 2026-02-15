# 🚀 Quick Start: Deploy Automated Data Refresh

**Goal:** Set up daily automated congressional trading data updates in under 10 minutes.

---

## Step 1: Push to GitHub (3 minutes)

```bash
cd "/Users/Mathijs/Congress tracker/Coding"

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Add automated daily data refresh via GitHub Actions"

# Create a NEW repository on GitHub:
# Go to: https://github.com/new
# Repository name: congressional-trading-intelligence
# Make it Public (for free GitHub Actions)
# Don't add README, .gitignore, or license (we have them)
# Click "Create repository"

# Copy the commands GitHub shows you:
git remote add origin https://github.com/YOUR_USERNAME/congressional-trading-intelligence.git
git branch -M main
git push -u origin main
```

**✅ Checkpoint:** Your code is now on GitHub!

---

## Step 2: Add GitHub Secrets (3 minutes)

Go to your repository on GitHub:
`https://github.com/YOUR_USERNAME/congressional-trading-intelligence`

1. Click **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"** (you'll do this 3 times)

**Add these 3 secrets:**

| Name | Value |
|------|-------|
| `QUIVER_API_KEY` | `9470ba57b0b4e9ab5dae1ab77ce91573c9334cdb` |
| `SUPABASE_URL` | Get from Railway environment variables |
| `SUPABASE_KEY` | Get from Railway environment variables |

**To find Supabase credentials:**
1. Go to Railway dashboard: https://railway.app/
2. Select your `congress-trader-api` project
3. Click **Variables** tab
4. Copy `SUPABASE_URL` and `SUPABASE_KEY`

**✅ Checkpoint:** All 3 secrets are added!

---

## Step 3: Test the Workflow (2 minutes)

1. Go to **Actions** tab in your GitHub repository
2. Click **"Daily Congressional Trading Data Refresh"** workflow
3. Click **"Run workflow"** dropdown (on the right)
4. Click green **"Run workflow"** button
5. Wait 2-3 minutes and watch it run!

**Expected output:**
```
✅ Set up Python 3.11
✅ Install dependencies
✅ Fetch congressional trading data
✅ Successfully fetched 109,847 trades
✅ Saved to Supabase database
✅ Data refresh completed successfully
```

**✅ Checkpoint:** Workflow runs successfully!

---

## Step 4: Enable Email Notifications (1 minute)

Get notified if the daily refresh fails:

1. Click your profile picture (top right) → **Settings**
2. **Notifications** → **Actions**
3. Check ✅ **"Send notifications for failed workflows only"**
4. Save changes

**✅ Checkpoint:** You'll get emailed if something breaks!

---

## 🎉 Done! What Happens Now?

**Every day at 6:00 AM EST:**
- ✅ GitHub Actions automatically runs
- ✅ Fetches latest congressional trades from Quiver API
- ✅ Updates your Supabase database
- ✅ Your dashboard shows fresh data

**No more manual `python fetch_quiver_fixed.py` commands!**

---

## 📊 Verify It's Working

**Check the Actions tab daily:**
- Go to: `https://github.com/YOUR_USERNAME/congressional-trading-intelligence/actions`
- See green checkmarks ✅ for successful runs
- See red X marks ❌ for failures (you'll get an email)

**View your dashboard:**
- Frontend: https://calm-entremet-cf440f.netlify.app
- Should show fresh data every morning after 6 AM EST

---

## 🔧 Troubleshooting

**Workflow failed with "Error: Process completed with exit code 1"**
- Check GitHub secrets are typed correctly (no extra spaces!)
- Verify Quiver API key is active: https://www.quiverquant.com/settings/api

**No trades fetched**
- Check your Quiver subscription is active
- Hobbyist tier ($10/month) should include congressional trading
- Try manual run: `python fetch_quiver_fixed.py`

**Workflow doesn't appear in Actions tab**
- Make sure `.github/workflows/daily-data-refresh.yml` was pushed to GitHub
- Run: `git status` to check uncommitted files
- Enable Actions in repo Settings if disabled

---

## 📋 What Files Were Created

1. ✅ `.github/workflows/daily-data-refresh.yml` - Automation workflow
2. ✅ `.gitignore` - Protects sensitive files from being committed
3. ✅ `AUTOMATED_REFRESH_SETUP.md` - Detailed documentation
4. ✅ `QUICK_START.md` - This file!

---

## 🚀 Next Steps

Now that data updates are automated, tackle these improvements:

1. **Add database indexes** for performance
2. **Set up custom domain** (congresstrades.io)
3. **Build user authentication** (free vs premium tiers)
4. **Add email alerts** (notify users of politician trades)

---

## ✅ Success Checklist

- [ ] Code pushed to GitHub
- [ ] All 3 secrets added (QUIVER_API_KEY, SUPABASE_URL, SUPABASE_KEY)
- [ ] Workflow tested manually (green checkmark)
- [ ] Email notifications enabled
- [ ] First automated run scheduled for tomorrow 6 AM EST

**All done? Congratulations! Your platform now runs on autopilot! 🎉**

---

*Questions? Check `AUTOMATED_REFRESH_SETUP.md` for detailed troubleshooting.*
