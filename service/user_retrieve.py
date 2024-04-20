import requests
import os
from dotenv import load_dotenv


users_file = 'users.txt'
last_user_file = 'last_user.txt'
load_dotenv()


def read_users_from_file(file_path):
    users = set()
    try:
        with open(file_path, "r") as file:
            for line in file:
                user = line.strip()
                users.add(user)
    except FileNotFoundError:
        pass
    return users


def get_github_users(limit=100, since=None, per_page=100, token=None):
    url = "https://api.github.com/users"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    params = {
        "since": since,
        "per_page": per_page
    }
    all_users = []
    for i in range(limit):
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            users = response.json()
            if not users:
                break
            store_users_to_file(users, users_file)
            all_users.extend(users)
            since = users[-1]["id"]
            params["since"] = since
            with open(last_user_file, "w") as file:
                file.write(str(since))
        else:
            print(f"Failed to retrieve users: {response.status_code}")
            break
    return all_users


def get_since_from_file():
    if os.path.isfile(last_user_file):
        with open(last_user_file, "r") as file:
            since = file.readline().strip()
            if since:
                return int(since)
    return None


def store_users_to_file(users, file_path):
    existing_users = read_users_from_file(file_path)
    new_users = {user_dict["login"] for user_dict in users}
    combined_users = existing_users.union(new_users)
    with open(file_path, "w") as file:
        for user in combined_users:
            file.write(user + "\n")


def main():
    token = os.getenv('GITHUB_TOKEN')
    get_github_users(token=token, since=get_since_from_file())


if __name__ == "__main__":
    main()
