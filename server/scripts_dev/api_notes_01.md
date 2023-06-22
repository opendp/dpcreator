

[click on this link](#direct-file-upload)

[click on this linkz](#get-dataset-info)


## Direct File Upload

- **API endpoint**: `/api/direct-upload/`
- **Method**: `POST`
- **Params**:
  - **name**: string
    - example: `Teacher survey 2023`
  - **source_file**: file to upload
    - note: actual file object
  - **creator**: string, user object id
    - example: `c1b958b3-92a3-46e0-83fc-3a89d276a11a`
- **Auth**: username/password
- **DRF link**: http://localhost:8000/api/direct-upload/
- Response example:
```json
{
    "object_id": "1258153b-7d3f-48c1-a1ed-6d2611129e8b",
    "name": "Teacher Survey",
    "source_file": "source-file/2023/06/22/teacher_survey_TTh9nVL.csv",
    "creator": "c1b958b3-92a3-46e0-83fc-3a89d276a11a"
}
```

## Get Dataset Info 

This includes depositor setup info.

- **API endpoint**: `/api/dataset-info/{dataset_object_id}/`
  - **Example**: `/api/dataset-info/0d8f0aec-0f3a-44af-8502-d185fb93e01d/`
- **Method**: `GET`
- **Auth**: username/password
- **DRF link**: http://localhost:8000/api/dataset-info/
- Response example:
```json
{
    "object_id": "0d8f0aec-0f3a-44af-8502-d185fb93e01d",
    "name": "Teacher Survey",
    "created": "2023-06-22T19:54:41.378354Z",
    "creator": "dp_analyst1",
    "depositor_setup_info": {
        "object_id": "b01377e1-eec0-43cc-9f7f-631f87dd4108",
        "id": 15,
        "created": "2023-06-22T19:54:41.375506Z",
        "updated": "2023-06-22T19:54:41.385458Z",
        "is_complete": false,
        "user_step": "step_100",
        "wizard_step": "step_100",
        "dataset_questions": null,
        "epsilon_questions": null,
        "unverified_data_profile": null,
        "data_profile": null,
        "default_epsilon": null,
        "epsilon": null,
        "default_delta": 0.0,
        "delta": 0.0,
        "confidence_level": 0.95
    },
    "status": "step_100",
    "analysis_plans": [],
    "resourcetype": "UploadFileInfo"
}
```