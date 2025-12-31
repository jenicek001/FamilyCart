# Configuration Directory

This directory contains environment variable templates for different deployment environments.

## Files

- **`.env.development`** - Template for local development with Docker Compose
- **`.env.uat`** - Template for UAT environment (actual secrets should be in vault/secrets manager)
- **`.env.production`** - Template for production environment (actual secrets should be in vault/secrets manager)

## Usage

### Development

Copy `.env.development` to your backend directory or use docker-compose.dev.yml which references these values directly:

```bash
# Using docker-compose (recommended)
docker-compose -f docker-compose.dev.yml up

# Or copy to backend for local development
cp config/.env.development backend/.env
```

### UAT/Production

**DO NOT** commit actual secrets to this repository. Use your secrets management system:

1. Copy the template to your deployment system
2. Replace placeholder values with actual secrets from your vault
3. Inject environment variables during deployment

## Environment Variable Naming Convention

- `DATABASE_URL` - Full PostgreSQL connection string
- `REDIS_URL` - Full Redis connection string
- `SECRET_KEY` - Application secret key (used for JWT signing, etc.)
- `DEBUG` - Enable debug mode (true/false)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ALLOWED_ORIGINS` - CORS allowed origins (comma-separated)
- `NEXT_PUBLIC_*` - Next.js public environment variables (exposed to browser)

## Security Notes

⚠️ **IMPORTANT**:
- Never commit real secrets to version control
- Development credentials are weak by design (not for production)
- Use different secrets for each environment
- Rotate secrets regularly
- Use a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.) for UAT/production

## Twelve-Factor App Compliance

This configuration follows the [Twelve-Factor App](https://12factor.net/) methodology:
- **III. Config** - Store config in the environment
- **X. Dev/prod parity** - Same config structure across all environments
