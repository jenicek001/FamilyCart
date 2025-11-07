# SSL Certificate Management

## Directory Structure

This directory contains SSL certificates for different domains used by the FamilyCart application.

```
ssl/
├── README.md                    # This file
├── connectedhome.cz/
│   ├── README.md               # Domain-specific certificate instructions
│   ├── connectedhome.cz.crt    # Certificate file (IGNORED by git)
│   └── connectedhome.cz.key    # Private key (IGNORED by git)
└── [other-domains]/
    ├── README.md
    ├── domain.crt
    └── domain.key
```

## ⚠️ Security Notice

**SSL certificates and private keys are automatically ignored by git** and should NEVER be committed to the repository.

The following file patterns are excluded in `.gitignore`:
- `*.crt` - Certificate files
- `*.key` - Private key files
- `*.pem` - PEM format certificates
- `ssl/` - This entire directory structure
- `**/ssl/**` - Any SSL directories

## Setting Up Certificates

### For CloudFlare Origin Certificates

1. **Create domain directory**: `mkdir -p ssl/yourdomain.com`
2. **Generate certificates in CloudFlare Dashboard**:
   - Go to SSL/TLS → Origin Server
   - Create Certificate
   - Choose your domain(s)
   - Download both certificate and private key
3. **Install certificates**:
   ```bash
   # Copy certificate files to domain directory
   cp yourdomain.com.crt ssl/yourdomain.com/
   cp yourdomain.com.key ssl/yourdomain.com/
   
   # Set proper permissions (important for nginx)
   chmod 644 ssl/yourdomain.com/yourdomain.com.crt
   chmod 644 ssl/yourdomain.com/yourdomain.com.key
   chown root:root ssl/yourdomain.com/yourdomain.com.*
   ```

### For Let's Encrypt Certificates

1. **Install certbot**: `sudo apt install certbot python3-certbot-nginx`
2. **Generate certificate**: `sudo certbot certonly --webroot -w /var/www/html -d yourdomain.com`
3. **Link to nginx SSL directory**:
   ```bash
   mkdir -p ssl/yourdomain.com
   ln -s /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/yourdomain.com/yourdomain.com.crt
   ln -s /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/yourdomain.com/yourdomain.com.key
   ```

## Nginx Configuration

SSL certificates should be referenced in nginx configurations as:

```nginx
ssl_certificate /etc/nginx/ssl/yourdomain.com/yourdomain.com.crt;
ssl_certificate_key /etc/nginx/ssl/yourdomain.com/yourdomain.com.key;
```

## Verification

Test your SSL setup:
```bash
# Test nginx configuration
nginx -t

# Check certificate expiration
openssl x509 -in ssl/yourdomain.com/yourdomain.com.crt -text -noout | grep "Not After"

# Test SSL connection
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

---
**Remember**: Never commit actual certificate files to git. Only commit README files and configuration templates.
