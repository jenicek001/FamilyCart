# Email Service Environment Configuration for UAT and PROD

**Date**: November 13, 2025  
**Purpose**: Configure email service for UAT and Production deployments  

## Required Environment Variables

Add these variables to your `.env` file in the deployment directory:

### UAT Configuration (`/opt/familycart-uat/.env`)

```bash
# ============================================================================
# EMAIL SERVICE CONFIGURATION - UAT
# ============================================================================

# Email Provider
EMAIL_PROVIDER=brevo

# Sender Configuration
FROM_EMAIL=noreply@familycart.app
FROM_NAME=FamilyCart

# Frontend URL (UAT)
FRONTEND_URL=https://uat.familycart.app

# Brevo SMTP Credentials (Use the same credentials from development .env)
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=<copy-from-development-env>
BREVO_SMTP_PASSWORD=<copy-from-development-env>

# Token Expiration Times (seconds)
VERIFICATION_TOKEN_LIFETIME_SECONDS=172800  # 48 hours
RESET_PASSWORD_TOKEN_LIFETIME_SECONDS=3600  # 1 hour
INVITATION_TOKEN_LIFETIME_SECONDS=604800    # 7 days
```

### PROD Configuration (`.env` for production deployment)

```bash
# ============================================================================
# EMAIL SERVICE CONFIGURATION - PRODUCTION
# ============================================================================

# Email Provider
EMAIL_PROVIDER=brevo

# Sender Configuration
FROM_EMAIL=noreply@familycart.app
FROM_NAME=FamilyCart

# Frontend URL (Production)
FRONTEND_URL=https://familycart.app

# Brevo SMTP Credentials (Use the same credentials from development .env)
BREVO_SMTP_HOST=smtp-relay.brevo.com
BREVO_SMTP_PORT=587
BREVO_SMTP_USER=<copy-from-development-env>
BREVO_SMTP_PASSWORD=<copy-from-development-env>

# Token Expiration Times (seconds)
VERIFICATION_TOKEN_LIFETIME_SECONDS=172800  # 48 hours
RESET_PASSWORD_TOKEN_LIFETIME_SECONDS=3600  # 1 hour
INVITATION_TOKEN_LIFETIME_SECONDS=604800    # 7 days
```

## Deployment Steps

### 1. UAT Deployment

```bash
# SSH to UAT server
ssh your-uat-server

# Navigate to UAT directory
cd /opt/familycart-uat

# Stop services
docker compose -f docker-compose.uat.yml down

# Edit .env file
nano .env
# Add the email configuration variables from above

# Pull latest changes (automated via CI/CD)
git pull origin develop

# Rebuild and restart services
docker compose -f docker-compose.uat.yml build backend
docker compose -f docker-compose.uat.yml up -d

# Verify backend logs
docker compose -f docker-compose.uat.yml logs -f backend
```

### 2. Production Deployment

```bash
# SSH to production server
ssh your-production-server

# Navigate to production directory
cd /opt/familycart-prod  # or wherever production is deployed

# Stop services
docker compose down

# Edit .env file
nano .env
# Add the email configuration variables from above

# Pull latest changes (from main branch after merge)
git pull origin main

# Rebuild and restart services
docker compose build backend
docker compose up -d

# Verify backend logs
docker compose logs -f backend
```

## Testing Email Service in UAT

### 1. Test Console Email Provider (Optional Pre-test)

```bash
# Temporarily change EMAIL_PROVIDER in UAT .env
EMAIL_PROVIDER=console

# Restart backend
docker compose -f docker-compose.uat.yml restart backend

# Check logs - emails will print to console
docker compose -f docker-compose.uat.yml logs -f backend

# Try registration at https://uat.familycart.app
# Email should appear in logs
```

### 2. Test Brevo SMTP Provider

```bash
# Set EMAIL_PROVIDER in UAT .env
EMAIL_PROVIDER=brevo

# Restart backend
docker compose -f docker-compose.uat.yml restart backend

# Test endpoints:
# 1. Register new user: POST https://uat.familycart.app/api/v1/auth/register
# 2. Request verification: POST https://uat.familycart.app/api/v1/auth/verify/request
# 3. Reset password: POST https://uat.familycart.app/api/v1/auth/reset-password
```

### 3. Test All Email Templates

```bash
# SSH to UAT server
ssh your-uat-server
cd /opt/familycart-uat

# Run test script inside backend container
docker compose -f docker-compose.uat.yml exec backend poetry run python test_all_templates.py

# Check your email inbox - you should receive 4 test emails
```

## Verification Checklist

### UAT Environment
- [ ] `.env` file updated with email configuration
- [ ] `EMAIL_PROVIDER=brevo` set
- [ ] `FRONTEND_URL=https://uat.familycart.app` set
- [ ] Backend container restarted
- [ ] Test user registration sends verification email
- [ ] Test password reset sends reset email
- [ ] Verify emails received in inbox (not spam)
- [ ] Check email links point to UAT frontend
- [ ] Test clicking verification link
- [ ] Test clicking password reset link

### Production Environment
- [ ] `.env` file updated with email configuration
- [ ] `EMAIL_PROVIDER=brevo` set
- [ ] `FRONTEND_URL=https://familycart.app` set
- [ ] Backend container restarted
- [ ] Test user registration sends verification email
- [ ] Test password reset sends reset email
- [ ] Verify emails received in inbox (not spam)
- [ ] Check email links point to production frontend
- [ ] Monitor Brevo dashboard for delivery rates
- [ ] Check no errors in backend logs

## Monitoring

### Brevo Dashboard
- URL: https://app.brevo.com/
- Check daily email quota usage (300/day on free tier)
- Monitor delivery rates and bounces
- Check spam reports

### Backend Logs
```bash
# UAT
docker compose -f docker-compose.uat.yml logs -f backend | grep -i email

# Production
docker compose logs -f backend | grep -i email
```

### Expected Log Messages
```
INFO - User <uuid> (<email>) has registered.
INFO - Verification requested for user <uuid> (<email>).
INFO - Verification email sent to <email>
INFO - User <uuid> (<email>) requested password reset.
INFO - Password reset email sent to <email>
```

### Error Log Messages
```
ERROR - Failed to send verification email to <email>: <error>
ERROR - Failed to send password reset email to <email>: <error>
```

## Troubleshooting

### Emails not sending
1. Check `EMAIL_PROVIDER` is set to `brevo`
2. Verify Brevo credentials are correct in `.env`
3. Check backend logs for SMTP errors
4. Verify Brevo account is active and not over quota
5. Test SMTP connection manually

### Emails landing in spam
1. Verify SPF record: `nslookup -type=txt familycart.app`
2. Check DKIM is configured in Brevo dashboard
3. Ensure DMARC record exists
4. Monitor Brevo dashboard for spam reports

### Wrong links in emails
1. Verify `FRONTEND_URL` is correct for environment
2. Restart backend after changing `.env`
3. Test with new registration/reset request

### Template rendering errors
1. Check backend logs for Jinja2 errors
2. Verify all template files are deployed
3. Check file permissions in container

## Brevo Account Details

**Account**: Already configured and tested  
**Free Tier**: 300 emails/day  
**Domain**: familycart.app (authenticated)  
**DNS Records**: SPF, DKIM, DMARC configured in Cloudflare  
**SMTP Credentials**: Same for dev/UAT/prod (shared account)  

**Note**: For production at scale, consider upgrading to Brevo paid plan or using separate accounts per environment.

## Security Considerations

### Current Setup
- ✅ Using environment variables (not hardcoded)
- ✅ SMTP credentials encrypted in transit (TLS)
- ✅ Domain authenticated via SPF/DKIM
- ✅ Email failures don't block user flows
- ✅ Credentials not committed to git

### Production Recommendations
- Consider separate Brevo account for production
- Rotate SMTP credentials periodically
- Monitor for unauthorized email sending
- Set up email rate limiting if needed
- Enable 2FA on Brevo account

## Rollback Plan

If email service causes issues:

```bash
# 1. Disable email sending temporarily
EMAIL_PROVIDER=console

# 2. Restart backend
docker compose restart backend

# 3. Emails will print to logs instead of sending

# 4. Investigate issue in logs
docker compose logs backend | grep -i email

# 5. Fix issue and re-enable
EMAIL_PROVIDER=brevo
docker compose restart backend
```

## Next Steps After Deployment

1. Monitor UAT for 24-48 hours
2. Collect user feedback on email delivery
3. Check Brevo dashboard for metrics
4. Verify no spam complaints
5. If stable, proceed with production deployment
6. Consider implementing:
   - Email analytics/tracking
   - Unsubscribe management
   - Email preferences per user
   - Localization support

## Support

**Email Service Documentation**: `backend/EMAIL_SERVICE_README.md`  
**Implementation Status**: `docs/EMAIL_SERVICE_IMPLEMENTATION_STATUS.md`  
**Brevo Support**: https://help.brevo.com/  
**SMTP Troubleshooting**: Test with `poetry run python test_brevo_email.py`
