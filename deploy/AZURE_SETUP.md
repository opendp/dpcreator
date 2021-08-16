# Setting up Kubernetes (K8s) on Azure

Note: These resources were created under a "Resource Group" named `DPCreator`

Through the Azure admin:
- Create a "Kubernetes Service" using these specs and default values for other attributes
  - **Node Size**: D2as_v4
  - **Node count**: 2  (Manually sized)
- Through the Admin, connect to the K8s service.

### Log In

- Use the Azure admin instructions to launch a web-based Cloud Shell and connect to the cluster
- Cluster name (suggestion): `dp-creator-cluster`

### Clone repository

```
# If needed, add this line to the end of the .bashrc file (w/o the "# "):
# alias kc="kubectl"

# Add deploy key to GitHub if needed.
# Assumes a key already exists
more .ssh/id_ed25519.pub
# Add key to https://github.com/opendp/dpcreator-deploy/settings/keys

# Clone repository (using SSH)
#git clone git@github.com:opendp/dpcreator-deploy.git
git clone git@github.com:opendp/dpcreator.git

cd dpcreator-deploy/k8s_maker/rendered/

```

### Make a static IP address through the Cloud Shell

1. Determine the resource group name
    ```
    az aks show --resource-group DPCreator \
     --name dp-creator-cluster \
     --query nodeResourceGroup -o tsv
    ```
    - Result: `MC_DPCreator_dp-creator-cluster_eastus`

2. Generate the public IP address
  - Inputs: 
    - Resource group (from above): `MC_DPCreator_dp-creator`
    - IP address label: `ip-dev-dpcreator-org`
    ```
    az network public-ip create \
     --resource-group MC_DPCreator_dp-creator-cluster_eastus \
     --name ip-dev-dpcreator-org \
     --sku Standard \
     --allocation-method static \
     --query publicIp.ipAddress -o tsv
    ```
  - Result: `52.191.30.153`

Note: When viewing this new address through the web admin, the "routing preference" should be "Microsoft network"

-> **Resulting IP Address**: 13.92.177.209

### Assign the IP address to the appropriate domain name



## Note: PSI service IP generation

    ```
    az network public-ip create \
         --resource-group MC_DPCreator_dp-creator-cluster_eastus \
         --name ip-psiprivacy-org \
         --sku Standard \
         --allocation-method static \
         --query publicIp.ipAddress -o tsv
    ```

  - Result: `52.249.185.246`
