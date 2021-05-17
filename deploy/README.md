# Deployment Instructions 

(in process)

## Kubernetes on Azure

- Example
```
cd ../deploy/nginx-setup
docker build -f ./Dockerfile -t ghcr.io/opendp/dpcreator/nginx:t01 .
docker push ghcr.io/opendp/dpcreator/nginx:t01 
cd ../../server;
```