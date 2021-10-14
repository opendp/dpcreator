# LaTeX Service for DP Creator

## Build the Docker Images

### Build the dpcreator/texlive-base image

```
# From within the ./latex_service directory
#
docker build -t ghcr.io/opendp/dpcreator/texlive-base:latest -f Dockerfile-texlive-base .
docker push ghcr.io/opendp/dpcreator/texlive-base:latest 

```

### Build the dpcreator/latex_service

```
docker build -t ghcr.io/opendp/dpcreator/latex-service:latest .
docker push ghcr.io/opendp/dpcreator/latex-service:latest 
```