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

### Scenario 1: User Creates a Local Account  / Not coming from Dataverse

- **Inputs**: username, email, password1, password2
- **Object created**: OpenDPUser
- **Email Confirmation**: By default, email confirmation is enabled
    - When email confirmation is _disabled_, the OpenDPUser is immediately enabled and logged in.

### Scenario 2: User Creates a Local Account  / Coming from Dataverse

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
    - When the user logs in after email confirmation, if the OpenDPUser contains a `handoffId`, it is used to make a `dv-file` API call which:
        - Retrieves the DataverseHandoff
        - Retrieves the DataverseUser
        - Constructs a DataverseFileInfo object
        - The handoffId is then removed from the OpenDPUser object

### Scenario 3: User Logins into a Local Account  / Not coming from Dataverse

- **Inputs**: username, password
- **Objects retrieved**: An existing OpenDPUser (upon successful login)
- **Additional processing**: If the OpenDPUser contains a `handoffId`, it is then used to make a `dv-file` API call which will create a DataverseFileInfo object -- as described at the end of Scenario 2

### Scenario 4: User Logins into a Local Account  / Coming from Dataverse 

In this scenario, the OpenDPUser already exists but a DataverseUser does not.

- **Inputs**: handoffId, username, password
- **Objects retrieved**: An existing OpenDPUser 
- **Additional processing**: The `handoffId` is saved in the Vue store and indicates the user has arrived from Dataverse. This `handoffId` is used to:
    - If needed, make a DataverseUser object via API call and then
    - Make a `dv-file` API call which will create a DataverseFileInfo object -- as described at the end of Scenario 2
  - **_Possible Issue_**: The OpenDPUser object itself may contain a `handoffId` attribute that differs from the `handoffId` stored in the Vue store. In this case the `handoffId` saved in the Vue store is used to make a `dv-file` API call which will create a DataverseFileInfo object -- as described at the end of Scenario 2.

### Scenario 5: User Creates an Account Through Social Auth / Not Coming from Dataverse

This is every similar to Scenario #1.

- **Inputs**: Social Auth such as a Google Login
- **Object created**: OpenDPUser
- **Email Confirmation**: None. The OpenDPUser is immediately enabled and logged in.

### Scenario 6: User Creates or Logs into an Account Through Social Auth / Coming from Dataverse

This scenario resembles Scenario #4.

- **Objects created or retrieved**: OpenDPUser 
- **Additional processing**: The `handoffId` is saved in the Vue store and indicates the user has arrived from Dataverse. This `handoffId` is used to:
    - If needed, make a DataverseUser object via API call and then
    - Make a `dv-file` API call which will create a DataverseFileInfo object -- as described at the end of Scenario 2
  - _**Possible Issue**_: The OpenDPUser object itself may contain a `handoffId` attribute that differs from the `handoffId` stored in the Vue store. In this case the `handoffId` saved in the Vue store is used to make a `dv-file` API call which will create a DataverseFileInfo object -- as described at the end of Scenario 2.