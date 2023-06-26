

### API Endpoints
DRF link: http://localhost:8000/api/

**Contents**
- [Direct File Upload](#direct-file-upload)
- [Get Dataset info (including depositor setup info)](#get-dataset-info)
- [Update Depositor Setup Info](#update-depositor-setup-info)


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

## Update Depositor Setup Info

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
  - **variable_info**: JSON
    - Updated from the confirm variables page
  - **epsilon**: float field or null
  - **delta**: float field or null
  - **confidence_level**: choices in UI (0.90, 0.95, 0.99) 
- Note: Params that CANNOT be updated via API  
  - **is_complete
  - **user_step**
  - **default_epsilon**
  - **default_delta**
- **DRF link**: http://localhost:8000/api/deposit/
- Response example:
```json
{
    "object_id": "ab0dd16d-01d6-4aa8-90f1-b897aeef8746",
    "id": 1,
    "created": "2023-06-26T12:53:53.960872Z",
    "updated": "2023-06-26T12:53:54.012436Z",
    "is_complete": true,
    "user_step": "step_600",
    "wizard_step": "step_100",
    "dataset_questions": {
        "radio_best_describes": "notHarmButConfidential",
        "radio_only_one_individual_per_row": "yes",
        "radio_depend_on_private_information": "yes"
    },
    "epsilon_questions": {
        "secret_sample": "no",
        "population_size": "",
        "observations_number_can_be_public": "yes"
    },
    "unverified_data_profile": null,
    "variable_info": {
        "dataset": {
            "rowCount": 7000,
            "variableCount": 10,
            "variableOrder": [
                [
                    0,
                    "sex"
                ],
                [
                    1,
                    "age"
                ],
                [
                    2,
                    "maritalstatus"
                ],
                [
                    3,
                    "Havingchild"
                ],
                [
                    4,
                    "highesteducationlevel"
                ],
                [
                    5,
                    "sourceofstress"
                ],
                [
                    6,
                    "smoking"
                ],
                [
                    7,
                    "optimism"
                ],
                [
                    8,
                    "lifesattisfaction"
                ],
                [
                    9,
                    "selfesteem"
                ]
            ]
        },
        "variables": {
            "age": {
                "name": "age",
                "type": "Integer",
                "label": "",
                "sort_order": 1
            },
            "sex": {
                "name": "sex",
                "type": "Integer",
                "label": "",
                "sort_order": 0
            },
            "smoking": {
                "name": "smoking",
                "type": "Categorical",
                "label": "",
                "categories": [],
                "sort_order": 6
            },
            "optimism": {
                "name": "optimism",
                "type": "Categorical",
                "label": "",
                "categories": [],
                "sort_order": 7
            },
            "selfesteem": {
                "name": "selfesteem",
                "type": "Categorical",
                "label": "",
                "categories": [],
                "sort_order": 9
            },
            "Havingchild": {
                "name": "Havingchild",
                "type": "Categorical",
                "label": "",
                "categories": [],
                "sort_order": 3
            },
            "maritalstatus": {
                "name": "maritalstatus",
                "type": "Integer",
                "label": "",
                "sort_order": 2
            },
            "sourceofstress": {
                "name": "sourceofstress",
                "type": "Categorical",
                "label": "",
                "categories": [],
                "sort_order": 5
            },
            "lifesattisfaction": {
                "name": "lifesattisfaction",
                "type": "Categorical",
                "label": "",
                "categories": [],
                "sort_order": 8
            },
            "highesteducationlevel": {
                "name": "highesteducationlevel",
                "type": "Integer",
                "label": "",
                "sort_order": 4
            }
        }
    },
    "default_epsilon": 1.0,
    "epsilon": 0.75,
    "default_delta": 1e-05,
    "delta": 0.0,
    "confidence_level": 0.95
}
```