# Home Assistant Configuration - Source of Truth Update

## ✅ Completed Tasks

### 1. **Home Assistant nginx Configuration Updated**
- **File**: `deploy/nginx/sites-available/homeassistant`
- **Status**: ✅ **Now source of truth in main repository**
- **Key Changes**:
  - ✅ Fixed deprecated `listen 443 ssl http2;` → `listen 443 ssl; http2 on;`
  - ✅ Replaced problematic upstream `homeassistant_service` with direct `proxy_pass http://192.168.3.30:8123`
  - ✅ Used your proven working proxy parameters
  - ✅ Removed problematic rate limiting zone
  - ✅ Simplified WebSocket connection handling

### 2. **SSL Certificate Security Implemented**
- **Status**: ✅ **Certificate files properly excluded from git**
- **.gitignore Updated** with patterns:
  - `*.crt` - Certificate files
  - `*.key` - Private key files  
  - `*.pem` - PEM format files
  - `**/ssl/**/*.crt` - Certificate files in SSL directories
  - `**/ssl/**/*.key` - Key files in SSL directories
- **Tested**: ✅ Certificate files are automatically ignored

### 3. **SSL Documentation Created**
- **Main SSL README**: `deploy/nginx/ssl/README.md`
  - Comprehensive SSL certificate management guide
  - Security best practices
  - Installation instructions for CloudFlare and Let's Encrypt
- **Domain-specific README**: `deploy/nginx/ssl/connectedhome.cz/README.md`
  - Instructions for connectedhome.cz certificates
  - CloudFlare Origin Certificate setup
  - nginx configuration examples

### 4. **Repository Structure Established**
```
deploy/nginx/ssl/
├── README.md                    # SSL management documentation
├── connectedhome.cz/
│   ├── README.md               # Domain-specific instructions
│   ├── connectedhome.cz.crt    # Certificate (IGNORED by git)
│   └── connectedhome.cz.key    # Private key (IGNORED by git)
└── [future-domains]/
    ├── README.md
    ├── domain.crt              # (IGNORED by git)
    └── domain.key              # (IGNORED by git)
```

## 🎯 Current Status

### **Main Development Repository** ✅
- **Location**: `/home/honzik/GitHub/FamilyCart/FamilyCart`
- **Home Assistant Config**: ✅ Updated and committed as source of truth
- **SSL Documentation**: ✅ Complete and committed
- **Certificate Security**: ✅ Files properly excluded from git
- **GitHub Status**: ✅ Pushed to `origin/main` (commit: 1b01fe8)

### **UAT Operations Repository** ✅
- **Location**: `/opt/familycart-uat-repo`
- **Home Assistant**: ✅ Working with your proven parameters
- **SSL Certificates**: ✅ Installed and functioning
- **nginx Status**: ✅ Configuration valid and loaded

## 🔄 Working Parameters (Source of Truth)

The following Home Assistant proxy parameters are now officially documented as working:

```nginx
# Direct proxy to Home Assistant (using your proven working parameters)
proxy_pass http://192.168.3.30:8123;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; # Important for correct logging on backend
proxy_set_header X-Forwarded-Proto $scheme; # Let backend know the original protocol
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

## 📋 Next Steps

1. **For new deployments**: Use main repository as source (`/home/honzik/GitHub/FamilyCart/FamilyCart`)
2. **For certificate installation**: Follow `deploy/nginx/ssl/README.md` instructions
3. **For Home Assistant setup**: Use `deploy/nginx/sites-available/homeassistant` configuration
4. **For SSL certificates**: Install in appropriate domain subdirectory (auto-ignored by git)

---
**Date**: September 11, 2025  
**Status**: ✅ **COMPLETE - Home Assistant configuration is now source of truth**
