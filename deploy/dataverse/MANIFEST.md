## External Tools Manifest File


```json
{
  "displayName": "DP Creator",
  "description": "Create Differentially Private Statistics.",
  "type": "explore",
  "toolUrl": "http://dev.dpcreator.org/api/dv-handoff",
  "toolParameters": {
    "queryParameters": [
      {
        "fileId": "{fileId}"
      },
      {
        "filePid": "{filePid}"
      },
      {
        "datasetPid": "{datasetPid}"
      },
      {
        "apiGeneralToken": "{apiToken}"
      },
	  {
	   "site_url": "{siteUrl}"
	  }
    ]
  }
}
```