import requests
import os


users_file = 'users.txt'


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


def search_users_with_language(language, token):
    url = "https://api.github.com/search/repositories"
    params = {"q": f"language:{language}"}
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        repositories = response.json()["items"]
        users = set()
        for repo in repositories:
            owner = repo["owner"]["login"]
            users.add(owner)
        return users
    else:
        print(f"Failed to search for {language} repositories: {response.status_code}")
        return set()


def search_users_with_languages(languages, token):
    users = set()
    for language in languages:
        users.update(search_users_with_language(language, token))
    return users


def store_users_to_file(users, file_path):
    with open(file_path, "w") as file:
        for user in users:
            file.write(user + "\n")


def main():
    languages = ["Go", "Rust", "JavaScript", "Python"]
    token = os.getenv('GITHUB_TOKEN')
    existing_users = read_users_from_file(users_file)
    new_users = search_users_with_languages(languages, token)
    combined_users = existing_users.union(new_users)
    store_users_to_file(combined_users, users_file)
    print(f"Stored {len(combined_users)} unique users to {users_file}.")


if __name__ == "__main__":
    main()
