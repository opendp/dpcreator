# Sendgrid mail notes

## Initial Setup 

These steps assume:
 - A SendGrid account has been set up
 - An actual email address is available to use as the from email. (e.g. info@opendp.org)
   - This needs to be an actual working account  
 - A SendGrid API key has been created and verified

## Environment variables required

```
# Used by Django settings (read by base.py)
#
export ACCOUNT_EMAIL_VERIFICATION=mandatory
export SENDGRID_API_KEY=(add API key here)
export DEFAULT_FROM_EMAIL=info@opendp.org
```

For k8s deployment, these variables may be specified in the k8s YAML files, with the SENDGRID_API_KEY in a secrets file.

Expected secrets file/name for Azure deploy:
- **file**: `dpcreator-azure-secrets.yaml`
- **name**: `dpcreator-app-secrets`