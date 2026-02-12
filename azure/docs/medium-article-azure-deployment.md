# Deploying a Full Stack Task Manager to Azure: A Practical, Beginner Friendly Guide

## Introduction

This article documents a real, end to end deployment of a full stack task management application to Microsoft Azure. It is written for developers who want a clear path from local development to a production ready setup in the cloud. The goal is to keep the language simple, the steps concrete, and the lessons easy to apply to other projects.

The application stack is straightforward and popular:

- Frontend: Next.js with TypeScript
- Backend: Flask with SQLAlchemy
- Database: PostgreSQL
- Infrastructure: Azure Container Apps, Azure Container Registry, Azure Database for PostgreSQL, and Azure Key Vault

By the end, you will see how the system is designed, how it is deployed, what it costs, and what to watch out for.

---

## The Deployment Architecture in Plain Language

The architecture has four core services and a few support services:

1. **Container Apps** runs the frontend and backend as managed containers.
2. **Azure Container Registry** stores Docker images for both services.
3. **PostgreSQL Flexible Server** hosts the database in a private subnet.
4. **Key Vault** stores secrets like database credentials and JWT keys.

Supporting services include:

- **Virtual Network** for private database access
- **Log Analytics and Azure Monitor** for logging and metrics
- **Azure DNS** for custom domain routing

The frontend is public, the backend is public, and the database is private. The backend talks to the database over the VNet and uses secrets stored in Key Vault.

---

## Why Azure Container Apps

For small to medium applications, Azure Container Apps is a good fit. You get:

- Simple deployment model
- Built in ingress and HTTPS
- Auto scaling with KEDA
- Easy integration with Azure Container Registry

It gives most of the benefits of Kubernetes without the operational overhead.

---

## Step 1: Prepare the Azure Foundation

The foundation includes:

- Resource group
- Virtual network
- Subnets for Container Apps and database
- Network security groups

The key decision is keeping the database private. Only the Container Apps subnet can reach it on port 5432. Everything else is blocked by default.

---

## Step 2: Create the Database

Use PostgreSQL Flexible Server with a low cost burstable tier during learning or early production. Connect it to the database subnet and disable public access.

Important detail: when the database is private, you cannot easily connect from your local machine. The application migrations are the clean way to initialize the schema.

---

## Step 3: Create the Container Registry

Build and push Docker images for both services:

- taskapp-backend
- taskapp-frontend

Use versioned tags for repeatable deployments and a latest tag for convenience. This makes rollback easy if a deployment fails.

---

## Step 4: Store Secrets Safely

Key Vault is used for:

- Database host
- Database name
- Database user
- Database password
- JWT secret key

This keeps the repository clean and avoids leaking credentials into environment files or build pipelines.

---

## Step 5: Deploy the Backend and Frontend

Both services are deployed as Container Apps with:

- Public ingress
- HTTPS enabled
- Images pulled from ACR
- Environment variables configured from secrets

Once deployed, each app has a stable public URL. The frontend uses the backend URL for API calls.

---

## Step 6: Configure Domain and TLS

With Container Apps, you can bind a custom domain and enable TLS. Azure issues and manages the certificate. After DNS records are created, you get HTTPS with no extra work.

---

## Step 7: Observability and Alerts

Logging and metrics are essential for production behavior. The setup includes:

- Log Analytics workspace
- Azure Monitor alerts
- Custom queries for error rates and container restarts

This makes it easy to track failures and performance issues early.

---

## Step 8: Infrastructure as Code

Bicep templates were created for:

- Resource group
- Network
- Database
- Container registry
- Container apps
- Monitoring

Even if you already have a running environment, the templates make it easier to rebuild and share the infrastructure.

---

## Step 9: CI and CD with GitHub Actions

Two workflows were created:

- Backend deployment
- Frontend deployment

Each workflow:

1. Logs into Azure
2. Builds a Docker image
3. Pushes it to ACR
4. Updates the Container App

This enables push to deploy and keeps the process consistent.

---

## Step 10: Cost and Scaling

Scaling is configured based on HTTP concurrency. Basic rules are usually enough:

- Minimum replicas: 1
- Maximum replicas: 5
- HTTP concurrency rule: 100

Cost estimates for this setup are reasonable for a learning project or small production workload. The biggest variable is log ingestion volume.

---

## What the Final System Looks Like

At the end, the system is stable and production friendly:

- Public frontend and backend
- Private database
- Secrets in Key Vault
- Continuous deployment
- Logs and monitoring
- Cost controls and scaling

---

## Lessons Learned

Here are the key takeaways from the build:

1. Private networking adds complexity but improves security.
2. Container Apps removes a lot of operational friction.
3. Clear naming conventions save time in the Azure Portal.
4. CI and CD needs clean RBAC permissions to work reliably.
5. A small amount of documentation pays off later.

---

## Azure vs AWS Snapshot

From a cost perspective, Azure was cheaper for this workload. The difference was most noticeable in managed database and container hosting. The trade off is that some Azure free tier resources have regional availability limits.

Both platforms are capable. For a team already using GitHub and looking for fast container deployment, Azure Container Apps is a strong option.

---

## Closing Thoughts

This deployment shows that you can run a modern full stack app on Azure without heavy infrastructure complexity. The biggest wins are simplicity, built in scaling, and good cost control.

If you want to replicate the process, start with a clear roadmap, automate what you can, and keep your documentation close to the work. It will save you time later.

---

## References

- Azure Container Apps documentation
- Azure Database for PostgreSQL documentation
- Azure Container Registry documentation
- Azure Key Vault documentation
- GitHub Actions for Azure documentation
