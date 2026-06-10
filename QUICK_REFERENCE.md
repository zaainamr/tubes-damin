# ⚡ QUICK REFERENCE - Copy & Paste Commands

## STEP 1: Local Testing (Sebelum Upload)

```bash
# Navigate to project folder
cd "c:\Users\LENOVO\Downloads\Tubes Damin"

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Run Streamlit app
streamlit run app_streamlit.py

# HASIL YANG DIHARAPKAN:
# - Browser membuka http://localhost:8501
# - Dashboard dengan 4 halaman: Beranda, Data Understanding, Data Preparation, Data Modeling
# - Tidak ada error di terminal
```

---

## STEP 2: GitHub Setup (First Time Only)

### 2A. Via Command Line (RECOMMENDED)

```bash
# Navigate to project
cd "c:\Users\LENOVO\Downloads\Tubes Damin"

# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Job Salary Prediction Dashboard"

# Rename branch to main
git branch -M main

# Add remote (CHANGE YOUR_USERNAME & REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/tubes-damin.git

# Push to GitHub
git push -u origin main

# VERIFY: Check github.com/YOUR_USERNAME/tubes-damin
```

### 2B. Via GitHub Web Interface

1. Go to https://github.com/new
2. Repository name: `tubes-damin`
3. Description: `Job Salary Prediction Dashboard - Data Mining`
4. Choose: Public
5. Create repository
6. Copy commands from "push an existing repository from the command line"
7. Run di terminal

---

## STEP 3: Verify GitHub Upload

```bash
# Check remote
git remote -v

# EXPECTED OUTPUT:
# origin  https://github.com/YOUR_USERNAME/tubes-damin.git (fetch)
# origin  https://github.com/YOUR_USERNAME/tubes-damin.git (push)

# Check if files are on GitHub
git log --oneline

# Should show your commits
```

---

## STEP 4: Deploy to Streamlit Cloud

### Automated (EASIEST)

1. Open https://share.streamlit.io
2. Login dengan GitHub account
3. Click "New app"
4. Select:
   - Repository: `tubes-damin`
   - Branch: `main`
   - Main file path: `app_streamlit.py`
5. Click "Deploy"
6. Wait 2-5 minutes untuk build

### Manual (If needed)

```bash
# Follow: https://docs.streamlit.io/deploy/streamlit-cloud/deploy-your-app
# Step by step di Streamlit Cloud documentation
```

---

## STEP 5: Access Your Live App

```
URL: https://share.streamlit.io/YOUR_USERNAME/tubes-damin/main/app_streamlit.py

ATAU

Streamlit Cloud Dashboard: https://share.streamlit.io
-> Click your app "tubes-damin"
```

---

## 🔄 COMMON WORKFLOWS

### After Making Changes Locally

```bash
# Check what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "Fix: Update XYZ feature"

# Push to GitHub (auto-redeploy on Streamlit Cloud)
git push origin main
```

### View Deployment Logs (Streamlit Cloud)

1. Go to https://share.streamlit.io
2. Click app "tubes-damin"
3. Click "Deploy logs" tab
4. View build & runtime logs

### If Deployment Fails

```bash
# Check local app still works
streamlit run app_streamlit.py

# If works locally, check requirements.txt
cat requirements.txt

# If requirements okay, check deployment logs on Streamlit Cloud
# Usually: missing package or typo in requirements.txt
```

---

## 📝 FILE CHECKLIST BEFORE PUSH

```bash
# Must have these files:
- app_streamlit.py          ✓
- requirements.txt          ✓
- README.md                 ✓
- .gitignore               ✓
- .streamlit/config.toml   ✓

# Optional:
- DEPLOYMENT_GUIDE.md      (helpful)
- SETUP_SUMMARY.md         (this file)
- Tubes_Datmin.ipynb       (for reference)
```

---

## ⚠️ TROUBLESHOOTING

### Issue: "fatal: not a git repository"
```bash
# Solution: Initialize git first
git init
git add .
git commit -m "Initial commit"
# Then continue with remote add & push
```

### Issue: "fatal: remote origin already exists"
```bash
# Solution: Remove old remote
git remote remove origin

# Then add new remote
git remote add origin https://github.com/YOUR_USERNAME/tubes-damin.git
git push -u origin main
```

### Issue: "rejected ... (fetch first)"
```bash
# Solution: Pull latest changes first
git pull origin main

# Then push
git push origin main
```

### Issue: "fatal: 'origin' does not appear to be a 'git' repository"
```bash
# Solution: Check remote is correct
git remote -v

# If empty, add remote again
git remote add origin https://github.com/YOUR_USERNAME/tubes-damin.git
```

### Issue: Streamlit Cloud shows "ModuleNotFoundError"
```bash
# Solution 1: Check requirements.txt has all packages
cat requirements.txt

# Solution 2: Reinstall locally
pip install -r requirements.txt

# Solution 3: Commit & push again
git add requirements.txt
git commit -m "Update requirements"
git push origin main

# Wait for Streamlit Cloud to redeploy (auto-triggers on push)
```

---

## 🎯 VERIFICATION CHECKLIST

After following all steps, verify:

- [ ] App runs locally: `streamlit run app_streamlit.py` ✓
- [ ] No errors in console ✓
- [ ] Dashboard loads with 4 tabs ✓
- [ ] Files pushed to GitHub ✓
- [ ] GitHub repo visible at: https://github.com/YOUR_USERNAME/tubes-damin ✓
- [ ] App deployed on Streamlit Cloud ✓
- [ ] Live app accessible at Streamlit URL ✓
- [ ] All visualizations render correctly ✓

---

## 💡 TIPS & TRICKS

### Speed up git operations
```bash
# Cache credentials (Windows)
git config --global credential.helper wincred

# Cache for 1 hour (Linux/Mac)
git config --global credential.helper 'cache --timeout=3600'
```

### Useful git commands
```bash
# See all commits
git log --oneline

# See what changed
git diff

# Undo last commit (local only)
git reset HEAD~1

# Check current branch
git branch -a

# Create new branch
git checkout -b feature/new-feature

# Switch branch
git checkout main
```

### Streamlit tips
```bash
# Run in specific port
streamlit run app_streamlit.py --logger.level=debug --server.port 8502

# Run without browser auto-open
streamlit run app_streamlit.py --logger.level=info --browser.gatherUsageStats false

# View config
streamlit config show
```

---

## 📦 FILES ORGANIZATION

```
Your GitHub Repository Structure:
tubes-damin/
├── app_streamlit.py           (Main file - Streamlit akan jalankan ini)
├── requirements.txt           (Streamlit akan install packages dari sini)
├── README.md                  (Streamlit Cloud display ini di about)
├── .gitignore                 (Git akan skip files listed here)
├── .streamlit/
│   └── config.toml           (Optional: Theme & settings)
├── DEPLOYMENT_GUIDE.md        (Optional: Untuk documentation)
├── SETUP_SUMMARY.md           (Optional: Untuk documentation)
└── Tubes_Datmin.ipynb        (Optional: Original notebook reference)
```

---

## 🚀 COMPLETE WORKFLOW (From Start to Finish)

```bash
# 1. TEST LOCALLY (5 minutes)
cd "c:\Users\LENOVO\Downloads\Tubes Damin"
.venv\Scripts\activate
streamlit run app_streamlit.py
# Browser: http://localhost:8501
# Verify: 4 tabs muncul, visualisasi oke
# Ctrl+C untuk stop

# 2. SETUP GIT (2 minutes)
git init
git add .
git commit -m "Initial commit: Job Salary Prediction Dashboard"
git branch -M main

# 3. CREATE GITHUB REPO (2 minutes)
# Go to https://github.com/new
# Create repo "tubes-damin"
# Copy the URL

# 4. PUSH TO GITHUB (1 minute)
git remote add origin https://github.com/YOUR_USERNAME/tubes-damin.git
git push -u origin main

# 5. DEPLOY TO STREAMLIT CLOUD (5 minutes)
# Go to https://share.streamlit.io
# New app: tubes-damin, app_streamlit.py
# Deploy
# Wait for build...

# 6. VERIFY (1 minute)
# https://share.streamlit.io/YOUR_USERNAME/tubes-damin/main/app_streamlit.py
# Try all tabs, verify working

# DONE! ✅
```

---

## 📞 QUICK LINKS

- GitHub: https://github.com/new
- Streamlit Cloud: https://share.streamlit.io
- Streamlit Docs: https://docs.streamlit.io
- Python Docs: https://docs.python.org/3/

---

## 💾 ENVIRONMENT VARIABLES (Optional for Advanced)

Jika perlu Kaggle API key di Streamlit Cloud:

1. Get token dari: https://www.kaggle.com/account/api
2. Di Streamlit Cloud: App settings → Secrets
3. Paste:
```
kaggle_username = "your_username"
kaggle_key = "your_api_key"
```

---

## 🎓 LEARNING RESOURCES

- Streamlit Tutorial: https://docs.streamlit.io/library/get-started
- Git Tutorial: https://git-scm.com/docs
- GitHub Guide: https://guides.github.com
- Kaggle API: https://www.kaggle.com/docs/api

---

**TIPS**: 
- Copy commands exactly (change YOUR_USERNAME)
- Test locally first before push to GitHub
- Check Streamlit Cloud logs if deployment fails
- Git status regularly: `git status`

**Ready to deploy? Start with STEP 1!** 🚀

---

Last Updated: 2024
