import requests


def search_github_repositories(query):
    url = f"https://api.github.com/search/repositories?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print("Error occurred while fetching repositories:", response.text)
        return []


def get_repository_files(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    response = requests.get(url)
    if response.status_code == 200:
        return [file['name'] for file in response.json() if file['type'] == 'file']
    else:
        print(f"Error occurred while fetching files for {owner}/{repo}: {response.text}")
        return []


def validate_lines(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        lines = response.text.split('\n')
        lines_count = len(lines)
        if lines_count == 12 or lines_count == 24:
            for line in lines:
                if len(line.split()) != 1:
                    return False
            return True
        else:
            if lines_count == 1:
                words_count = len(lines[0].split())
                if words_count == 12 or words_count == 24:
                    return True
            return False
    else:
        print(f"Error occurred while fetching file content from {file_url}: {response.text}")
        return False


def main():
    query = input("Enter search query for GitHub repositories: ")
    repositories = search_github_repositories(query)

    for repo in repositories:
        owner = repo['owner']['login']
        repo_name = repo['name']
        files = get_repository_files(owner, repo_name)
        for file in files:
            file_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/master/{file}"
            if validate_lines(file_url):
                with open('output.txt', 'w') as output_file:
                    output_file.write(f"{file_url} in {owner}/{repo_name} repository is valid.")


if __name__ == "__main__":
    main()
