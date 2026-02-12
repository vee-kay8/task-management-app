# Azure Cost Breakdown

This document summarizes estimated and observed costs for the Azure deployment.

## Estimated Monthly Costs

| Resource | Estimated Cost | Notes |
|----------|----------------|------|
| PostgreSQL Flexible Server (B1ms) | $0 (free 12 months), then ~$15-20 | Burstable tier |
| Container Apps (2 apps, avg 1.5 replicas) | ~$20-25 | Consumption plan |
| Azure Container Registry (Basic) | ~$5 | Image storage |
| Key Vault | ~$0.12 | Secrets only |
| Log Analytics (30-day retention) | ~$5-10 | Log ingestion |
| Virtual Network | $0 | Free |
| Azure DNS (optional) | ~$0.50 | If used |
| **Total** | **~$30-40 (year 1)** | **~$45-60 after free tier** |

## Notes

- Costs vary with traffic and log volume.
- Review Cost Management weekly during the first month.

## CSV

A CSV version is available at azure/docs/cost-breakdown.csv.
