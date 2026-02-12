# Network Architecture Diagram

This diagram captures the VNet layout, subnets, and traffic boundaries.

```mermaid
flowchart TB
  internet[Internet]
  nsgCa[NSG - Container Apps\nAllow 80/443]
  nsgDb[NSG - Database\nAllow 5432 from CA subnet]

  subgraph vnet[VNet: vnet-taskapp (10.0.0.0/16)]
    subgraph caSubnet[Subnet: subnet-container-apps (10.0.1.0/24)]
      caEnv[Container Apps Environment\n(env-taskapp-prod)]
    end
    subgraph dbSubnet[Subnet: subnet-database (10.0.2.0/24)]
      pg[PostgreSQL Flexible Server]
    end
  end

  internet --> nsgCa --> caSubnet
  caSubnet --> nsgDb --> dbSubnet
```

## Security Boundaries

- **Database subnet** blocks all inbound except PostgreSQL from Container Apps subnet.
- **Container Apps subnet** allows public HTTP/HTTPS for frontend access.

## Notes

- DB has private access only.
- Public access is mediated by Container Apps ingress and custom domain.
