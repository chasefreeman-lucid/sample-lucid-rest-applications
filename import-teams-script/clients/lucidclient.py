from requests import post
from requests import get
from time import sleep
import logging


logger = logging.getLogger("log")
base_url = "https://api.lucid.co"

def create_team(token, name, initial_users, team_type):
    request_url = f"{base_url}/teams"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
        "Lucid-Request-As": "admin",
    }

    body = {
        "name": f"{name}",
        "users": initial_users,
        "type": f"{team_type}"
    }

    response = post(url=request_url, json=body, headers=headers)

    if response.status_code == 429:
        retry_after = response.headers['Retry-after']
        sleep(int(retry_after))
        response = post(url=request_url, json=body, headers=headers)

    response.raise_for_status()

    return response.json()['id']

def get_teams(token): 
    request_url = f"{base_url}/teams"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
        "Lucid-Request-As": "admin",
    }

    # set a page limit in case of infinite looping error should allow for processing 200,000 teams
    page_limit = 1000
    page_count = 0

    team_dictionary = {}

    while page_count < page_limit:
        page_count += 1

        response = get(url=request_url, headers=headers)

        if response.status_code == 429:
            retry_after = response.headers['Retry-after']
            sleep(int(retry_after))
            response = get(url=request_url, headers=headers)

        response.raise_for_status()

        json_data = response.json()

        for team in json_data:
            team_dictionary[f"{team["name"]}"] = team["id"]


        link = response.headers.get("Link")
        if link == None:
            break

        start_index = link.find("<") + 1
        end_index = link.find(">")
        new_url = link[start_index:end_index]

        request_url = new_url

    return team_dictionary

def add_team_users(token, target_team, users):
    request_url = f"{base_url}/teams/{target_team}/users/add"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
        "Lucid-Request-As": "admin",
    }

    body = {
        "users": users,
    }

    response = post(url=request_url, json=body, headers=headers)

    if response.status_code == 429:
        retry_after = response.headers['Retry-after']
        sleep(int(retry_after))
        response = post(url=request_url, json=body, headers=headers)

    response.raise_for_status()

    return


def get_team_users(token, target_team):
    request_url = f"{base_url}/teams/{target_team}/users"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
        "Lucid-Request-As": "admin",
    }

    # set a page limit in case of infinite looping error should allow for processing 200,000 users
    page_limit = 1000
    page_count = 0

    team_users = []

    while page_count < page_limit:
        page_count += 1

        response = get(url=request_url, headers=headers)

        if response.status_code == 429:
            retry_after = response.headers['Retry-after']
            sleep(int(retry_after))
            response = get(url=request_url, headers=headers)

        response.raise_for_status()  

        json_data = response.json()

        for profile in json_data:  
            team_users.append(profile["id"])

        link = response.headers.get("Link")
        if link == None:
            return team_users

        start_index = link.find("<") + 1
        end_index = link.find(">")
        new_url = link[start_index:end_index]

        request_url = new_url
            
        
def remove_team_users(token, team_id, users):
    request_url = f"{base_url}/teams/{team_id}/users/remove"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
        "Lucid-Request-As": "admin",
    }

    body = {
        "users": users
    }

    response = post(url=request_url, json=body, headers=headers)

    if response.status_code == 429:
        retry_after = response.headers['Retry-after']
        sleep(int(retry_after))
        response = post(url=request_url, json=body, headers=headers)

    response.raise_for_status

    return
        
def create_folder(token, folderName, parent_folder = None, parent_team = None):
    if parent_folder == None and parent_team == None:
        logger.error("Attempting to create a folder with no defined parent")
        return None
    
    request_url = f"{base_url}/folders"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
    }

    body = {
        "name": f"{folderName}",
        "type": "folder"
    }

    if parent_folder != None:
        body["parent"] = parent_folder
    else:
        body["team"] = parent_team
    
    response = post(url=request_url, json=body, headers=headers)

    if response.status_code == 429:
        retry_after = response.headers['Retry-after']
        sleep(int(retry_after))
        response = post(url=request_url, json=body, headers=headers)

    response.raise_for_status()

    return response.json()['id']
    

def get_user_profile_id(token):
    request_url = f"{base_url}/users/me/profile"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
    }

    response = get(url=request_url, headers=headers)

    if response.status_code == 429:
        retry_after = response.headers['Retry-after']
        sleep(int(retry_after))
        response = get(url=request_url, headers=headers)

    response.raise_for_status()

    return response.json()['id']

    
            
def search_users(token, user_emails):
    request_url = f"{base_url}/users/searchByEmail"

    headers = {
        "Authorization": f"Bearer {token}",
        "Lucid-Api-Version": "1",
    }

    # set a page limit in case of infinite looping error should allow for processing 200,000 users
    page_limit = 1000
    page_count = 0

    # 200 is the maximum requestable body from Lucid
    page_size = 200
    user_index = 0

    userDict = {}

    while user_index < len(user_emails) and page_count < page_limit:
        body = {
            "emails": user_emails[user_index:user_index + page_size]
        }

        page_count += 1
        user_index += page_size

        response = post(url=request_url, json=body, headers=headers)

        if response.status_code == 429:
            retry_after = response.headers['Retry-after']
            sleep(int(retry_after))
            response = post(url=request_url, json=body, headers=headers)

        response.raise_for_status()

        json_data = response.json()

        for user in json_data:
            userDict[user['email']] = user['id']


    return userDict



    