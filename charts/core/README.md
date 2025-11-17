# Charts-Core

## External Secrets Operator (ESO)

This chart supports integration with External Secrets Operator for syncing secrets from Azure Key Vault.

### Prerequisites

ESO requires the following secrets to be defined in `secEnvVars`:
- `AZURE_CLIENT_ID` - Azure Service Principal Client ID
- `AZURE_CLIENT_SECRET` - Azure Service Principal Client Secret
- `AZURE_TENANT_ID` - Azure Tenant ID
- `KeyVault__Url` - Azure Key Vault URL (e.g., `https://your-keyvault.vault.azure.net/`)

### Configuration

To enable ESO, set the following in your `values.yaml`:

```yaml
global:
  eso:
    enabled: true
    refreshInterval: "1h"  # Optional: how often to sync secrets (default: 1h)
    findRegex: ".*"        # Optional: regex to filter secrets from Key Vault (default: .*)
    conversionStrategy: "Unicode"  # Optional: conversion strategy (default: Unicode)
  
  secEnvVars:
    AZURE_CLIENT_ID: '#{clientId}#'
    AZURE_CLIENT_SECRET: '#{clientSecret}#'
    AZURE_TENANT_ID: '#{azAccountTenantId}#'
    KeyVault__Url: 'https://#{keyVaultName}#.vault.azure.net/'
```

### Generated Resources

When ESO is enabled, the chart creates:
- **ClusterSecretStore**: `<release-name>-cluster-secret-store` - connects to Azure Key Vault
- **ExternalSecret**: `<release-name>-external-secret` - syncs secrets to `<release-name>-secure-kv`

The ESO will use the existing `<release-name>-secure` secret (created from `secEnvVars`) for authentication to Azure Key Vault.

# How to test locally
1. Install prerequisites as specified in tests requirements.txt
2. in charts\charts\core type "helm template ." make sure the template renders correctly
3. in charts\charts\core type "pytest" all tests should pass

# How to debug in VS code
https://code.visualstudio.com/docs/python/testing
test discovery in subfolders is based on existence of __init__.py file
to run tests succesfully you need to set test working directory go to File->Preferences->settings, search Tests, select Python and find "Optional working directory for tests." Set it to charts\core