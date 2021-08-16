# Setting up Kubernetes (K8s) on Azure

Through the Azure admin:
- Create a "Kubernetes Service" using these specs and default values for other attributes
  - **Node Size**: D2as_v4
  - **Node count**: 2  (Manually sized)
- Through the Admin, connect to the K8s service.

### Log In

- Use the Azure admin instructions to launch a web-based Cloud Shell and connect to the cluster

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

### Make a static IP

Use the Azure web admin to create a "Public IP address"

- **Name**: ip-dev-dpcreator-org
- **DNS name label**: dev-dpcreator-org
- **Routing preference**: Microsoft network

-> **Resulting IP Address**: 13.92.177.209


