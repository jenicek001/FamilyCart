# Envi## Development Environment
**Target**: Local development on developer machine

- **Frontend**: Runs on port 9002
- **API**: Uses Next.js proxy to backend (configurable port, default 8005)
- **WebSocket**: Connects to backend (configurable port, default 8005)

## Staging/Production Environment
**Target**: Deployed instances (UAT, production)

- **API**: Auto-detects current hostname and uses backend port (configurable, default 8005)
- **WebSocket**: Auto-detects current hostname and uses backend port (configurable, default 8005)ment Configuration Guide

## How it Works

The FamilyCart frontend automatically detects the appropriate API and WebSocket URLs based on the environment:

### 1. Development (localhost)
- **API**: Uses Next.js proxy to `http://localhost:8005`
- **WebSocket**: Connects to `ws://localhost:8005`
- **Configuration**: Leave `NEXT_PUBLIC_API_URL` empty

### 2. Network Development (accessing from other devices)
- **API**: Auto-detects current hostname and uses port 8005
- **WebSocket**: Auto-detects current hostname and uses port 8005
- **Configuration**: Leave `NEXT_PUBLIC_API_URL` empty

### 3. Production with CloudFlare
- **API**: Set `NEXT_PUBLIC_API_URL=https://yourdomain.com`
- **WebSocket**: Auto-detects from API URL → `wss://yourdomain.com`
- **Configuration**: Set explicit URL in environment

### 4. Production with separate API domain
- **API**: Set `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
- **WebSocket**: Auto-detects from API URL → `wss://api.yourdomain.com`
- **Configuration**: Set explicit URL in environment

## Environment Variables

### Frontend (.env.local)
```bash
# Leave empty for auto-detection (recommended for development)
NEXT_PUBLIC_API_URL=

# Or set explicitly for production:
NEXT_PUBLIC_API_URL=https://yourdomain.com
```

### Backend
Make sure the backend accepts connections from the appropriate interfaces:
```bash
# Development: listen on all interfaces (port configurable via environment)
uvicorn app.main:app --host 0.0.0.0 --port 8005
# Or override with: PORT=8006 uvicorn app.main:app --host 0.0.0.0 --port 8006

# Production: use proper reverse proxy (nginx, CloudFlare, etc.)
```

## Benefits of This Approach

1. **No hardcoded IPs**: Works on any network configuration
2. **Auto-detection**: Automatically adapts to local vs network access
3. **Production ready**: Supports CloudFlare, custom domains, etc.
4. **Development friendly**: Works out of the box for localhost development
5. **Cross-platform**: Same config works on different machines/networks

## Migration from Hardcoded IPs

If you previously had hardcoded IPs:
1. Remove any hardcoded IP addresses from configs
2. Set `NEXT_PUBLIC_API_URL=` (empty) for development
3. Set appropriate production URL for deployment
4. Restart both frontend and backend
