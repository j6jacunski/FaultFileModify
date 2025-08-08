# Frontend Environment Setup

## Problem
When accessing the application from a separate PC, the frontend tries to make API calls to `localhost:49490`, which refers to the client's machine, not your server.

## Solution 1: Use Relative URLs (Recommended)

The frontend API configuration has been updated to use relative URLs:

```typescript
// frontend/src/services/api.ts
const API_BASE_URL = process.env.REACT_APP_API_URL || '';
```

This means API calls will go to the same server that serves the frontend.

## Solution 2: Environment Variables

### For Development
Create `frontend/.env.development`:
```
REACT_APP_API_URL=http://localhost:49490
```

### For Production
Create `frontend/.env.production`:
```
REACT_APP_API_URL=
```

## Solution 3: Build-time Configuration

When building the frontend, you can set the environment variable:

```bash
# Build with specific API URL
REACT_APP_API_URL=http://YOUR_SERVER_IP:49490 npm run build

# Or build with relative URLs
REACT_APP_API_URL= npm run build
```

## Rebuild the Application

After making changes, rebuild the Docker container:

```bash
docker compose down
docker compose up -d --build
```

## Test the Fix

1. **Local access:** http://localhost:49490 (should still work)
2. **Remote access:** http://YOUR_SERVER_IP:49490 (should now work)

## Verification

Check that API calls are going to the correct server:
1. Open browser developer tools (F12)
2. Go to Network tab
3. Upload a file
4. Verify the API calls go to the correct server IP
