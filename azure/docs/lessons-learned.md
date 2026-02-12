# Lessons Learned

## What Worked Well
- Container Apps simplified deployment and revision management.
- ACR integration made image distribution straightforward.
- Key Vault centralized secrets safely.

## What Was Challenging
- Regional availability constraints for PostgreSQL free tier.
- Networking and private access setup required careful NSG rules.
- CI/CD permissions needed precise RBAC configuration.

## Azure-Specific Features Used
- Container Apps (ingress + revisions)
- PostgreSQL Flexible Server
- Key Vault RBAC
- Log Analytics + Application Insights

## Differences vs AWS
- Azure Container Apps reduced orchestration overhead.
- Azure Portal UI is robust but can be slower to navigate.
- Cost Management tooling is strong and integrated.
