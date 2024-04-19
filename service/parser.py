import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv


output_file_name = 'output.txt'
load_dotenv()


def clean_file(file_path):
    with open(file_path, "w") as file:
        file.truncate(0)


def send_email(receiver_email, subject, body, attachment_path=None):
    if os.path.getsize(output_file_name) == 0:
        return
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {attachment_path.split('/')[-1]}")
        message.attach(part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

    print("Email sent successfully")
    clean_file(output_file_name)


def get_all_repositories(username):
    url = f"https://api.github.com/users/{username}/repos"
    token = os.getenv('GITHUB_TOKEN')
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repositories = response.json()
        return repositories
    else:
        print(f"Failed to retrieve repositories: {response.status_code}")
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


def main(search):
    if not search:
        query = input("Enter search query for GitHub repositories: ")
    else:
        query = search
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


if __name__ == "__main__":
    receiver_address = os.getenv('RECEIVER_ADDRESS')
    main('rdovgan')
    send_email(receiver_address, 'Diamond inside', 'Result email with attachment', output_file_name)
