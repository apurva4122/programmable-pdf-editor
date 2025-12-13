# GitHub Repository Setup Instructions

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Repository name: `programmable-pdf-editor` (or your preferred name)
5. Description: "A web application for programmatically editing PDFs using OCR"
6. Choose **Public** or **Private**
7. **DO NOT** initialize with README, .gitignore, or license (we already have these)
8. Click "Create repository"

## Step 2: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Use these commands:

```bash
# Add the remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/programmable-pdf-editor.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

## Step 3: Verify

1. Go to your GitHub repository page
2. You should see all your files
3. Check that the README.md displays correctly

## Step 4: Set Up GitHub Actions Secrets (Optional - for Vercel deployment)

If you want to enable automatic Vercel deployment:

1. Go to your repository Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `VERCEL_TOKEN`
4. Value: Your Vercel token (get it from Vercel dashboard → Settings → Tokens)

## Step 5: Enable GitHub Pages (Optional)

If you want to host documentation:

1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: `main` / `docs` folder
4. Save

## Troubleshooting

### If you get authentication errors:
- Use GitHub CLI: `gh auth login`
- Or use SSH: `git remote set-url origin git@github.com:YOUR_USERNAME/programmable-pdf-editor.git`

### If branch name conflicts:
```bash
git branch -M main
git push -u origin main
```

