# Railway Build Fix - Frontend

## Issue
Railway build was failing because `npm ci` requires `package-lock.json` which wasn't in the repository.

## Solution
1. **Updated Dockerfile**: Changed from `npm ci` to `npm install` (works without lock file)
2. **Created Nixpacks config**: Added `frontend/nixpacks.toml` to ensure Railway uses Nixpacks instead of Dockerfile
3. **Updated Railway config**: Explicitly set Nixpacks as builder

## What Changed

### Frontend Dockerfile
- Changed: `RUN npm ci` → `RUN npm install`
- This allows builds without package-lock.json

### Frontend Nixpacks Config
- Created `frontend/nixpacks.toml` with explicit build steps
- Uses `npm install` instead of `npm ci`

### Railway Config
- Updated to explicitly use Nixpacks builder
- Points to nixpacks.toml configuration

## For Future Builds

If you want to use `npm ci` for faster, more reliable builds:

1. Generate package-lock.json locally:
   ```bash
   cd frontend
   npm install
   ```

2. Commit package-lock.json:
   ```bash
   git add frontend/package-lock.json
   git commit -m "Add package-lock.json"
   git push
   ```

3. Update Dockerfile back to use `npm ci`:
   ```dockerfile
   COPY package.json package-lock.json ./
   RUN npm ci
   ```

## Current Status
✅ Build should now work with `npm install` (no lock file required)
✅ Railway will use Nixpacks configuration
✅ Faster builds possible with package-lock.json in future

