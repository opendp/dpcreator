# Kubernetes Deployment

This document contains steps for a basic deployment of the DPCreator application on Azure. 

The deployment is on a kubernetes (k8s) cluster and requires the coordination of several pieces, including:

- Building of Docker Images
- Creation of k8s .yaml files with correct environment variable settings
- Using the k8s files on an Azure cluster
- Setting up Azure resources (_covered in a separate doc_)

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

(Note: In the future this could be a GitHub action.)

Deployment currently requires the building of two Docker images:
- (A) DPCreator app 
- (B) DPCreator nginx 

### (A) DPCreator app

1. Build node/vue app files
    ```
    # Switch to the "client" directory 
    #  (at the top-level of the dpcreator repository)
    cd client
    
    #
    # Build the language file from the .csv
    #   - For more information, see README-TEXT.md at the top of the project directory
    #
    node ./build_locale/CreateLocaleJson.js
    # If this fails, try this--then run `CreateLocaleJson.js` again:
    # rm -rf node_modules
    # npm install
    # npm update
    
    #
    # Build the Vue app
    #
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
    #
    docker tag ghcr.io/opendp/dpcreator/app:YYYY-MMDD ghcr.io/opendp/dpcreator/app:latest
    docker push ghcr.io/opendp/dpcreator/app:latest
   
    # Example:
    docker build -t ghcr.io/opendp/dpcreator/app:2022-0119 .
    docker push ghcr.io/opendp/dpcreator/app:2022-0119  
    docker tag ghcr.io/opendp/dpcreator/app:2022-0119 ghcr.io/opendp/dpcreator/app:latest
    docker push ghcr.io/opendp/dpcreator/app:latest    
   ```
   

### (B) DPCreator nginx

- Build/Push docker images

    ```
    # Switch to the "deploy/nginx-setup" directory 
    #  (from the top-level of the dpcreator repository)
    cd ../deploy/nginx-setup
      
    # Build/Push DPCreator nginx
    #  -- change YYYY-MMDD to the current date
    docker build -t ghcr.io/opendp/dpcreator/nginx:YYYY-MMDD .
    docker push ghcr.io/opendp/dpcreator/nginx:YYYY-MMDD
    docker tag ghcr.io/opendp/dpcreator/nginx:YYYY-MMDD ghcr.io/opendp/dpcreator/nginx:latest
    docker push ghcr.io/opendp/dpcreator/nginx:latest
  
    # Example:
    docker build -t ghcr.io/opendp/dpcreator/nginx:2022-0119 .
    docker push ghcr.io/opendp/dpcreator/nginx:2022-0119
    docker tag ghcr.io/opendp/dpcreator/nginx:2022-0119 ghcr.io/opendp/dpcreator/nginx:latest
    docker push ghcr.io/opendp/dpcreator/nginx:latest  
    ```

## Creating the K8s deployment file(s)

(Assumes access to the Azure cluster with existing resources in place)

These steps document how to run a Python script which will generate a k8s specification that includes the Docker images generated above.

### Run the script to create the K8s file

1. Switch to the "deploy/k8s_maker" directory (from the top-level of the dpcreator repository)
    ```
    cd ../k8s_maker  # ../deploy/k8s_maker
    pip install -r requirements.txt     # one time install
    ```
2. Update the `dpcreator_specs_01.py` file.
    - This file contains variables which are passed into a k8s template.
    - __For most cases__, you will only need to change the `dpcreator_container_tag` to the current date. 
      - Example: `dpcreator_container_tag="2021-0608"`
3. _(Infrequent update)._ If needed, update the templates used to create the k8s file. 
    - Template location: `deploy/k8s_maker/templates`
        - There are two basic templates: one for the database container and another for the app.
    - Open the `make_k8s.py` file. 
    - Within the `make_k8s_template()` function, update these variables to point to the correct files:
        - `db_template_name` 
            - Example: `db_template_name = 'azure_k8s_04_database.yaml'`
        - `app_template_name` 
            - Example: `app_template_name = 'azure_k8s_04_app.yaml'`
   1. Run the script
      ```
      # From the "deploy/k8s_maker" directory
      python make_k8s.py
   
      # Expected output, something like:
      # ----------------------------------------
      # file written: /Users/ramanprasad/Documents/github-rp/dpcreator/deploy/k8s_maker/rendered/dev.dpcreator.org_07_2021_1213.yaml
      # ----------------------------------------
      # ----------------------------------------
      # file written: /Users/ramanprasad/Documents/github-rp/dpcreator/deploy/k8s_maker/rendered/test.dpcreator.org_07_2021_1213.yaml
      # ----------------------------------------   
      ```

4. Check the new/updated k8s file into the [opendp/dpcreator](https://github.com/opendp/dpcreator) repository

## Azure: Using the K8s file

(Assumes you have an Azure account.)
In this example, the cluster name is **DPCreatorCluster01**

1. Log into 'portal.azure.com'
1. From the "All Resources" section, find your cluster name and click on it.
1. Click on the "Connect" icon
   - Follow instructions 1 and 2 to open the Cloud Shell and connect to the cluster
1. (One time) Clone the dpcreator repository
   ```
   git clone git@github.com:opendp/dpcreator.git
   ```
1. (Very Infrequent) Upload the k8s secrets YAML file which contains settings such as the SECRET_KEY. (* The secrets file is not in this repository. Example name: `dpcreator-azure-secrets.yaml`)
   - The Azure cloud shell has a button to upload a file to your home directory.
   - Make the secrets available to the k8s cluster using the command:
      ```
      kc apply -f dpcreator-azure-secrets.yaml
      ```
1. Update the dpcreator repository + Start the app and related services
   ```
   cd dpcreator/deploy/k8s_maker/rendered/
   git pull
   # The k8s file you created in the previous section should be available
   
   # Start the application
   # - file name example: dpcreator_05_2021_0608.yaml
   #    
   kc apply -f dpcreator_nn_YYYY_MMDD.yaml  
   
   # Stop the application
   #
   kc delete -f dpcreator_nn_YYYY_MMDD.yaml  
   
   # To stop it immediately:
   kc delete -f dpcreator_nn_YYYY_MMDD.yaml -grace-period=0 --force
   
   
   ```
   - You should see output similar to:
       ```    
        configmap/dpcreator-db-data-configmap created
        deployment.apps/postgres created
        service/postgres-service created
        configmap/dpcreator-app-configmap created
        deployment.apps/dpcreator-app created
        service/dpcreator-load-balancer created
       ```
1. To see the running pods, run: `kc get pods`
   - Sample output:
        ```
        NAME                                 READY   STATUS              RESTARTS   AGE
        dpcreator-app-856ccfcfcc-cn5dr       0/2     ContainerCreating   0          1s
        dpcreator-database-695bffdb4-grvld   0/1     ContainerCreating   0          2s
        ```
    - Note, the DPCreator pod names are prefaced with `dpcreator-`
    - To see more details on a specific pod:
        ```
        # syntax:  kc describe pod dpcreator-app-[extension added at runtime)
        # example (be sure to change the extension!)
        #
        kc describe pod dpcreator-app-856ccfcfcc-cn5dr 
        ```
    
1. Below are several more k8s commands. 
    - For commands that are pod specific, you'll need the pod name from:
      - `kc get pods`
   ```
   # See if the services are running and the IP address
   #  - `dpcreator-load-balancer` - should have an external IP
   #  - `dpcreator-postgres-service` - db service
   # 
   kc get svc
   
   # -----------------
   # --- View Logs ---
   # -----------------
   # See the logs for the dpcreator app or nginx
   #  - example uses pod name "dpcreator-app-zzzzzzzz" where "zzzzzzzz" is 
   #    the extension added at pod creation
   
   # nginx logs, regular and tailed
   kc logs dpcreator-app-zzzzzzzz dpcreator-nginx
   kc logs -f dpcreator-app-zzzzzzzz dpcreator-nginx 

   # app logs, regular and tailed
   kc logs dpcreator-app-zzzzzzzz dpcreator-app
   kc logs -f dpcreator-app-zzzzzzzz dpcreator-app

   # ------------------------------------
   # --- Log into a Running Container ---
   # ------------------------------------
   # Log into the container dpcreator app or nginx
   #  - example uses pod name "dpcreator-app-zzzzzzzz" where "zzzzzzzz" is 
   #    the extension added at pod creation
   # 
   # Syntax:
   # kc exec -it [pod name] -c [container name] -- /bin/bash
   
   # nginx 
   kc exec -it dpcreator-app-zzzzzzzz -c dpcreator-nginx -- /bin/bash

   # app 
   kc exec -it dpcreator-app-zzzzzzzz -c dpcreator-app -- /bin/bash

   ```   
    