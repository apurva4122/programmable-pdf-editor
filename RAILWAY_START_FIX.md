# Railway Start Command Fix

## Issue
Railway is still trying to use the old standalone server path even after updating the config files.

## Solution

### Option 1: Update Start Command in Railway Dashboard (Recommended)

1. Go to Railway Dashboard
2. Select your **Frontend** service
3. Go to **Settings** → **Deploy**
4. Find **Start Command** field
5. Change it to: `npm start`
6. Save and redeploy

### Option 2: Clear Railway Cache

If the above doesn't work:
1. Go to Railway Dashboard
2. Select your **Frontend** service
3. Go to **Settings** → **Deploy**
4. Click **Clear Build Cache**
5. Redeploy the service

### Option 3: Verify Configuration Files

Make sure these files are correct:

**frontend/nixpacks.toml:**
```toml
[start]
cmd = "npm start"
```

**frontend/railway.json:**
```json
{
  "deploy": {
    "startCommand": "npm start"
  }
}
```

**frontend/next.config.js:**
```js
// Should NOT have output: 'standalone'
```

## Why This Happens

Railway might cache the start command or use settings from the dashboard instead of config files. Always update both the config files AND the Railway dashboard settings.

