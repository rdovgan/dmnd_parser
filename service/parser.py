import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
import time


output_file_name = 'output.txt'
progress_file_name = 'progress.txt'
users_file_name = 'users.txt'
load_dotenv()

token = os.getenv('GITHUB_TOKEN')
headers = {"Authorization": f"token {token}"}

rate_limit = 0.72  # can make 5000 requests per hour


def clean_file(file_path):
    with open(file_path, "w") as file:
        file.truncate(0)


def send_email():
    receiver_email = os.getenv('RECEIVER_ADDRESS')
    if os.path.getsize(output_file_name) == 0:
        return
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = 'Diamond inside'

    message.attach(MIMEText('Result email with attachment', "plain"))

    with open(output_file_name, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {output_file_name.split('/')[-1]}")
    message.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

    print("Email sent successfully")
    clean_file(output_file_name)


def get_all_repositories(username):
    repositories = []
    url = f"https://api.github.com/users/{username}/repos"
    page = 1
    while True:
        params = {
            "page": page,
            "per_page": 100
        }
        time.sleep(rate_limit)
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            page_repositories = response.json()
            repositories.extend(page_repositories)
            if len(page_repositories) < 100:
                # If the number of repositories in the response is less than 100, we've reached the last page
                break
            else:
                # Increment the page number for the next request
                page += 1
        else:
            print(f"Failed to retrieve repositories: {response.status_code}")
            return []
    return repositories


def get_repository_files(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/"
    time.sleep(rate_limit)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [file['name'] for file in response.json() if file['type'] == 'file']
    else:
        print(f"Error occurred while fetching files for {owner}/{repo}: {response.text}")
        return []


def validate_lines(file_url):
    time.sleep(rate_limit)
    response = requests.get(file_url, headers=headers)
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


def main(search):
    if not search:
        print(f'Empty username')
        query = input("Enter GitHub username to search repositories: ")
    else:
        query = search
    print(f'Scan {search} user')
    repositories = get_all_repositories(query)
    print(f'Got {len(repositories)} repositories')

    for repo in repositories:
        owner = repo['owner']['login']
        repo_name = repo['name']
        files = get_repository_files(owner, repo_name)
        for file in files:
            file_url = f"https://raw.githubusercontent.com/{owner}/{repo_name}/master/{file}"
            if validate_lines(file_url):
                with open(output_file_name, 'a') as output_file:
                    output_file.write(f"{file_url} in {owner}/{repo_name} repository is valid.")


def update_progress(username):
    with open(progress_file_name, 'w') as file:
        file.write(username)


def read_next_username():
    with open(progress_file_name, 'r+') as progress:
        found_user = False
        last_processed_user = progress.readline().strip()
        with open(users_file_name, 'r') as user_file:
            if last_processed_user is None or not last_processed_user:
                found_user = True
            for line in user_file:
                if found_user:
                    next_username_to_process = line.strip()
                    update_progress(next_username_to_process)
                    return next_username_to_process
                if line.strip() == last_processed_user:
                    found_user = True
    return None


if __name__ == "__main__":
    next_username = read_next_username()
    while next_username is not None:
        main(next_username)
        send_email()
        next_username = read_next_username()
