# Git Repository Structure

## 📁 Repository Layout

You now have **two separate Git repositories**:

### 1. OrcaSlicer (Existing)
```
~/Documents/OrcaSlicer/
├── .git/                    # OrcaSlicer repo
├── src/                     # Source code (with your fix)
├── build/                   # Your custom build
└── ...
```

**Purpose:** Track OrcaSlicer source code and your custom modifications

**Remote:** https://github.com/SoftFever/OrcaSlicer (upstream)

### 2. Print Service (New)
```
~/AI_PIPELINE/service/
├── .git/                    # Service repo (independent)
├── server.js
├── routes/
├── utils/
└── ...
```

**Purpose:** Track your API service code

**Remote:** None yet (you can push to GitHub/GitLab)

### 3. AI_PIPELINE (Parent Directory)
```
~/AI_PIPELINE/
├── .gitignore              # Excludes service/ directory
├── service/                # Has its own .git (ignored by parent)
├── LOCKED_SPLIT_STAGE/
├── SLICED_OUTPUT/
├── slice_pipeline.sh
└── *.md                    # Documentation
```

**Status:** Not a Git repo (just a working directory)

**Note:** If you want to track the pipeline scripts and docs, you can `git init` here too, but the `service/` directory will be ignored (it has its own repo).

## 🔄 Working with Both Repos

### Service Repository
```bash
cd ~/AI_PIPELINE/service

# Check status
git status

# Make changes
git add .
git commit -m "Add new feature"

# Push to remote (after setting up)
git push origin main
```

### OrcaSlicer Repository
```bash
cd ~/Documents/OrcaSlicer

# Check status
git status

# Your custom changes
git add src/libslic3r/Print.cpp
git commit -m "Fix validation bug for CLI"

# Keep track of upstream
git remote add upstream https://github.com/SoftFever/OrcaSlicer.git
git fetch upstream
```

## 🚀 Setting Up Remote for Service

### Option 1: GitHub
```bash
cd ~/AI_PIPELINE/service

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/orcaslicer-print-service.git
git branch -M main
git push -u origin main
```

### Option 2: GitLab
```bash
cd ~/AI_PIPELINE/service

git remote add origin https://gitlab.com/YOUR_USERNAME/orcaslicer-print-service.git
git branch -M main
git push -u origin main
```

### Option 3: Keep Local Only
```bash
# No remote needed - just commit locally
cd ~/AI_PIPELINE/service
git add .
git commit -m "Your changes"
```

## 📝 What's Ignored

### Service `.gitignore`:
- `node_modules/` - Dependencies
- `.env` - Secrets
- `logs/*.log` - Log files
- `.DS_Store` - macOS files

### AI_PIPELINE `.gitignore`:
- `service/` - Has its own repo
- `*.stl` - Large STL files
- `*.gcode` - Generated G-code
- `*.log` - Logs

### OrcaSlicer `.gitignore`:
- Already configured by upstream

## 🎯 Recommended Workflow

### For Service Development:
```bash
cd ~/AI_PIPELINE/service

# 1. Make changes
vim server.js

# 2. Test
npm run dev

# 3. Commit
git add .
git commit -m "Descriptive message"

# 4. Push (if remote configured)
git push
```

### For OrcaSlicer Modifications:
```bash
cd ~/Documents/OrcaSlicer

# 1. Make changes
vim src/libslic3r/Print.cpp

# 2. Rebuild
./build_release_macos.sh

# 3. Commit your changes
git add src/
git commit -m "Fix: Disable validation for CLI"

# 4. Keep separate from upstream
git branch my-fixes
```

## 🔍 Quick Reference

### Check which repo you're in:
```bash
pwd                    # Show current directory
git remote -v          # Show remote URLs
git log --oneline -5   # Show recent commits
```

### Service repo status:
```bash
cd ~/AI_PIPELINE/service && git status
```

### OrcaSlicer repo status:
```bash
cd ~/Documents/OrcaSlicer && git status
```

## ✅ Current Status

- ✅ Service repo initialized: `~/AI_PIPELINE/service/.git`
- ✅ Initial commit made with all service files
- ✅ `.gitignore` configured for both locations
- ✅ Repos are completely independent
- ⏳ Remote not configured yet (optional)

## 🎓 Benefits of This Setup

1. **Independence:** Changes in service don't affect OrcaSlicer and vice versa
2. **Clean history:** Each repo has its own commit history
3. **Easy deployment:** Service can be deployed independently
4. **Upstream tracking:** Can still pull OrcaSlicer updates
5. **Flexibility:** Can push service to different remote than OrcaSlicer

---

**You're all set!** Both repos are independent and ready for development. 🎉
