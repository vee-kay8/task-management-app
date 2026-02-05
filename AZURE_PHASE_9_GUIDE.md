# Phase 9: Monitoring & Logging - Azure Monitor Setup

**Estimated Time**: 3-4 hours  
**Prerequisites**: Phases 1-8 completed  
**Status**: Not Started

---

## Overview

In this phase, you'll set up comprehensive monitoring and logging for your Azure Container Apps application. You'll configure Azure Monitor, Application Insights, Log Analytics, and create custom dashboards and alerts.

**What You'll Learn**:
- Azure Monitor architecture and components
- Log Analytics workspace and KQL queries
- Application Insights for application performance monitoring (APM)
- Custom dashboards and visualizations
- Alert rules and action groups
- Cost monitoring and optimization

**What You'll Build**:
- Application Insights for backend and frontend
- Log Analytics queries for troubleshooting
- Custom Azure Dashboard
- Alert rules for critical metrics
- Email notifications for incidents

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Azure Monitor                          │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ Application     │  │ Log Analytics    │  │  Metrics   │ │
│  │ Insights        │  │ Workspace        │  │  Explorer  │ │
│  └─────────────────┘  └──────────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────┘
           ▲                    ▲                    ▲
           │                    │                    │
    ┌──────┴─────┐      ┌──────┴─────┐      ┌──────┴─────┐
    │  Frontend  │      │  Backend   │      │  Database  │
    │ Container  │      │ Container  │      │ PostgreSQL │
    │    App     │      │    App     │      │   Server   │
    └────────────┘      └────────────┘      └────────────┘
```

**Components**:
- **Application Insights**: Application performance monitoring (APM) for code-level insights
- **Log Analytics Workspace**: Centralized log storage and querying (already created in Phase 6)
- **Azure Monitor Metrics**: Time-series metrics for resources
- **Dashboards**: Visual representation of metrics and logs
- **Alerts**: Automated notifications based on conditions

---

## Prerequisites Check

Before starting, verify you have:

```bash
# Check Log Analytics workspace (should exist from Phase 6)
az monitor log-analytics workspace list \
  --resource-group rg-taskapp-prod \
  --output table

# Check Container Apps (should show both frontend and backend)
az containerapp list \
  --resource-group rg-taskapp-prod \
  --output table

# Verify your custom domain is working
curl -I https://app.techveesolutions.com
```

**Expected**:
- Log Analytics workspace exists (created automatically with Container Apps Environment)
- Both container apps are running
- Custom domain returns HTTP 200 or redirects

---

## Step 1: Enable Application Insights for Backend

### 1.1 Create Application Insights Resource

```bash
# Create Application Insights for backend
az monitor app-insights component create \
  --app appinsights-taskapp-backend \
  --location centralus \
  --resource-group rg-taskapp-prod \
  --workspace $(az monitor log-analytics workspace show \
    --resource-group rg-taskapp-prod \
    --workspace-name $(az monitor log-analytics workspace list \
      --resource-group rg-taskapp-prod \
      --query "[0].name" -o tsv) \
    --query id -o tsv)
```

**What this does**:
- Creates an Application Insights resource
- Links it to your existing Log Analytics workspace
- Provides a workspace for application-level telemetry

### 1.2 Get Application Insights Connection String

```bash
# Get the connection string (you'll need this)
az monitor app-insights component show \
  --app appinsights-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query connectionString -o tsv
```

**Save this output** - you'll add it to your backend container app.

### 1.3 Install Application Insights SDK in Backend

**Edit `backend/requirements.txt`** and add:

```txt
opencensus-ext-azure==1.1.13
opencensus-ext-flask==0.8.0
```

**Edit `backend/app/__init__.py`** to add Application Insights:

```python
import os
from flask import Flask
from flask_cors import CORS
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
import logging

def create_app():
    app = Flask(__name__)
    
    # Existing configuration...
    app.config.from_object('app.config.Config')
    
    # CORS configuration
    CORS(app, resources={
        r"/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Application Insights setup
    app_insights_conn = os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if app_insights_conn:
        # Add Azure Log Handler
        logger = logging.getLogger(__name__)
        logger.addHandler(AzureLogHandler(connection_string=app_insights_conn))
        logger.setLevel(logging.INFO)
        
        # Add Flask middleware for request tracking
        FlaskMiddleware(
            app,
            exporter=AzureLogHandler(connection_string=app_insights_conn)
        )
        
        app.logger.info("Application Insights enabled")
    
    # Rest of your initialization...
    from app.routes import auth, users, projects, tasks
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(projects.bp)
    app.register_blueprint(tasks.bp)
    
    return app
```

### 1.4 Rebuild and Push Backend Image

```bash
# Navigate to project root
cd /c/Users/vokeo/OneDrive/Desktop/task-management-app

# Build new backend image
docker build -t taskappacr2026.azurecr.io/taskapp-backend:v2 ./backend

# Push to ACR
az acr login --name taskappacr2026
docker push taskappacr2026.azurecr.io/taskapp-backend:v2
```

### 1.5 Update Backend Container App with App Insights

```bash
# Add connection string to Key Vault first
APPINSIGHTS_CONN_STRING="<paste-connection-string-from-step-1.2>"

az keyvault secret set \
  --vault-name kv-taskapp-prod-88 \
  --name appinsights-connection-string \
  --value "$APPINSIGHTS_CONN_STRING"

# Update backend container app with new image and environment variable
az containerapp update \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --image taskappacr2026.azurecr.io/taskapp-backend:v2 \
  --set-env-vars "APPLICATIONINSIGHTS_CONNECTION_STRING=secretref:appinsights-connection-string"
```

### 1.6 Verify Backend Telemetry

Wait 2-3 minutes, then check Application Insights:

```bash
# Open Application Insights in browser
az monitor app-insights component show \
  --app appinsights-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query id -o tsv | \
  xargs -I {} echo "https://portal.azure.com/#@/resource{}/overview"
```

Or navigate manually:
1. Go to **Azure Portal** → **Resource Groups** → **rg-taskapp-prod**
2. Click **appinsights-taskapp-backend**
3. Click **Live Metrics** to see real-time data
4. Make some API requests to generate telemetry

---

## Step 2: Enable Application Insights for Frontend

### 2.1 Create Application Insights for Frontend

```bash
# Create Application Insights for frontend
az monitor app-insights component create \
  --app appinsights-taskapp-frontend \
  --location centralus \
  --resource-group rg-taskapp-prod \
  --workspace $(az monitor log-analytics workspace show \
    --resource-group rg-taskapp-prod \
    --workspace-name $(az monitor log-analytics workspace list \
      --resource-group rg-taskapp-prod \
      --query "[0].name" -o tsv) \
    --query id -o tsv)

# Get the connection string
az monitor app-insights component show \
  --app appinsights-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --query connectionString -o tsv
```

### 2.2 Install Application Insights SDK in Frontend

**Edit `frontend/package.json`** and add:

```json
{
  "dependencies": {
    "@microsoft/applicationinsights-web": "^3.0.8",
    // ... other dependencies
  }
}
```

**Create `frontend/lib/appInsights.ts`**:

```typescript
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

let appInsights: ApplicationInsights | null = null;

export const initAppInsights = () => {
  const connectionString = process.env.NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING;
  
  if (!connectionString) {
    console.warn('Application Insights connection string not found');
    return;
  }

  if (!appInsights) {
    appInsights = new ApplicationInsights({
      config: {
        connectionString: connectionString,
        enableAutoRouteTracking: true,
        enableCorsCorrelation: true,
        enableRequestHeaderTracking: true,
        enableResponseHeaderTracking: true,
      }
    });
    
    appInsights.loadAppInsights();
    appInsights.trackPageView();
  }

  return appInsights;
};

export const trackEvent = (name: string, properties?: { [key: string]: any }) => {
  if (appInsights) {
    appInsights.trackEvent({ name }, properties);
  }
};

export const trackException = (error: Error, severityLevel?: number) => {
  if (appInsights) {
    appInsights.trackException({ exception: error, severityLevel });
  }
};

export default appInsights;
```

**Edit `frontend/app/layout.tsx`** to initialize App Insights:

```typescript
'use client';

import { useEffect } from 'react';
import { initAppInsights } from '@/lib/appInsights';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    // Initialize Application Insights on client side
    initAppInsights();
  }, []);

  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  );
}
```

### 2.3 Rebuild and Push Frontend Image

```bash
# Build frontend with App Insights connection string
APPINSIGHTS_FRONTEND_CONN="<paste-frontend-connection-string>"

docker build \
  --build-arg NEXT_PUBLIC_API_URL=https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io \
  --build-arg NEXT_PUBLIC_APPINSIGHTS_CONNECTION_STRING="$APPINSIGHTS_FRONTEND_CONN" \
  -t taskappacr2026.azurecr.io/taskapp-frontend:v2 \
  ./frontend

# Push to ACR
docker push taskappacr2026.azurecr.io/taskapp-frontend:v2
```

### 2.4 Update Frontend Container App

```bash
az containerapp update \
  --name ca-taskapp-frontend \
  --resource-group rg-taskapp-prod \
  --image taskappacr2026.azurecr.io/taskapp-frontend:v2
```

---

## Step 3: Create Log Analytics Queries

### 3.1 Find Your Log Analytics Workspace

```bash
# Get workspace ID
WORKSPACE_ID=$(az monitor log-analytics workspace list \
  --resource-group rg-taskapp-prod \
  --query "[0].customerId" -o tsv)

echo "Workspace ID: $WORKSPACE_ID"

# Get workspace name
WORKSPACE_NAME=$(az monitor log-analytics workspace list \
  --resource-group rg-taskapp-prod \
  --query "[0].name" -o tsv)

echo "Workspace Name: $WORKSPACE_NAME"
```

### 3.2 Open Log Analytics and Create Queries

Navigate to **Azure Portal** → **Log Analytics workspaces** → **[your-workspace]** → **Logs**

#### Query 1: Recent Application Errors (Last 24 Hours)

```kql
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(24h)
| where Log_s contains "ERROR" or Log_s contains "error" or Log_s contains "Error"
| project TimeGenerated, ContainerAppName_s, ContainerName_s, Log_s
| order by TimeGenerated desc
| take 100
```

**Save this query** as "Application Errors - 24h"

#### Query 2: API Response Times

```kql
AppRequests
| where TimeGenerated > ago(1h)
| summarize 
    AvgDuration = avg(DurationMs),
    P50 = percentile(DurationMs, 50),
    P95 = percentile(DurationMs, 95),
    P99 = percentile(DurationMs, 99),
    RequestCount = count()
    by bin(TimeGenerated, 5m), Name
| order by TimeGenerated desc
```

**Save this query** as "API Response Times"

#### Query 3: Failed Login Attempts

```kql
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(7d)
| where Log_s contains "login" or Log_s contains "authentication"
| where Log_s contains "failed" or Log_s contains "error" or Log_s contains "invalid"
| project TimeGenerated, Log_s
| order by TimeGenerated desc
```

**Save this query** as "Failed Login Attempts"

#### Query 4: Container Restarts

```kql
ContainerAppSystemLogs_CL
| where TimeGenerated > ago(24h)
| where Log_s contains "restart" or Log_s contains "started" or Log_s contains "stopped"
| project TimeGenerated, ContainerAppName_s, ContainerName_s, Log_s
| order by TimeGenerated desc
```

**Save this query** as "Container Restarts"

#### Query 5: Database Connection Errors

```kql
ContainerAppConsoleLogs_CL
| where TimeGenerated > ago(24h)
| where Log_s contains "database" or Log_s contains "postgres" or Log_s contains "psycopg2"
| where Log_s contains "error" or Log_s contains "ERROR" or Log_s contains "failed"
| project TimeGenerated, ContainerAppName_s, Log_s
| order by TimeGenerated desc
```

**Save this query** as "Database Connection Errors"

---

## Step 4: Create Azure Dashboard

### 4.1 Create Dashboard from Azure Portal

1. Navigate to **Azure Portal** → **Dashboard**
2. Click **+ Create** → **Custom**
3. Name it: **Task Management App - Production**

### 4.2 Add Tiles to Dashboard

**Tile 1: Container Apps Overview**
- Click **+ Add tile**
- Select **Resource group**
- Configure: Select `rg-taskapp-prod`
- Position: Top left

**Tile 2: Backend Response Time**
- Click **+ Add tile**
- Select **Metrics chart**
- Configure:
  - Resource: `ca-taskapp-backend`
  - Metric: `Requests` or `CPU Usage`
  - Aggregation: Average
  - Time range: Last 24 hours

**Tile 3: Frontend Response Time**
- Same as above, but select `ca-taskapp-frontend`

**Tile 4: Database Connections**
- Add **Metrics chart**
- Resource: `taskapp-db-88`
- Metric: `Active Connections`
- Aggregation: Average

**Tile 5: Recent Errors (from Log Analytics)**
- Click **+ Add tile**
- Select **Logs**
- Paste the "Application Errors - 24h" query
- Set refresh to 5 minutes

**Tile 6: Request Count**
- Add **Metrics chart**
- Resource: `ca-taskapp-backend`
- Metric: `Requests`
- Aggregation: Sum
- Chart type: Bar or Line

### 4.3 Save Dashboard

Click **Done customizing** and save.

---

## Step 5: Create Alert Rules

### 5.1 Create Action Group for Email Notifications

```bash
# Create action group for email alerts
az monitor action-group create \
  --name ag-taskapp-alerts \
  --resource-group rg-taskapp-prod \
  --short-name taskapp \
  --email-receiver \
    name=admin \
    email-address=vokeogigbah@yahoo.com
```

### 5.2 Create Alert: High CPU Usage (Backend)

```bash
# Get backend resource ID
BACKEND_ID=$(az containerapp show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query id -o tsv)

# Create CPU alert
az monitor metrics alert create \
  --name "Backend High CPU" \
  --resource-group rg-taskapp-prod \
  --scopes $BACKEND_ID \
  --condition "avg UsageNanoCores > 800000000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action ag-taskapp-alerts \
  --severity 2 \
  --description "Backend CPU usage above 80%"
```

### 5.3 Create Alert: High Memory Usage (Backend)

```bash
az monitor metrics alert create \
  --name "Backend High Memory" \
  --resource-group rg-taskapp-prod \
  --scopes $BACKEND_ID \
  --condition "avg WorkingSetBytes > 900000000" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action ag-taskapp-alerts \
  --severity 2 \
  --description "Backend memory usage above 90% (900MB of 1GB)"
```

### 5.4 Create Alert: Container App Down (No Replicas)

```bash
az monitor metrics alert create \
  --name "Backend Container App Down" \
  --resource-group rg-taskapp-prod \
  --scopes $BACKEND_ID \
  --condition "avg Replicas == 0" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action ag-taskapp-alerts \
  --severity 0 \
  --description "Backend container app has no running replicas"
```

### 5.5 Create Alert: High Error Rate (Log-based)

```bash
# Create log-based alert for errors
az monitor scheduled-query create \
  --name "High Error Rate" \
  --resource-group rg-taskapp-prod \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/rg-taskapp-prod/providers/Microsoft.OperationalInsights/workspaces/$WORKSPACE_NAME \
  --condition "count > 10" \
  --condition-query "ContainerAppConsoleLogs_CL | where TimeGenerated > ago(5m) | where Log_s contains 'ERROR' | summarize count()" \
  --description "More than 10 errors in 5 minutes" \
  --evaluation-frequency 5m \
  --window-size 5m \
  --severity 1 \
  --action-groups $(az monitor action-group show --name ag-taskapp-alerts --resource-group rg-taskapp-prod --query id -o tsv)
```

### 5.6 Create Alert: Database Connection Failures

```bash
# Get database resource ID
DB_ID=$(az postgres flexible-server show \
  --name taskapp-db-88 \
  --resource-group rg-taskapp-prod \
  --query id -o tsv)

# Create alert for failed connections
az monitor metrics alert create \
  --name "Database Connection Failures" \
  --resource-group rg-taskapp-prod \
  --scopes $DB_ID \
  --condition "total failed_connections > 5" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --action ag-taskapp-alerts \
  --severity 1 \
  --description "More than 5 failed database connections in 5 minutes"
```

---

## Step 6: Enable Container Apps Insights (Built-in)

Container Apps has built-in monitoring. Let's verify it's enabled:

```bash
# Check Container Apps environment monitoring
az containerapp env show \
  --name env-taskapp-prod \
  --resource-group rg-taskapp-prod \
  --query "properties.appLogsConfiguration" -o json
```

**Expected output**: Should show Log Analytics workspace configuration.

---

## Step 7: Test Monitoring & Alerts

### 7.1 Generate Test Load

**Test API endpoints**:

```bash
# Test backend health
for i in {1..50}; do
  curl https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io/health
  sleep 1
done

# Test login (will create some activity)
curl -X POST https://ca-taskapp-backend.redtree-99ec4a5a.centralus.azurecontainerapps.io/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"wrongpassword"}'
```

### 7.2 Check Application Insights

1. Navigate to **Application Insights** → **appinsights-taskapp-backend**
2. Click **Live Metrics** - you should see live requests
3. Click **Performance** - view response times
4. Click **Failures** - view any failed requests

### 7.3 Check Log Analytics

1. Navigate to **Log Analytics workspace**
2. Click **Logs**
3. Run one of your saved queries
4. Verify logs appear

### 7.4 Test Alert

Verify email notifications work:
1. Check your email (vokeogigbah@yahoo.com)
2. You should have received a test email from Azure Monitor
3. Confirm the action group is active

---

## Step 8: Create Custom Metrics (Optional)

### 8.1 Add Custom Metrics to Backend Code

**Edit `backend/app/routes/auth.py`** (or any route):

```python
from opencensus.stats import aggregation, measure, view
from opencensus.ext.azure import metrics_exporter
import time

# Define custom metrics
login_attempts_measure = measure.MeasureInt("login_attempts", "Number of login attempts", "1")
login_success_measure = measure.MeasureInt("login_success", "Number of successful logins", "1")

# Track in your login route
@bp.route('/login', methods=['POST'])
def login():
    start_time = time.time()
    
    try:
        # Your existing login logic...
        
        # Track successful login
        # (Add after successful authentication)
        
        response_time = time.time() - start_time
        return jsonify({"token": token}), 200
        
    except Exception as e:
        # Track failed login
        return jsonify({"error": str(e)}), 401
```

---

## Step 9: Document Your Monitoring Setup

Create a monitoring runbook in `azure/docs/monitoring-runbook.md`:

```markdown
# Monitoring & Alerting Runbook

## Application Insights
- **Backend**: appinsights-taskapp-backend
- **Frontend**: appinsights-taskapp-frontend

## Log Analytics Workspace
- **Name**: [workspace-name]
- **ID**: [workspace-id]

## Saved Queries
1. Application Errors - 24h
2. API Response Times
3. Failed Login Attempts
4. Container Restarts
5. Database Connection Errors

## Alerts
1. Backend High CPU (>80%)
2. Backend High Memory (>90%)
3. Backend Container App Down
4. High Error Rate (>10 errors/5min)
5. Database Connection Failures (>5/5min)

## Alert Recipients
- admin: vokeogigbah@yahoo.com

## Dashboard
- **Name**: Task Management App - Production
- **URL**: [dashboard-url]

## Troubleshooting

### No data in Application Insights
- Check connection string is correct
- Verify SDK is installed
- Check container logs for instrumentation errors

### Alerts not firing
- Verify action group email is confirmed
- Check alert rule conditions
- Review metric data in Metrics Explorer

### Logs not appearing
- Check Log Analytics workspace is connected
- Verify Container Apps environment configuration
- Wait 5-10 minutes for ingestion delay
```

---

## Verification Checklist

After completing Phase 9, verify:

- [ ] Application Insights enabled for backend
- [ ] Application Insights enabled for frontend
- [ ] Log Analytics queries created and saved
- [ ] Azure Dashboard created with key metrics
- [ ] Action group created for email notifications
- [ ] At least 5 alert rules configured
- [ ] Test alerts received via email
- [ ] Live metrics visible in Application Insights
- [ ] Logs visible in Log Analytics workspace
- [ ] Documentation created for monitoring setup

---

## Troubleshooting

### Issue: No telemetry data in Application Insights

**Solution**:
```bash
# Check container app environment variables
az containerapp show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --query "properties.template.containers[0].env" -o json

# Check logs for errors
az containerapp logs show \
  --name ca-taskapp-backend \
  --resource-group rg-taskapp-prod \
  --follow
```

### Issue: Alert emails not arriving

**Solution**:
```bash
# Verify action group
az monitor action-group show \
  --name ag-taskapp-alerts \
  --resource-group rg-taskapp-prod

# Check spam folder
# Confirm email address in action group settings
```

### Issue: Logs not appearing in workspace

**Cause**: Ingestion delay (5-10 minutes)

**Solution**: Wait and try again. Check:
```bash
# Verify Container Apps environment is connected to workspace
az containerapp env show \
  --name env-taskapp-prod \
  --resource-group rg-taskapp-prod \
  --query "properties.appLogsConfiguration"
```

---

## Cost Estimate

**Phase 9 Costs**:
- **Application Insights**: ~$2-5/month (5GB free ingestion, then $2.30/GB)
- **Log Analytics**: ~$3-8/month (5GB free, then $2.76/GB)
- **Alerts**: ~$0.10-0.50/month ($0.10 per alert rule)
- **Total Phase 9**: ~$5-15/month

**Cumulative Total** (Phases 1-9):
- **Database**: ~$12/month
- **Container Apps**: ~$20-30/month
- **Container Registry**: ~$5/month
- **Key Vault**: ~$0.03/month
- **Monitoring**: ~$5-15/month
- **Total**: ~$42-62/month

---

## Next Steps

After completing Phase 9:

1. **Save your progress** in `AZURE_PROGRESS.md`
2. **Test all monitoring features**
3. **Document any custom queries or alerts**
4. **Proceed to Phase 10**: Infrastructure as Code (Bicep)

**Phase 10 Preview**: Convert all your manually created resources into Bicep templates for repeatable deployments.

---

## Resources

- [Azure Monitor Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/)
- [Application Insights Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
- [Log Analytics Tutorial](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial)
- [KQL Query Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/)
- [Container Apps Monitoring](https://learn.microsoft.com/en-us/azure/container-apps/observability)

---

**Phase 9 Status**: Ready to begin ✅  
**Estimated Completion Time**: 3-4 hours  
**Next Phase**: Phase 10 - Infrastructure as Code (Bicep)
