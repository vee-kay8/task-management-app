# Azure Architecture Diagram

This diagram shows the end-to-end Azure deployment for the Task Management Application.

```mermaid
flowchart LR
  user[User Browser]
  dns[Custom Domain\napp.techveesolutions.com]
  caFront[Container App\nFrontend]
  caBack[Container App\nBackend API]
  pg[Azure Database for PostgreSQL\nFlexible Server]
  acr[Azure Container Registry]
  kv[Azure Key Vault]
  la[Log Analytics + Azure Monitor]

  user --> dns --> caFront --> caBack --> pg
  caFront <-->|image pull| acr
  caBack <-->|image pull| acr
  caBack -->|secrets| kv
  caFront -->|logs| la
  caBack -->|logs| la
  pg -->|metrics| la
```

## Key Components

- **Container Apps**: Host frontend and backend services.
- **PostgreSQL Flexible Server**: Managed database.
- **ACR**: Stores backend and frontend images.
- **Key Vault**: Centralized secrets store.
- **Azure Monitor/Log Analytics**: Logs and metrics.

## Notes

- Container Apps use VNet integration for backend-to-database access.
- Public access is via custom domain with HTTPS.
