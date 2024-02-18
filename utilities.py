import requests
import json
import subprocess
import os

def download_github_repo_wget(repo_url, destination_path):
    """
    Download a GitHub repository as a ZIP archive using wget and extract it to a specified destination path.

    Args:
        repo_url (str): GitHub repository URL.
        destination_path (str): Local path to store the downloaded repository.
    """
    # Use wget to download the ZIP archive
    subprocess.run(["wget", repo_url + "/archive/main.zip", "-O", "temp.zip"])

    # Create the destination directory if it doesn't exist
    os.makedirs(destination_path, exist_ok=True)

    # Extract the ZIP archive to the destination path
    subprocess.run(["unzip", "temp.zip", "-d", destination_path])

    # Remove the temporary ZIP file
    os.remove("temp.zip")


def get_github_token(json_file_path) -> str:
    """
    Retrieve GitHub personal access token from a JSON file.

    Args:
        json_file_path (str): path to token

    Returns:
        str: GitHub personal access token.
    """
    with open(json_file_path, 'r') as json_file:
        github_token = json.load(json_file)["github_token"]
    return github_token

def create_pull_request(repo_owner, repo_name, base_branch, head_branch, title, body, token):
    """
    Create a pull request on GitHub.

    Args:
        repo_owner (str): Owner of the repository.
        repo_name (str): Name of the repository.
        base_branch (str): The branch where the changes should be merged into.
        head_branch (str): The branch containing the changes.
        title (str): Title of the pull request.
        body (str): Description of the changes in the pull request.
        token (str): GitHub personal access token with 'repo' scope.

    Returns:
        dict or None: JSON response if successful, None otherwise.
    """
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    payload = {
        'title': title,
        'body': body,
        'head': head_branch,
        'base': base_branch
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("Pull request created successfully!")
        return response.json()
    else:
        print(f"Failed to create pull request. Status code: {response.status_code}")
        print(response.text)
        return None
    
def run_checkstyle(checkstyle_dir_path, directory_path, output_file):
    """
    Run Checkstyle on Java code in a directory and save the results to an output file.

    Args:
        checkstyle_dir_path (str): Path to the Checkstyle directory.
        directory_path (str): Directory containing Java source files.
        output_file (str): File to save Checkstyle results.
    
    Returns:
        CompletedProcess: The result of the Checkstyle command.
    """
    checkstyle_jar_path = os.path.join(checkstyle_dir_path, "checkstyle-10.13.0-all.jar")
    checkstyle_xml_path = os.path.join(checkstyle_dir_path, "metric-checks.xml")

    command = f"java -jar {checkstyle_jar_path} \
        -c {checkstyle_xml_path} {directory_path} \
        > {output_file}"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # processing output even further
    with open(output_file, 'r') as file:
        lines = file.readlines()

    # removing system dependent paths
    prefix_to_remove = directory_path
    modified_lines = [line.split(prefix_to_remove)[-1].strip()+"\n" for line in lines]
    modified_lines = modified_lines[1:-1] # leave out audit statements

    with open(output_file, 'w') as file:
        file.writelines(modified_lines)

    return result

