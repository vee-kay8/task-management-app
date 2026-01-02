# Security Hardening Checklist - Task Management Application

## Overview
This checklist ensures Docker containers and the application are secure for production deployment.

## Pre-Deployment Security Checklist

### ✅ Container Security

#### Image Security
- [x] Using official base images (python:3.9-slim, node:18-alpine, postgres:15-alpine)
- [x] Multi-stage builds implemented (reduces attack surface)
- [x] Running as non-root users (appuser, nextjs)
- [x] No secrets in Dockerfiles or images
- [x] Minimal base images (Alpine/Slim variants)
- [ ] Regular vulnerability scanning enabled
- [ ] Image signing with Docker Content Trust
- [ ] Automated security updates configured

#### Runtime Security
- [x] Non-root user execution (UID 1001)
- [x] Read-only root filesystem where possible
- [x] Health checks configured
- [x] Resource limits defined (CPU, memory)
- [ ] Security profiles applied (AppArmor/SELinux)
- [ ] Capabilities dropped (drop all, add only necessary)
- [ ] Seccomp profiles configured

#### Network Security
- [x] Isolated bridge network (taskapp_network)
- [x] Only necessary ports exposed (3000, 5000, 5432)
- [x] CORS properly configured
- [ ] TLS/SSL encryption for external communication
- [ ] Network policies implemented
- [ ] Rate limiting enabled
- [ ] DDoS protection configured

### ✅ Application Security

#### Authentication & Authorization
- [x] JWT token-based authentication
- [x] Secure password hashing (bcrypt)
- [x] Environment-based secret management
- [ ] Token expiration enforced (1 hour access, 7 days refresh)
- [ ] Multi-factor authentication (MFA) support
- [ ] Session management with Redis
- [ ] Role-based access control (RBAC)

#### Data Security
- [x] PostgreSQL with password authentication
- [x] Database user with limited privileges
- [ ] Database encryption at rest
- [ ] Encrypted backups
- [ ] Data retention policies
- [ ] Audit logging enabled
- [ ] GDPR compliance measures

#### API Security
- [x] CORS configuration
- [ ] API rate limiting (per user/IP)
- [ ] Input validation and sanitization
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection headers
- [ ] CSRF protection
- [ ] Request size limits
- [ ] API versioning

### ✅ Infrastructure Security

#### Secrets Management
- [x] Secrets in .env file (not in code)
- [x] .env file in .gitignore
- [x] Strong random key generation documented
- [ ] Docker secrets or external vault
- [ ] Automated secret rotation
- [ ] Encrypted secret storage
- [ ] Audit trail for secret access

#### Access Control
- [ ] SSH key-based authentication
- [ ] Firewall rules configured
- [ ] VPN for production access
- [ ] Principle of least privilege
- [ ] Regular access reviews
- [ ] Disabled root login
- [ ] Failed login attempt monitoring

#### Monitoring & Logging
- [x] Application health checks
- [x] Container log aggregation
- [ ] Centralized logging (ELK/Loki)
- [ ] Security event monitoring
- [ ] Intrusion detection system
- [ ] Log retention policies
- [ ] Alerting for suspicious activity

### ✅ Configuration Security

#### Environment Variables
- [x] No default/weak passwords in production
- [x] Unique SECRET_KEY and JWT_SECRET_KEY
- [x] FLASK_DEBUG=False in production
- [x] NODE_ENV=production
- [x] Proper CORS origins
- [ ] All sensitive data encrypted
- [ ] Environment-specific configs

#### File Permissions
- [x] .dockerignore prevents sensitive file inclusion
- [ ] Proper file ownership in containers
- [ ] Restricted permissions on config files
- [ ] No world-readable secrets

### ✅ Build & Deployment

#### CI/CD Security
- [ ] Automated security scanning in pipeline
- [ ] Code quality gates
- [ ] Dependency vulnerability checks
- [ ] Container image scanning
- [ ] Signed commits
- [ ] Protected branches
- [ ] Approval workflows

#### Container Registry
- [x] Images pushed to Docker Hub
- [ ] Private registry for production
- [ ] Registry access controls
- [ ] Image retention policies
- [ ] Vulnerability scanning on push
- [ ] Image signing verification

## Security Implementation Guide

### 1. Generate Secure Keys

```bash
# Generate 256-bit (64 hex characters) secrets
python -c "import secrets; print(secrets.token_hex(32))"
```

**Requirements**:
- Minimum 64 characters hexadecimal
- Different keys for SECRET_KEY and JWT_SECRET_KEY
- Never reuse across environments
- Rotate every 90 days

### 2. Configure Non-Root Users

**Backend** (already implemented):
```dockerfile
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1001 -m -s /bin/bash appuser
USER appuser
```

**Frontend** (already implemented):
```dockerfile
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
USER nextjs
```

### 3. Set Resource Limits

**In docker-compose.prod.yml** (already implemented):
```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### 4. Enable Security Headers

**Flask (backend/app/__init__.py)**:
```python
from flask_talisman import Talisman

# Add to create_app() function
Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    content_security_policy={
        'default-src': "'self'",
        'img-src': '*',
        'script-src': "'self' 'unsafe-inline'",
    }
)
```

**Next.js (frontend/next.config.js)**:
```javascript
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        {
          key: 'X-Frame-Options',
          value: 'DENY',
        },
        {
          key: 'X-Content-Type-Options',
          value: 'nosniff',
        },
        {
          key: 'X-XSS-Protection',
          value: '1; mode=block',
        },
        {
          key: 'Referrer-Policy',
          value: 'strict-origin-when-cross-origin',
        },
      ],
    },
  ]
}
```

### 5. Implement Rate Limiting

**Install Flask-Limiter**:
```bash
pip install Flask-Limiter
```

**Configure (backend/app/__init__.py)**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass
```

### 6. Database Security

**Create limited privilege user**:
```sql
-- Create application user with limited privileges
CREATE USER taskapp_api WITH PASSWORD 'strong_password_here';

-- Grant only necessary privileges
GRANT CONNECT ON DATABASE taskmanagement_db TO taskapp_api;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO taskapp_api;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO taskapp_api;

-- Revoke superuser
REVOKE CREATE ON SCHEMA public FROM taskapp_api;
```

**Enable SSL connections**:
```bash
# In .env
DATABASE_URL=postgresql://user:pass@db:5432/dbname?sslmode=require
```

### 7. Container Hardening

**Read-only root filesystem**:
```yaml
# docker-compose.prod.yml
backend:
  read_only: true
  tmpfs:
    - /tmp
    - /app/logs
```

**Drop capabilities**:
```yaml
backend:
  cap_drop:
    - ALL
  cap_add:
    - NET_BIND_SERVICE  # Only if binding to port <1024
```

**Security options**:
```yaml
backend:
  security_opt:
    - no-new-privileges:true
    - apparmor=docker-default
```

### 8. Vulnerability Scanning

**Using Trivy** (recommended):
```bash
# Install Trivy
brew install aquasecurity/trivy/trivy  # macOS
# or
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh

# Scan images
trivy image veekay8/task-management-backend:1.0.0
trivy image veekay8/task-management-frontend:1.0.0

# Scan with severity threshold
trivy image --severity HIGH,CRITICAL veekay8/task-management-backend:1.0.0

# Generate report
trivy image --format json --output backend-scan.json veekay8/task-management-backend:1.0.0
```

**Using Snyk**:
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Scan Docker images
snyk container test veekay8/task-management-backend:1.0.0
snyk container test veekay8/task-management-frontend:1.0.0

# Monitor for ongoing vulnerabilities
snyk container monitor veekay8/task-management-backend:1.0.0
```

### 9. Network Security

**Firewall rules (UFW example)**:
```bash
# Default deny
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow 22/tcp

# Allow only necessary ports
ufw allow 80/tcp   # HTTP (will redirect to HTTPS)
ufw allow 443/tcp  # HTTPS

# Enable firewall
ufw enable
```

**Nginx reverse proxy with SSL**:
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Production Deployment Checklist

### Before Deployment
- [ ] All secrets rotated from defaults
- [ ] FLASK_DEBUG=False
- [ ] Strong passwords generated
- [ ] HTTPS/TLS configured
- [ ] Firewall rules configured
- [ ] Backup strategy in place
- [ ] Monitoring configured
- [ ] Vulnerability scan passed

### During Deployment
- [ ] Deploy to staging first
- [ ] Run integration tests
- [ ] Security scan passed
- [ ] Performance tests passed
- [ ] Rollback plan ready
- [ ] Team notified

### After Deployment
- [ ] Verify all services healthy
- [ ] Check logs for errors
- [ ] Monitor resource usage
- [ ] Verify backups working
- [ ] Test disaster recovery
- [ ] Document deployment

## Incident Response

### Security Breach Protocol
1. **Contain**: Isolate affected containers immediately
2. **Investigate**: Check logs, analyze breach vector
3. **Eradicate**: Remove malicious code/access
4. **Recover**: Restore from clean backups
5. **Review**: Post-mortem, update security measures

### Emergency Contacts
- Security Team: security@yourdomain.com
- On-call Engineer: oncall@yourdomain.com
- Infrastructure: infra@yourdomain.com

## Compliance

### GDPR Considerations
- [ ] Data encryption at rest and in transit
- [ ] Right to be forgotten implemented
- [ ] Data export capability
- [ ] Privacy policy updated
- [ ] Consent management
- [ ] Data retention policies

### SOC 2 Considerations
- [ ] Access logging
- [ ] Change management
- [ ] Incident response plan
- [ ] Regular security training
- [ ] Vendor risk assessment

## Regular Security Tasks

### Daily
- Monitor security alerts
- Review access logs
- Check system health

### Weekly
- Review failed login attempts
- Update dependencies
- Vulnerability scan

### Monthly
- Security patch deployment
- Access rights review
- Backup restoration test

### Quarterly
- Penetration testing
- Security audit
- Disaster recovery drill
- Secret rotation

### Annually
- Security policy review
- Compliance audit
- Security training
- Infrastructure review

## Tools & Resources

### Recommended Security Tools
- **Trivy**: Vulnerability scanner
- **Snyk**: Dependency scanning
- **OWASP ZAP**: Web application scanner
- **Falco**: Runtime security
- **Vault**: Secret management
- **Fail2ban**: Intrusion prevention

### Security Standards
- OWASP Top 10
- CIS Docker Benchmarks
- NIST Cybersecurity Framework
- PCI DSS (if handling payments)

### Learning Resources
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- Docker Security Best Practices: https://docs.docker.com/develop/security-best-practices/
- CIS Docker Benchmark: https://www.cisecurity.org/benchmark/docker

## Version History
- v1.0.0 (2026-01-02): Initial security checklist
