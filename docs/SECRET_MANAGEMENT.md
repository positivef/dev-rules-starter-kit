# 🔐 Secret Management Strategy

## Overview
This document outlines the secure handling of sensitive information (API keys, tokens, webhooks, credentials) in the Tier 1 Integration System.

## ⚠️ Golden Rules

1. **NEVER commit secrets to Git**
2. **NEVER hardcode secrets in source code**
3. **ALWAYS use environment variables or secure vaults**
4. **ALWAYS rotate secrets regularly**

## 📋 Secret Management Layers

### 1. Local Development

#### Using .env Files
```bash
# Create .env file (NEVER commit this!)
cp .env.example .env

# Edit .env with your actual secrets
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
OBSIDIAN_VAULT_PATH=C:/Users/your-user/Documents/Obsidian Vault
DATABASE_PASSWORD=your-secure-password
API_KEY=your-api-key-here
```

#### .gitignore Configuration
```gitignore
# Ensure these are in .gitignore
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
credentials/
```

### 2. CI/CD Environment

#### GitHub Actions Secrets
```yaml
# .github/workflows/tier1-ci.yml
env:
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
  API_KEY: ${{ secrets.API_KEY }}
  DATABASE_PASSWORD: ${{ secrets.DATABASE_PASSWORD }}
```

To add secrets:
1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add name and value
4. Reference in workflows as `${{ secrets.SECRET_NAME }}`

### 3. Production Environment

#### Option A: Environment Variables (Basic)
```bash
# Set environment variables in production
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."
export API_KEY="production-api-key"
export DATABASE_PASSWORD="strong-production-password"
```

#### Option B: AWS Secrets Manager (Recommended for AWS)
```python
import boto3
import json

def get_secret(secret_name):
    """Retrieve secret from AWS Secrets Manager."""
    client = boto3.client('secretsmanager')

    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

# Usage
secrets = get_secret('tier1-integration/prod')
slack_webhook = secrets.get('SLACK_WEBHOOK_URL')
```

#### Option C: HashiCorp Vault (Enterprise)
```python
import hvac

def get_vault_secret(path):
    """Retrieve secret from HashiCorp Vault."""
    client = hvac.Client(
        url='https://vault.yourcompany.com',
        token=os.environ['VAULT_TOKEN']
    )

    response = client.secrets.kv.v2.read_secret_version(path=path)
    return response['data']['data']

# Usage
secrets = get_vault_secret('tier1-integration/prod')
```

#### Option D: Docker Secrets (For Docker Deployments)
```yaml
# docker-compose.yml
version: '3.8'

services:
  tier1-integration:
    image: tier1-integration:latest
    secrets:
      - slack_webhook
      - api_key
      - db_password

secrets:
  slack_webhook:
    external: true
  api_key:
    external: true
  db_password:
    external: true
```

```python
# Read Docker secret in Python
def read_docker_secret(secret_name):
    """Read secret from Docker secrets."""
    secret_path = f'/run/secrets/{secret_name}'
    try:
        with open(secret_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return os.environ.get(secret_name.upper())
```

## 🔧 Implementation in Code

### Secure Configuration Loading
```python
# scripts/secure_config_loader.py
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class SecureConfigLoader:
    """Secure configuration loader with multiple fallbacks."""

    def __init__(self):
        # Load .env file if exists (development)
        env_path = Path('.env')
        if env_path.exists():
            load_dotenv(env_path)

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get secret from environment with fallbacks.

        Priority:
        1. Environment variable
        2. Docker secret
        3. AWS Secrets Manager
        4. Default value (for non-sensitive configs only)
        """
        # 1. Try environment variable
        value = os.environ.get(key)
        if value:
            return value

        # 2. Try Docker secret
        secret_path = Path(f'/run/secrets/{key.lower()}')
        if secret_path.exists():
            with open(secret_path, 'r') as f:
                return f.read().strip()

        # 3. Try AWS Secrets Manager (if configured)
        if os.environ.get('USE_AWS_SECRETS'):
            # Implementation shown above
            pass

        # 4. Return default (only for non-sensitive)
        return default

    def get_required_secret(self, key: str) -> str:
        """Get required secret, raise if not found."""
        value = self.get_secret(key)
        if not value:
            raise ValueError(f"Required secret '{key}' not found")
        return value

# Usage
config = SecureConfigLoader()
slack_webhook = config.get_secret('SLACK_WEBHOOK_URL')
api_key = config.get_required_secret('API_KEY')
```

## 📝 .env.example Template

```bash
# Copy this file to .env and fill with actual values
# NEVER commit .env to version control!

# Notification Settings
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-app-specific-password

# Obsidian Integration
OBSIDIAN_VAULT_PATH=/path/to/your/vault
OBSIDIAN_ENABLED=true

# API Keys
API_KEY=your-api-key-here
GITHUB_TOKEN=ghp_your_github_token
OPENAI_API_KEY=sk-your-openai-key

# Database (if applicable)
DATABASE_URL=postgresql://user:password@localhost/dbname
DATABASE_PASSWORD=secure-password-here

# MCP Server Configurations
MCP_CONTEXT7_KEY=your-context7-key
MCP_SEQUENTIAL_KEY=your-sequential-key

# Feature Flags
USE_AWS_SECRETS=false
USE_VAULT=false
ENABLE_NOTIFICATIONS=true
```

## 🚨 Security Checklist

### Before Committing Code
- [ ] Run `git diff` to check no secrets in changes
- [ ] Verify .env is in .gitignore
- [ ] Use `git-secrets` or similar tools to scan
- [ ] Review all configuration files

### Secret Rotation Schedule
- [ ] API Keys: Every 90 days
- [ ] Webhooks: Every 180 days
- [ ] Database passwords: Every 60 days
- [ ] Service tokens: Every 30 days

### Incident Response
If a secret is accidentally exposed:
1. **Immediately rotate** the exposed secret
2. **Audit logs** for any unauthorized access
3. **Update** all systems using the secret
4. **Document** the incident and prevention measures

## 🛠️ Tools and Utilities

### git-secrets Installation
```bash
# Prevent committing secrets
brew install git-secrets  # macOS
# or
git clone https://github.com/awslabs/git-secrets
cd git-secrets && make install

# Initialize in repo
git secrets --install
git secrets --register-aws  # For AWS credentials
```

### pre-commit Hook
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

## 📚 Additional Resources

- [12 Factor App - Config](https://12factor.net/config)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [AWS Secrets Manager Best Practices](https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)

---

**Remember**: Security is everyone's responsibility. When in doubt, ask for help rather than risk exposing sensitive information.
