# Dataverse Notes

- Note: This applies to Dataverse instances used for **testing/demonstration** of DP Creator, not production versions.

## Make Messaging/Permission Updates

- Log in with an account that has Admin privileges
- Go to the homepage
- From the right side of the screen, click the "Edit" button
- Select "**General Information**" from the dropdown
  - Make the following changes:
     - **Dataverse Name**: 
        ```html
        This Dataverse is for DP Creator testing purposes only.
        ```
     - **Description**: 
        ```html
         This site is for demonstration purposes only. Please DO NOT use sensitive or confidential data. For more information, please <a href="https://docs.google.com/document/d/e/2PACX-1vRlZ2IgigIhl4oz_uOakQPxovzlrmFkbD-x_9RUO31dC0eRq2wCt_vN2Go0_9LTRd67srjgy04CfPVk/pub" target="_blank">read the tutorial</a> or <a href="mailto:info@opendp.org?subject=DP%20Creator">contact us</a>.
        ```
       - In the future, the link should go to the user guide on the GitHub page
  - Save the changes
- Return to the homepage, click the "Edit" button again
- Select "**Permissions**" from the dropdown
  - Click the "**Edit Access**" button
     - For "**Who can add to this dataverse?**"
        - Select "Anyone with a Dataverse account can add datasets"
     - For "**When a user adds a new dataset to this dataverse, which role should be automatically assigned to them on that dataset?**"
        - Select "Curator - <i>Edit metadata, upload files, and edit files, edit Terms, Guestbook, File Restrictions (Files Access + Use), Edit Permissions/Assign Roles + Publish</i>"
     - Save the changes

### Checking updates

- At this point, the homepage should display a message at the top saying:
  ```
  This Dataverse is for DP Creator testing purposes only. (DO NOT upload sensitive data)
  ```
- In addition, under the "Metrics" section at the top left, a description should appear similar to:
    ```
    DO NOT upload sensitive data to this Dataverse.
    For more information, please read the DP Creator tutorial.
    ```
- Log out and log in with a _non-admin account_ (e.g. create a 2nd account if needed), on the homepage the user should have button labeled:
- 
   - `+ Add Data`
   - Test the button to see if the user can upload a file.
  
  
  