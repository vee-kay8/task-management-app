# Phase 12: Cost Optimization & Auto-Scaling - Complete Guide

**Estimated Time**: 2-3 hours  
**Prerequisites**: Phases 1-11 completed  
**Status**: ✅ Complete

---

## Overview

In this phase, you’ll optimize Azure costs and configure autoscaling for Container Apps. You’ll analyze current spend, set a budget with alerts, tune scaling rules, and apply retention policies to keep costs predictable.

**What You’ll Learn**:
- Azure Cost Management analysis and budgets
- Container Apps scaling rules and KEDA basics
- Scheduled scaling and scaling safeguards
- Log Analytics retention tuning
- ACR image retention policies

**What You’ll Build**:
- Autoscaling rules for backend and frontend
- Monthly budget alerts
- Cost optimization report
- Retention policies for logs and images

---

## Prerequisites Check

```bash
# Verify Container Apps
az containerapp list \
  --resource-group rg-taskapp-prod \
  --output table

# Verify Log Analytics Workspace (for Container Apps)
az monitor log-analytics workspace list \
  --resource-group rg-taskapp-prod \
  --output table

# Verify ACR
az acr list \
  --resource-group rg-taskapp-prod \
  --output table
```

---

## Step 1: Review Costs in Azure Portal

1. Open **Azure Portal → Cost Management + Billing**.
2. Filter by **Resource Group: rg-taskapp-prod**.
3. Export a **last 7 days** report.
4. Identify top cost drivers.

**Deliverable**: A short cost summary in `azure/docs/` (optional).

---

## Step 2: Create a Budget & Alerts

```bash
# Create a monthly budget ($100) with alert thresholds
az consumption budget create \
  --resource-group rg-taskapp-prod \
  --name taskapp-budget \
  --amount 100 \
  --time-grain Monthly \
  --time-period startDate=2026-02-01 endDate=2027-02-01 \
  --category cost \
  --notification {
      "enabled": true,
      "operator": "GreaterThan",
      "threshold": 80,
      "contactEmails": ["you@example.com"],
      "thresholdType": "Actual"
    } \
  --notification {
      "enabled": true,
      "operator": "GreaterThan",
      "threshold": 100,
      "contactEmails": ["you@example.com"],
      "thresholdType": "Forecasted"
    }
```

**Note**: Replace `you@example.com` with your email.

---

## Step 3: Configure Container Apps Autoscaling

### Backend (HTTP concurrency)

```bash
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

### Frontend (HTTP concurrency)

```bash
az containerapp update \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --min-replicas 1 \
  --max-replicas 5 \
  --scale-rule-name http-rule \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

### Optional: CPU-based Scaling

```bash
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --scale-rule-name cpu-rule \
  --scale-rule-type cpu \
  --scale-rule-metadata "type=Utilization" "value=70"
```

---

## Step 4: Set Log Analytics Retention

```bash
# Set retention to 30 days
az monitor log-analytics workspace update \
  --resource-group rg-taskapp-prod \
  --workspace-name <LOG_ANALYTICS_WORKSPACE> \
  --retention-time 30
```

Replace `<LOG_ANALYTICS_WORKSPACE>` with your workspace name.

---

## Step 5: Configure ACR Retention Policy

```bash
# Enable retention policy (keep last 20 images)
az acr config retention update \
  --registry taskappacr2026 \
  --status enabled \
  --days 30
```

**Recommendation**: Keep a stable tag (e.g., `prod`) and prune untagged images.

---

## Step 6: Optional Scheduled Scaling

Use scheduled scaling if traffic is predictable.

```bash
# Example: scale down at night (manual change)
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --min-replicas 0 \
  --max-replicas 2
```

---

## Verification Checklist

- [ ] Cost report reviewed and saved
- [ ] Budget created with alerts at 80% and 100%
- [ ] Backend autoscaling configured
- [ ] Frontend autoscaling configured
- [ ] Log Analytics retention set to 30 days
- [ ] ACR retention policy enabled
- [ ] App stable under load

---

## Troubleshooting

### Issue: Budget create fails
**Fix**: Ensure billing access and correct subscription scope.

### Issue: Container App update fails
**Fix**: Confirm app names: `ca-taskapp-backend`, `ca-taskapp-frontend`.

### Issue: Log Analytics update fails
**Fix**: Verify workspace name and permissions.

---

## Best Practices

1. Keep min replicas at 1 for production to avoid cold starts
2. Start with HTTP concurrency rules, add CPU/memory later
3. Review costs weekly during learning phase
4. Use retention policies to prevent runaway storage costs

---

## Cost Estimate (Optimized)

- PostgreSQL (Burstable B1ms): $0 (free 12 months), then ~$15-20
- Container Apps (avg 1.5 replicas): ~$20-25
- ACR (Basic): ~$5
- Key Vault: ~$0.12
- Log Analytics (30 days): ~$5-10

**Estimated Total**: ~$30-40/month (first year)

---

## Next Steps

After completing Phase 12:

1. Record completion in `AZURE_PROGRESS.md`
2. Proceed to Phase 13: Final Documentation & Comparison

---

## Resources

- [Azure Cost Management](https://learn.microsoft.com/en-us/azure/cost-management-billing/costs/)
- [Azure Container Apps Scaling](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [ACR Retention Policy](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-retention-policy)

---

**Phase 12 Status**: Complete ✅  
**Estimated Completion Time**: 2-3 hours  
**Next Phase**: Phase 13 - Final Documentation & Comparison
