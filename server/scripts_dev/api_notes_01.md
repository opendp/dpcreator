

### API Endpoints
DRF link: http://localhost:8000/api/

**Contents**
- [Direct File Upload](#direct-file-upload)
- [Get Dataset info (including depositor setup info)](#get-dataset-info)


--- 

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

## Get Dataset info

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

## Update Depositor Info

This includes depositor setup info.

- **API endpoint**: `/api/deposit/{depositor_setup_object_id}/`
  - **Example**: `/api/deposit/b01377e1-eec0-43cc-9f7f-631f87dd4108/`
- **Method**: `PUT`
- **Auth**: username/password
- **Params**: Any or all of these params may be updated
  - **dataset_questions**: JSON, with the following keys and potential values:
    - **radio_best_describes**: "public", "notHarmButConfidential", "couldCauseHarm", "wouldLikelyCauseHarm", "wouldCauseSevereHarm"
       - empty string ("") returns an error
    - **radio_only_one_individual_per_row**: "yes", "no"
       - maybe be an empty string ("") in API call if not answered
    - **radio_depend_on_private_information**: "yes", "no"
       - maybe be an empty string ("") in API call if not answered
  - **epsilon_questions**: JSON, with the following keys and potential values:
    - **secret_sample**: "yes", "no"
       - maybe be an empty string ("") in API call if not answered
    - **population_size**: positive integer
       - Must be positive integer if secret_sample is "yes". Otherwise, population_size is not checked.
    - **observations_number_can_be_public**: "yes", "no"
       - maybe be an empty string ("") in API call if not answered
  - **data_profile**: json
    - Updated from the confirm variables page
  - **epsilon**: boolean
  - **delta**: boolean
  - **confidence_level**: choices
  - **is_complete**: boolean
- **DRF link**: http://localhost:8000/api/deposit/
- Response example:
```json
```