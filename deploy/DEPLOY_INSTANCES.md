Domain Naming/Setup

Checklist for Domain setup for instance + connected `RegisteredDataverse`

|                 |   DP Creator (K8s deploy)   |         Dataverse (EC2)        |              toolUrl (external tools manifest)             |  
|-----------------|:---------------------------:|:------------------------------:|:----------------------------------------------------------:|
| Demo Deployment | `http://demo.dpcreator.org` | `demo-dataverse.dpcreator.org` | `http://demo.dpcreator.org/api/dv-handoff/dv_orig_create/` |   
| Dev Deployment  | `http://dev.dpcreator.org`  | `dev-dataverse.dpcreator.org`  | `http://dev.dpcreator.org/api/dv-handoff/dv_orig_create/`  |   

**Demo**
- **OpenDP Team** - DP Creator instance: `demo.dpcreator.org`
  - [x] Azure K8s
  - [x] Fixture with Registered Dataverse `demo-dataverse.dpcreator.org`
- **Dataverse Team** 
  - [x] Stand-up EC2 instance: `demo-dataverse.dpcreator.org`  (DV version 5.8)
  - [x] Use SSL/HTTPS
  - [x] DNS setup via Google Domains (coordinate with @raprasad)
  - [x] external tools manifest file: Modify existing manifest file to use  `demo.dpcreator.org` 
    - **toolUrl**: `http://demo.dpcreator.org/api/dv-handoff/dv_orig_create/`
    - [x] Make sure the name of the tool in Dataverse is `DP Creator`

**Dev**

- **OpenDP Team** 
  - [x] Azure K8s
  - [x] Fixture with Registered Dataverse `dev-dataverse.dpcreator.org`
  - [x] Generate fixture update to change from EC2 url to domain name
- **Dataverse Team** - EC2 instance: `dev-dataverse.dpcreator.org`
  - [x] Stand-up EC2 instance:  `dev.dpcreator.org`
  - [x] No https
  - [x] DNS setup via Google Domains
  - [x] Upgrade to DV version ~~5.8~~ 5.9 
      - For DP Creator-related auxiliary file functionality -- ability to add JSON files
  - [x] external tools manifest file: Use existing manifest file with `dev.dpcreator.org` 
        - **toolUrl**: `http://dev.dpcreator.org/api/dv-handoff/dv_orig_create/`
    - [x] Make sure the name of the tool in Dataverse is `DP Creator`

