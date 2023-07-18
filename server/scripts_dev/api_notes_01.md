

### API Endpoints
DRF link: http://localhost:8000/api/

**Contents**
- [Direct File Upload](#direct-file-upload)
- [Get Dataset info (including depositor setup info)](#get-dataset-info)
- [Update Depositor Setup Info](#update-depositor-setup-info)
- [Create Analysis Plan](#create-analysis-plan)
- [Update Analysis Plan](#update-analysis-plan)


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
        "data_profile": null,
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
- **Method**: `PATCH`
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
  - **is_complete**
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
    "data_profile": null,
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

## Create Analysis Plan 

Create an Analysis Plan using a DataSetInfo object. This endpoint may only be used by the user who is specified as the `creator` of the DataSetInfo object.
 

- **API endpoint**: `/api/analysis-plan/`
- **Method**: `POST`
- **Auth**: username/password
- **Params**: Sent as a JSON payload. Example:
  ```json
  {
    "object_id": "bbc5bd52-7c1e-4cf2-9938-28fd4745b5b1",
    "analyst_id": "0681867b-1ce8-46c9-adfb-df83b8efff24",
    "name": "Teacher survey plan",
    "description": "Release DP Statistics for the teacher survey, version 1",
    "epsilon": 0.25,
    "expiration_date": "2023-07-23"
  }
  ```
  - **object_id**: UUID of the DataSetInfo object
  - **analyst_id**: (optional) UUID of the Analyst, an OpenDP user. If not specified, the `creator` of the DatasetInfo object will be used as the Analyst
  - **name**: string, name of the new AnalysisPlan
  - **description**: (optional) string, description of the new AnalysisPlan
  - **epsilon**: float, allotted privacy budget for the new AnalysisPlan
  - **expiration_date**: string, expiration date of the new AnalysisPlan in YYYY-MM-DD format
- Response example:
  - Notes:
    - `object_id` is the UUID of the new AnalysisPlan
    - `variable_info` has been copied from `DataSetInfo.DepositorSetupInfo.variable_info`
    - `dp_statistics` is empty
    - `release_info` is empty
```json
{
  "object_id": "74526f03-7d6b-4205-b03e-da2131cd5a91",
  "name": "Teacher survey plan",
  "description": "Release DP Statistics for the teacher survey, version 1",
  "analyst": "549a4c94-2f85-4687-8205-94d7947f17e4",
  "dataset": "bbc5bd52-7c1e-4cf2-9938-28fd4745b5b1",
  "epsilon": 0.25,
  "delta": 0.0,
  "is_complete": false,
  "user_step": "step_100",
  "wizard_step": "step_100",
  "expiration_date": "2023-07-23T00:00:00Z",
  "variable_info": {
    "age": {
      "max": 55,
      "min": 5,
      "name": "age",
      "type": "Integer",
      "label": "age",
      "selected": true,
      "sortOrder": 1
    },
    "sex": {
      "max": null,
      "min": null,
      "name": "sex",
      "type": "Integer",
      "label": "sex",
      "selected": false,
      "sortOrder": 0
    },
    "smoking": {
      "name": "smoking",
      "type": "Categorical",
      "label": "",
      "sortOrder": 6,
      "categories": []
    },
    "optimism": {
      "name": "optimism",
      "type": "Categorical",
      "label": "",
      "sortOrder": 7,
      "categories": []
    },
    "selfesteem": {
      "name": "selfesteem",
      "type": "Categorical",
      "label": "",
      "sortOrder": 9,
      "categories": []
    },
    "havingchild": {
      "name": "Havingchild",
      "type": "Categorical",
      "label": "",
      "sortOrder": 3,
      "categories": []
    },
    "maritalstatus": {
      "name": "maritalstatus",
      "type": "Integer",
      "label": "",
      "sortOrder": 2
    },
    "sourceofstress": {
      "name": "sourceofstress",
      "type": "Categorical",
      "label": "",
      "sortOrder": 5,
      "categories": []
    },
    "lifesattisfaction": {
      "name": "lifesattisfaction",
      "type": "Categorical",
      "label": "",
      "sortOrder": 8,
      "categories": []
    },
    "highesteducationlevel": {
      "name": "highesteducationlevel",
      "type": "Integer",
      "label": "",
      "sortOrder": 4
    }
  },
  "dp_statistics": null,
  "release_info": null,
  "created": "2023-07-18T16:05:38.587556Z",
  "updated": "2023-07-18T16:05:38.587586Z"
}
```

## Update Analysis Plan 

Note: This endpoint may only be used by the user who is specified as the `analyst` of the AnalysisPlan.

- **API endpoint**: `/api/analysis-plan/{analysis_plan_object_id}/`
- **Method**: `PATCH`
- **Auth**: username/password
- **Params**: Sent as a JSON payload. Only a single field is needed for the patch. This example shows all updateable fields:
  ```json
  {
  "dp_statistics": "...JSON update from the create statistics page...",
  "variable_info": "...JSON update from the create variables page...",
  "name": "Teacher survey plan, version 2a",
  "description": "A new description",
  "wizard_step": "yellow brick road"
  }
  ```
    - **dp_statistics**: (optional) JSON object, updates to the DP Statistics. Send all of the `dp_statistics` each time, it doesn't update partial `dp_statistics`..
    - **variable_info**: (optional) JSON object, updates to the variable_info. Send all of the `variable_info` each time--it doesn't update partial `variable_inf`.
    - **name**: (optional) The AnalysisPlan may be renamed at any time.
    - **description**: (optional) The AnalysisPlan description be changed at any time.
    - **wizard_step**: (optional) Update  `wizard_step`. There is no server-side validation for this field--except that's an non-empty string
- Response example:
  - The response will be the same as that for Create Analysis Plan (above), with the field updates reflected.

## Delete Analysis Plan 

Both the `AnalysisPlan.analyst` and `DatasetInfo.creator` have permission to delete an AnalysisPlan.

**Note**: Delete is NOT allowed if a ReleaseInfo object has been created for this AnalysisPlan.


- **API endpoint**: `/api/analysis-plan/{analysis_plan_object_id}/`
- **Method**: `DELETE`
- **Auth**: username/password
- **Expected response**: `204 No Content`