# SSL Certificate Configuration for FamilyCart UAT

This directory should contain SSL certificates for the UAT environment.

## Required Files

For the nginx configuration to work properly, you need the following certificate files:

### Self-Signed Certificates (for testing)
```bash
# Generate self-signed certificate for UAT
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout uat.familycart.local.key \
  -out uat.familycart.local.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=uat.familycart.local"
```

### Let's Encrypt Certificates (for production-like UAT)
```bash
# Using certbot (install first: sudo apt install certbot)
sudo certbot certonly --standalone -d uat.familycart.local

# Copy certificates
cp /etc/letsencrypt/live/uat.familycart.local/fullchain.pem uat.familycart.local.crt
cp /etc/letsencrypt/live/uat.familycart.local/privkey.pem uat.familycart.local.key
```

## Expected File Structure
```
nginx/ssl/
├── uat.familycart.local.crt    # Certificate file
├── uat.familycart.local.key    # Private key file
└── dhparam.pem                 # Diffie-Hellman parameters (optional)
```

## Generate DH Parameters (recommended for security)
```bash
openssl dhparam -out dhparam.pem 2048
```

## Security Considerations

1. **File Permissions**: Ensure private keys have restricted permissions
   ```bash
   chmod 600 *.key
   chmod 644 *.crt
   ```

2. **Certificate Renewal**: For Let's Encrypt certificates, set up auto-renewal
   ```bash
   # Add to crontab
   0 3 * * * certbot renew --quiet
   ```

3. **Testing**: Verify certificates are valid
   ```bash
   openssl x509 -in uat.familycart.local.crt -text -noout
   ```

## Docker Compose Integration

The nginx configuration in `docker-compose.uat.yml` mounts this directory as:
```yaml
volumes:
  - ./nginx/ssl:/etc/nginx/ssl:ro
```

The nginx configuration (`deploy/nginx/uat.conf`) expects:
- Certificate: `/etc/nginx/ssl/uat.familycart.local.crt`
- Private key: `/etc/nginx/ssl/uat.familycart.local.key`

## Troubleshooting

- If SSL is not needed for testing, you can comment out the SSL server block in `uat.conf`
- For local testing, add `uat.familycart.local` to your `/etc/hosts` file:
  ```
  127.0.0.1 uat.familycart.local
  ```