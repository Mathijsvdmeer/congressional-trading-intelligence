# Push Your Code to GitHub - Commands

Your GitHub repository is ready! 🎉

**Repository:** https://github.com/Mathijsvdmeer/congressional-trading-intelligence

---

## Terminal Commands to Run

Open Terminal and run these commands **in order**:

```bash
# Navigate to your project folder
cd "/Users/Mathijs/Congress tracker/Coding"

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit with a message
git commit -m "Initial commit: Congressional Trading Intelligence with automated data refresh"

# Add the GitHub remote
git remote add origin https://github.com/Mathijsvdmeer/congressional-trading-intelligence.git

# Rename branch to main
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## What These Commands Do

1. **Navigate** to your project folder
2. **Initialize** git repository
3. **Add** all your files (GitHub Actions workflow, scripts, etc.)
4. **Commit** everything with a descriptive message
5. **Connect** to your GitHub repository
6. **Push** all files to GitHub

---

## After Pushing

Once the code is pushed, we'll add the 3 GitHub secrets:
- QUIVER_API_KEY
- SUPABASE_URL
- SUPABASE_KEY

Then you can test the automated workflow!

---

## Troubleshooting

**"fatal: remote origin already exists"**
```bash
git remote remove origin
git remote add origin https://github.com/Mathijsvdmeer/congressional-trading-intelligence.git
```

**Permission denied (authentication failed)**
- GitHub may prompt you to authenticate
- Use your GitHub username and personal access token
- Or authenticate via browser when prompted

---

**Ready?** Run the commands above in Terminal, then I'll help you add the GitHub secrets! 🚀
