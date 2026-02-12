# Archive Checklist

Use this checklist to archive temporary or sensitive artifacts created during the deployment.

- [ ] Remove temporary credentials files (e.g., azure/config/db-credentials-temp.txt)
- [ ] Remove any local export files containing secrets
- [ ] Ensure Key Vault is the source of truth for secrets
- [ ] Validate .gitignore covers Azure temp files
- [ ] Move final docs into azure/docs/

**Status**: Checklist created. Mark items complete after verification.
