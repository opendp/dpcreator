# Dataverse Integration

## Integration (insecure) with Signed Urls

- Reference: https://docs.google.com/document/d/1iVNgr3eKCqoz5hjP9GF78TX6VC1Y4NY7Gn4z4G9jK7I/edit#heading=h.t2km9jjm5eu7

Dataverse communicates with DP Creator via signed urls. Specifically, when a Dataverse user launches DP Creator, the Dataverse goes to the following endpoint with the following data:

- **Endpoint**: `/api/dv-handoff/init-connection/`
  - Example: `http://dev.dpcreator.org/api/dv-handoff/init-connection/`
  - Method: POST followed by DP Creator redirecting to its UI
- **Data**: 
  - The data consists of a dictionary of named and signed urls used for retrieving and depositing data to/from Dataverse. 
  - URL Names/Purposes:
    - **userInfo** 
      - Retrieve information about the Dataverse user including name and email
    - **schemaInfo**
      - Retrieve information, including citation info, about the Dataverse file being used with DP Creator
    - **retrieveDataFile**
        - URL used to retrieve/access the Dataverse file. This url is not used until the user of DP Creator answers a preliminary set of questions regarding the suitability of the dataset for differential privacy.
    - **depositDPReleaseFile**
        - Once a DP Release is created, this endpoint is used to deposit the JSON and PDF files back in Dataverse    
  - Example
```JSON
{
   "apis":[
      {
         "name":"userInfo",
         "httpMethod":"GET",
         "signedUrl":"http://host.docker.internal:8089/api/users/:me?until=2022-08-08T11:18:28.368&user=dataverseAdmin&method=GET&token=bad3cbfff29bb2c3f8baa168dd20c86444c3a710195b9e25915eca4cc41791f84c5c3be08ec6a0a5f52573fa86876714d00e807c223572e143f92149525f29b2",
         "timeOut":10
      },
      {
         "name":"schemaInfo",
         "httpMethod":"GET",
         "signedUrl":"http://host.docker.internal:8089/api/datasets/export?exporter=schema.org&persistentId=doi:10.5072/FK2/FEWCXP&until=2022-08-08T11:23:28.431&user=dataverseAdmin&method=GET&token=1f3ec61c1fdf7cff9211861e4a988cdda12592b779c77d14eed78c51aa2c9be58ac1ea58189f5821dc59233a1455f3c9e8d5df9e338e00190401d7fcff914032",
         "timeOut":15
      },
      {
         "name":"retrieveDataFile",
         "httpMethod":"GET",
         "signedUrl":"http://host.docker.internal:8089/api/access/datafile/:persistentId/?persistentId=&until=2022-08-08T11:38:28.431&user=dataverseAdmin&method=GET&token=e56bf3c771d6c734bcb8c23b1c15a10ea2c1ffbbcf2d40dac0893a934ecc8ce99e081f2feef2a35a0c51b6fde06e86ab1cfb0cdc2fe67e2435dd27cadfde636a",
         "timeOut":30
      },
      {
         "name":"depositDPReleaseFile",
         "httpMethod":"POST",
         "signedUrl":"http://host.docker.internal:8089/api/access/datafile/4/auxiliary/dpJson/v1?until=2022-08-10T11:08:28.432&user=dataverseAdmin&method=POST&token=ee4de3814aee1bbca70e5b92f46de3168c90a7491d0292d52318b035cb4dd3bf26dc3a48979ced66434c2004ce9452747d4e4436961b5a28f3df0a8a083c24b0",
         "timeOut":2880
      }
   ]
}
```

### API Endpoint Validation / Workflow

- urls.py -> DataverseHandoffView (dataverse_handoff_view.py) -> init-connection




## Integration (insecure) with External Tools Framework

(Note: This will be phased out/removed once signed urls are in production.)

- **Endpoint**: `/api/dv-handoff/dv_orig_create/`
  - Example: `http://dev.dpcreator.org/api/dv-handoff/dv_orig_create/`