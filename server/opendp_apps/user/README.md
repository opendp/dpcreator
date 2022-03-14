# OpenDP User Objects

This document describes user scenarios to accommodate the creation/updating of accounts when the user launches DP Creator via Dataverse. (Currently Dataverse is not an OAuth provider, e.g. the worksarounds)

In general:
- User information for DP Creator is stored in the **OpenDPUser** object--an extension of the core Django User object. 
- In addition, if the person is using DP Creator via Dataverse, a **DataverseUser** is also created.
   - The **DataverseUser** is Dataverse installation specific
   - It's _possible_ that an OpenDPUser has multiple, related, DataverseUser objects
- In general, a user always has an **OpenDPUser** object and may have 1 or more related **DataverseUser** objects


```
(FK = ForeignKey)

- OpenDPUser - core User object
  - DataverseUser (optional)
    - FK to OpenDPUser 
    - FK to RegisteredDataverse 1
  - DataverseUser  (optional)
    - FKs to OpenDPUser 
    - FK to RegisteredDataverse 2

Example: 
- OpenDPUser - adumas, Alexander Dumas
  - DataverseUser 1
    - FK to OpenDPUser (adumas)
    - FK to RegisteredDataverse  (dataverse.harvard.edu)
  - DataverseUser 2
    - FK to OpenDPUser (adumas)
    - FK to RegisteredDataverse  (another-dataverse.odum-library.edu)
```

(Disclaimer: This structure of "optional" DataverseUser objects is a bit of a hack. e.g. Dataverse having an oauth service would be ideal.)


## OpenDP User Scenarios

The creation and login of users opening DP Creator from Dataverse presents a number of scenarios as described below.

Currently, the GET string from Dataverse to DP Creator contains Dataverse File information that is saved to DP Creator for use **after** the user creates an account and logs in. 

The saved information in this GET string is stored in a "DataverseHandoff" object, a Django model and is used to:
  - Create a DataverseUser 
    - The DataverseHandoff contains info indicating which RegisteredDataverse the data is coming from. It also contains the user's Dataverse API token--which doesn't work for security -- but will be corrected with [Issue 127](https://github.com/opendp/dpcreator/issues/127)
    - Remember, a DataverseUser is basically an object with FKs to:
      - an OpenDPUser and 
      - a RegisteredDataverse
  - Create a DataverseFileInfo object
    - The DataverseHandoff contains info indicating the Dataverse file ID, the enclosing Dataverse Dataset DOI, and other information to create a DataverseFileInfo object

### Note: Email Confirmation 

By default, **when creating a local account email confirmation is enabled**. All of the scenarios below **assume email confirmation is enabled**.

The enabling requires 3 Django settings:

1. SENDGRID_API_KEY - [SendGrid service](https://sendgrid.com/) API key
2. DEFAULT_FROM_EMAIL - "From" email used for SendGrid
3. ACCOUNT_EMAIL_VERIFICATION - `"mandatory"`
    - To disable email confirmation for account creation, change this setting to "none" -- the string `"none"` -- not the Python `None`
    - This setting is part of the Django [allauth package](https://django-allauth.readthedocs.io/en/latest/configuration.html)

Example settings via environment variables:

```
export SENDGRID_API_KEY=your-crazy-long-hashy-looking-sendgrid-key
export DEFAULT_FROM_EMAIL=info@opendp.org
export ACCOUNT_EMAIL_VERIFICATION=mandatory
```
--- 

### Note: Scenarios 1 to 8 below are also described in this google doc: 
  - https://docs.google.com/spreadsheets/d/199ZfuqGhBVzs3FHqekZjtIaYK-imh7Ri7DM2E7_FGsU/edit#gid=0


---

## Scenarios 1 to 4: Not Coming from Dataverse (No DataverseHandoff information/id)

### Scenario 1: User Creates a Local Account 

- **Inputs**: username, email, password1, password2
- **Object created**: OpenDPUser
- **Email Confirmation**: By default, email confirmation is enabled
    - When email confirmation is _disabled_, the OpenDPUser is immediately enabled and logged in.

### Scenario 2: User Logins into a Local Account  

- **Inputs**: username, password
- **Objects retrieved**: An existing OpenDPUser (upon successful login)
 
### Scenario 3: User Creates an Account through Social Auth

- **Inputs**: Google auth, etc.
- **Object created**: OpenDPUser
- **Email Confirmation**: Not applicable
 
### Scenario 4: User Logins into a Local Account 

- **Inputs**: Google auth, etc.
- **Objects retrieved**: An existing OpenDPUser (upon successful login)

## Scenarios 5 to 8: Coming from Dataverse (DataverseHandoff object saved, handoff id used)

### Scenario 5: User Creates a Local Account  / Coming from Dataverse

- **Inputs**: handoffId, username, email, password1, password2
  - `handoffId` - As noted earlier the `handoffId` gives access to a DataverseHandoff object stored in the database
- **Objects created**: OpenDPUser, DataverseUser
- **Email Confirmation**: By default, email confirmation is enabled
    - When email confirmation is _disabled_, the OpenDPUser is immediately enabled and logged in.
- **Additional functionality/error checking**: This scenario includes:
    - Retrieving the DataverseHandoff object from the database
    - Using the Dataverse API token stored in the DataverseHandoff to retrieve additional user information from Dataverse
    - If the DataverseHandoff cannot be found or the API call fails, neither the OpenDPUser nor DataverseUser is created.
    - On successful DataverseUser creation, the handoffId is stored as an attribute on the OpenDPUser object. 

### Scenario 6: User Logins into a Local Account  / Coming from Dataverse 

In this scenario, the OpenDPUser and DataverseUser exist and the OpenDPUser has a `handoff_id` saved on the server side.

- **Inputs**: username, password
- **Objects retrieved**: An existing OpenDPUser that has the `handoff_id` populated  
- **Additional processing**: The `handoffId` is saved in the Vue store and indicates the user has arrived from Dataverse. This `handoffId` is used to:
    - Make a `dv-file` API call which will create a DataverseFileInfo object by:
        - Retrieving the DataverseHandoff
        - Retrieving the DataverseUser
        - Constructing a DataverseFileInfo object
        - The handoffId is then removed from the OpenDPUser object
    - **_Possible Issue_**: The OpenDPUser object itself may contain a `handoffId` attribute that differs from the `handoffId` stored in the Vue store. In this case the `handoffId` saved in the Vue store is used to make a `dv-file` API call which will create a DataverseFileInfo object.

### Scenario 7: User Creates an Account Through Social Auth

This is every similar to Scenario #3. Note, because the account is created via social auth, the user is automatically logged in, e.g. Scenario 8 is immediately triggered.

- **Inputs**: Google auth, etc.
- **Object created**: OpenDPUser
- **Email Confirmation**: Not applicable

### Scenario 8: User Logs into an Account Through Social Auth 

This scenario is somewhat similar to Scenario #6, except that the DataverseUser does not yet exist.

- **Objects created or retrieved**: OpenDPUser 
- **Additional processing**: The `handoffId` has been saved in the Vue store and indicates the user has arrived from Dataverse. This `handoffId` is used to:
    - Call `/api/dv-user/` to create/update a DataverseUser object. 
      - Inputs: `OpenDPUser.object_id`, `handoffId`
    -  Call `/api/dv-file/` to create a DataverseFileInfo object -- as described at the end of Scenario 6
    - _**Possible Issue**_: The OpenDPUser object itself may contain a `handoffId` attribute that differs from the `handoffId` stored in the Vue store. In this case the `handoffId` saved in the Vue store is used to make a `dv-file` API call which will create a DataverseFileInfo object.