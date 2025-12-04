# Vercel Deploy Instructions - Proxy Route Fix

## Problem
The `/api/live/frame` route returns 404 on Vercel even though:
- ✅ File exists at `src/app/api/live/frame/route.ts`
- ✅ Build succeeds locally (`npm run build`)
- ✅ Route appears in build output: `├ λ /api/live/frame`

## Solution: Force Redeploy on Vercel

### Option 1: Trigger Redeploy via Git Push
1. Make a small change to trigger redeploy:
   ```bash
   cd visionsleuthai.v3/frontend
   echo "# Force redeploy" >> README.md
   git add README.md
   git commit -m "Force Vercel redeploy for /api/live/frame route"
   git push origin main
   ```

### Option 2: Redeploy via Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Select your project: `master-thesis-nu`
3. Go to **Deployments** tab
4. Click **⋯** (three dots) on the latest deployment
5. Click **Redeploy**
6. ✅ Check **"Use existing Build Cache"** is **UNCHECKED** (important!)
7. Click **Redeploy**

### Option 3: Clear Vercel Cache and Redeploy
1. Go to Vercel Dashboard → Project Settings → General
2. Scroll down to **"Clear Build Cache"**
3. Click **Clear**
4. Then redeploy (Option 2)

## Verify Deployment
After redeploy, check:
1. Vercel deployment logs show the route: `├ λ /api/live/frame`
2. Test the route: `https://master-thesis-nu.vercel.app/api/live/frame` (should return 405 Method Not Allowed for GET, which is correct)
3. Test POST from browser console:
   ```javascript
   fetch('/api/live/frame', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ image: 'test' })
   }).then(r => r.json()).then(console.log)
   ```

## Why This Happens
- Vercel caches builds aggressively
- Sometimes route files aren't picked up on first deploy
- Force redeploy without cache ensures fresh build


