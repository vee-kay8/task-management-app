# ECS Task Definition - Environment Variables

**⚠️ IMPORTANT: This file contains sensitive information. DO NOT commit to Git!**

## Step 8: Environment Variables for Task Definition

Based on your backend configuration, here are the environment variables needed for the ECS task definition:

---

## Required Environment Variables

### 1. Flask Configuration
```
FLASK_ENV=production
DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

### 2. Secret Keys (Generated)
```
SECRET_KEY=FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0=
JWT_SECRET_KEY=IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4=
```

### 3. Database Connection
**✅ Password configured: Blessed99.**

```
DATABASE_URL=postgresql://postgres:Blessed99.@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement
```

Or as separate components (if your app uses them):
```
DB_HOST=taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=taskmanagement
DB_USER=postgres
DB_PASSWORD=Blessed99.
```

### 4. CORS Configuration
**Note: We'll update this after creating the ALB in Step 7**

For now, use wildcard (allows all origins):
```
CORS_ORIGINS=*
```

After ALB is created, update to:
```
CORS_ORIGINS=http://taskapp-alb-XXXXXXXXXX.us-east-1.elb.amazonaws.com
```

### 5. JWT Configuration
```
JWT_ACCESS_TOKEN_EXPIRES=24
```

### 6. Application Settings
```
APP_NAME=Task Management App
API_VERSION=v1
```

---

## Complete List for ECS Task Definition

**Copy these to your task definition in Step 9:**

```json
"environment": [
  {
    "name": "FLASK_ENV",
    "value": "production"
  },
  {
    "name": "DEBUG",
    "value": "False"
  },
  {
    "name": "SECRET_KEY",
    "value": "FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0="
  },
  {
    "name": "JWT_SECRET_KEY",
    "value": "IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4="
  },
  {
    "name": "DATABASE_URL",
    "value": "postgresql://postgres:Blessed99.@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement"
  },
  {
    "name": "CORS_ORIGINS",
    "value": "*"
  },
  {
    "name": "JWT_ACCESS_TOKEN_EXPIRES",
    "value": "24"
  }
]
```

---

## AWS Console Format

If using AWS Console to create task definition, add each variable individually:

| Name | Value |
|------|-------|
| FLASK_ENV | production |
| DEBUG | False |
| SECRET_KEY | FaKgFvIjFU3tz6bAugmkRw6CQfoaJuqAbJe/PYlyyu0= |
| JWT_SECRET_KEY | IB8fu3yhS/mPgIRmP6CsBab//X7Hnm+VggOHqXnB/F4= |
| DATABASE_URL | postgresql://postgres:Blessed99.@taskapp-db.cqaewjp43tdm.us-east-1.rds.amazonaws.com:5432/taskmanagement |
| CORS_ORIGINS | * |
| JWT_ACCESS_TOKEN_EXPIRES | 24 |

---

## Next Steps

1. ✅ **Database password confirmed**: Blessed99. (from .env.aws)

2. ✅ **All environment variables ready** for task definition

3. **Use these values in Step 9** when creating the task definition

4. **After ALB is created**, update CORS_ORIGINS with the actual ALB DNS name

---

## Security Best Practices

✅ **DO:**
- Keep this file local only
- Add to `.gitignore`
- Use AWS Secrets Manager for production (Phase 11)
- Rotate secrets periodically

❌ **DON'T:**
- Commit secrets to Git
- Share secrets in plain text
- Use the same secrets across environments
- Hard-code secrets in application code

---

## For AWS Secrets Manager (Future Enhancement)

In a production environment, you should store sensitive values in AWS Secrets Manager and reference them in the task definition:

```json
"secrets": [
  {
    "name": "DATABASE_URL",
    "valueFrom": "arn:aws:secretsmanager:us-east-1:858448674350:secret:taskapp/database-XXXXX"
  }
]
```

We'll set this up in Phase 11 (Optimization & Best Practices).

---

**Created**: January 21, 2026  
**For**: AWS Phase 5 - Step 8  
**Status**: Ready for Step 9 (Task Definition)
