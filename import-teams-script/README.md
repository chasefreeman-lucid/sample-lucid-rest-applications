# LUCID TEAMS CREATION SCRIPT

## Helper script to automatically generate teams with specified sets of users and custom folder structure. This uses the Lucid Public API to query and create teams and optional folder structure.

# Setup.

Follow the directions below to set up the script.

1. Create a Lucid API Key
    - Go to the [Lucid Developer Portal API Keys section](https://lucid.app/developer/apikeys)
    - Click `Create API Key`
    - Give the key a name and set the expiration
    - Define the grants as the following
        - Always Required: 
            - Teams: Admin
                - This requires the user to have the Team Admin role in Lucid to grant
            - Accounts: Readonly
        - Required if using a custom folder structure:
            - Folder: Edit
            - User: View
    - Click `Generate Api Key` and copy the generated key. You will not be able to see it again
    - Note: An [OAuth2 token](https://developer.lucid.co/reference/obtaining-an-access-token) with the `teams:admin`, `account.user:readonly`, `folder`, and `user.profile` can be used in place of the API Key
2. Open the `config.ini` file and set the following required values:
    - TOKENS
        - `KEY` - The API Key or equivalent token created during step 2
    - FILES
        - `TEAM_CSV_FILEPATH` - The relative filepath to the CSV file that defines the teams and users
            - The CSV must contain a column titled `email` that contains the email of the Lucid user to be added to teams
            - The CSV must contain a column titled `teams` that contains a comma separated string of teams that the user defined in the same row should be added to
            - An example CSV containing these fields can be found in `example_teams.csv`
    - Note: Optional Field Definitions
        - `REMOVE_EXISTING_USERS` - This flag defines the behavior for the event that a Lucid team already exists with the same name
            - `true` - The script will remove any users from the specified team that are not defined in the CSV
            - `false` - The script will leave existing users on a team in place despite status of the CSV
        - `CREATE_FOLDER_STRUCTURE` - This flag defines whether or not the script should create a set of folders in each team created
            - `true` - The script will create the folder structure defined by the file contained at the path defined at `FOLDER_STRUCTURE_FILEPATH` in the `config.ini` file
                - Note: If true, the `FOLDER_STRUCTURE_FILEPATH` is **required**. 
            - `false` - The script will not create a custom folder structure even if defined
        - `FOLDER_STRUCTURE_FILEPATH` - The relative filepath to the JSON file that defines the custom folder structure
            - The structure of the JSON file is expected to be of the following sample format:
            ```
            [
                {
                    "name": "FolderName",
                    "subFolders": [
                        {
                            "name": "SubFolderName",
                            "subFolders": [...]
                        },
                    ]
                },
                ...
            ]
            ```
            - See `example_folders.json` for a more defined example of what this could look like.
3. Run the script manually via python
    - Example: `python ./importteams.py`
    - If the data is configured properly, the script will print a statement noting it as complete along with any errors that may have occurred.

# Important Notes
- This script is not intended to work with unlicensed users. If detected, the script will print an error message with the email of the user that does not have a valid Lucid license. 
    - If this would result in a team with no users, that team will not be created and an error message will be printed with the team that did not get created.
- The script will not create custom folders in already existing teams
    - This is to prevent a situation in which duplicate folders are created inside of an already configured team.


