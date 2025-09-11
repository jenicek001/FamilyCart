# connectedhome.cz SSL Certificate

This directory contains SSL certificates for the `connectedhome.cz` domain and its subdomains.

## Domain Coverage

The certificate covers:
- `homeassistant.connectedhome.cz` - Home Assistant instance

## Certificate Type

**CloudFlare Origin Certificate**
- Issued by: CloudFlare
- Valid for: 15 years (until ~2040)
- Type: Origin Certificate (for use with CloudFlare proxy)

## Required Files

The following files are needed but **ignored by git**:

```
connectedhome.cz/
├── connectedhome.cz.crt    # CloudFlare Origin Certificate
└── connectedhome.cz.key    # Private key
```

## Installation Instructions

### 1. Download from CloudFlare Dashboard

1. Go to CloudFlare Dashboard → SSL/TLS → Origin Server
2. Create new certificate for `*.connectedhome.cz` and `connectedhome.cz`
3. Download both PEM files

### 2. Install Certificates

```bash
# Copy certificate files to this directory
cp connectedhome.cz.crt /path/to/nginx/ssl/connectedhome.cz/
cp connectedhome.cz.key /path/to/nginx/ssl/connectedhome.cz/

# Set proper permissions for nginx
chmod 644 connectedhome.cz.crt connectedhome.cz.key
chown root:root connectedhome.cz.*
```

### 3. Nginx Configuration

The certificate is used in nginx configurations like this:

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name homeassistant.connectedhome.cz;

    ssl_certificate /etc/nginx/ssl/connectedhome.cz/connectedhome.cz.crt;
    ssl_certificate_key /etc/nginx/ssl/connectedhome.cz/connectedhome.cz.key;
    
    # Include common SSL settings
    include /etc/nginx/conf.d/ssl-common.conf;
    
    # Your location blocks here...
}
```

## Services Using This Certificate

- **Home Assistant**: `homeassistant.connectedhome.cz`
  - Configuration: `../sites-available/homeassistant`
  - Proxy target: `http://192.168.3.30:8123`

## Security Notes

- ⚠️ **Never commit certificate files to git**
- ✅ Certificate files are automatically ignored by `.gitignore`
- ✅ Use 644 permissions for both certificate and key (nginx requirement)
- ✅ Root ownership required for nginx to read the files

## Verification

```bash
# Test certificate validity
openssl x509 -in connectedhome.cz.crt -text -noout | grep -E "(Subject|Issuer|Not After)"

# Test nginx configuration
nginx -t

# Test SSL handshake
openssl s_client -connect homeassistant.connectedhome.cz:443 -servername homeassistant.connectedhome.cz
```
