import logging
import pandas as pd
import configuration
from clients import lucidclient as lucid
from time import sleep

logger = logging.getLogger("log")
team_csv_path = configuration.get_value("FILES", "TEAM_CSV_FILEPATH")
folder_json_path = configuration.get_value("FILES", "FOLDER_STRUCTURE_FILEPATH")
token = configuration.get_value("TOKENS", "KEY")
create_custom_folders = configuration.get_value("FLAGS", "CREATE_FOLDER_STRUCTURE")
remove_existing_users = configuration.get_value("FLAGS", "REMOVE_EXISTING_USERS")


def ingest_data():

    csv = pd.read_csv(team_csv_path)

    team_dictionary = {}
        
    user_dictionary = lucid.search_users(token, csv["email"].values.tolist())

    for row in csv.itertuples():
        user_value = user_dictionary.get(row.email)
        teams = row.teams.split(',')

        if user_value == None:
            logger.warning(f"No Lucid user found for email {row.email}")

        for team in teams:
            stripped_team = team.strip()
            team_value = team_dictionary.get(stripped_team)

            if team_value == None and user_value == None:
                team_dictionary[stripped_team] = []
            elif team_value != None and user_value == None:
                continue
            elif team_value == None and user_value != None:
                team_dictionary[stripped_team] = [user_value]
            else:
                team_dictionary[stripped_team].append(user_value) 

        
    
    return team_dictionary

def process_teams(teams):

    # Get existing teams
    existing_teams = lucid.get_teams(token)

    folder_json = None
    if create_custom_folders:
        folder_json = pd.read_json(folder_json_path)
        if folder_json == None:
            print("Unable to find folder json with specified filepath, stopping without creating teams")
            return
    
    for key in teams.keys():
        users = teams[key]

        # if team exists
        existing_team_id = existing_teams.get(key)
        if existing_team_id != None:
            print(f"Team: {key} already exists in Lucid, adding new users")
            lucid.add_team_users(token, existing_team_id, users)

            if remove_existing_users:
                users_on_team = lucid.get_team_users(token, existing_team_id)

                users_to_remove = list(set(users_on_team) - set(users))
                if len(users_to_remove) != 0:
                    lucid.remove_team_users(token, existing_team_id, users_to_remove)

            # do not attempt custom folder structure to prevent duplication of folders in a team
            continue

        if len(users) == 0:
            logger.warning(f"No Lucid users assigned to {key}, skipping creation")
        else: 
            if create_custom_folders:
                user_id = lucid.get_user_profile_id(token)

                remove_current_user = False
                if user_id not in users:
                    users.append(user_id)
                    remove_current_user = True

                team_id = lucid.create_team(token, key, users, "open")

                # Prevents a race condition between creating the team and adding the folders
                # Lucid Teams Teams has been notifed. PLEASE REMOVE BEFORE PUBLISHING
                sleep(1)

                for folder in folder_json.itertuples():
                    add_folders(folder.name, folder.subFolders, parent_team=team_id)

                if remove_current_user:
                    lucid.remove_team_users(token, team_id, [user_id])
            else:
                lucid.create_team(token, key, users, "open")

    return

def add_folders(folderName, sub_folders, parent_folder = None, parent_team = None):

    folderId = lucid.create_folder(token, folderName, parent_folder, parent_team)

    if folderId == None:
        logger.error("Failed to create folder")

    for folder in sub_folders:
        add_folders(folder['name'], folder['subFolders'], parent_folder=folderId)


print("Team creation script started")

team_data = ingest_data()

print("CSV successfully ingested")

process_teams(team_data)

print("Team creation script compelte")