# SSL Certificates for UAT Environment

## Directory Structure
```
ssl/
├── uat.familycart.local.crt  # Primary UAT certificate
├── uat.familycart.local.key  # Primary UAT private key
└── README.md                 # This file
```

## Certificate Installation

### For Self-Signed (Development/Testing):
```bash
# Generate self-signed certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/uat.familycart.local.key \
    -out ssl/uat.familycart.local.crt \
    -subj "/C=CZ/ST=Prague/L=Prague/O=FamilyCart/CN=uat.familycart.local"

# Set correct permissions
chmod 600 ssl/uat.familycart.local.*
```

### For Production Certificates:
1. Obtain certificates from your CA
2. Copy certificate to `ssl/uat.familycart.local.crt`
3. Copy private key to `ssl/uat.familycart.local.key`  
4. Set permissions: `chmod 600 ssl/uat.familycart.local.*`
