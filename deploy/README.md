# Azure Deployment

This document contains steps for a basic deployment of the DPCreator application on Azure. 

The deployment is on a kubernetes (k8s) cluster and requires the coordination of several pieces, including:

- Building of Docker Images
- Creation of k8s .yaml files with correct environment variable settings
- Setting up Azure resources

The instructions here are not exhaustive and depend on the specific cluster/etc.

## Preliminaries

Before starting, make sure you have access to:

- GitHub [opendp/dpcreator repository](https://github.com/opendp/dpcreator) 
- OpenDP GitHub [packages/container registry](https://github.com/orgs/opendp/packages)
- [Azure account](https://azure.microsoft.com/)

In terms of software, you'll need:
- A local DPCreator development environment installed including Node and Python.
- Docker

## Building of Docker Images

(Note: In the future this should be a GitHub action.)

Deployment currently requires the building of two Docker images:
- (A) DPCreator app 
- (B) DPCreator nginx 

### (A) DPCreator app

1. Build node/vue app files
    ```
    # Switch to the "client" directory 
    #  (at the top-level of the dpcreator repository)
    cd client
    export NODE_ENV=production DEV_MODE=false
    ./run_client.sh   #npm run build
    ```
2. Build/Push docker images
    ```
    # Switch to the "server" directory 
    #  (at the top-level of the dpcreator repository)
    cd ../server
    
    # Build/Push DPCreator app  
    #  -- change YYYY-MMDD to the current date
    docker build -t ghcr.io/opendp/dpcreator/app:YYYY-MMDD .
    docker push ghcr.io/opendp/dpcreator/app:YYYY-MMDD   
    ```

### (B) DPCreator nginx

- Build/Push docker images

    ```
    # Switch to the "deploy/nginx-setup" directory 
    #  (from the top-level of the dpcreator repository)
    cd deploy/nginx-setup
      
    # Build/Push DPCreator nginx
    #  -- change YYYY-MMDD to the current date
    docker build -t ghcr.io/opendp/dpcreator/nginx:YYYY-MMDD .
    docker push tghcr.io/opendp/dpcreator/nginx:YYYY-MMDD
    ```

- Setting up Azure resources
