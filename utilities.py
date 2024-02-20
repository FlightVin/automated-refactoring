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
    
def build_prompt(prompt_file_path, checkstyle_output_path, current_code_path):
    """
    Build a prompt for a code completion task using information from a JSON prompt file,
    the current code file, and Checkstyle metrics.

    Args:
        prompt_file_path (str): Path to the JSON prompt file.
        checkstyle_output_path (str): Path to the Checkstyle output file.
        current_code_path (str): Path to the current Java code file.

    Returns:
        str: The constructed prompt for code completion.
    """
    import json
    import os

    # Load information from the JSON prompt file
    with open(prompt_file_path, 'r') as json_file:
        prompt_file = json.load(json_file)

    # Extract the considered code path from the current code file path
    considered_code_path = current_code_path.split("temp")[1][1:]

    # Construct the base prompt using information from the prompt file
    prompt = prompt_file["base"] + prompt_file["code_desc"].format(file_name=considered_code_path)

    # Read the content of the current code file and add it to the prompt
    with open(current_code_path) as f:
        current_code = f.read()

    prompt += "```java\n"
    prompt += current_code
    prompt += "\n```\n\n"

    # Add code metrics information from Checkstyle output
    prompt += prompt_file["checkstyle_desc"]

    with open(checkstyle_output_path) as f:
        all_code_metrics = f.readlines()

    # Filter out metrics for the current file
    code_file_name = os.path.basename(current_code_path)
    current_code_metrics = ""
    for i in all_code_metrics:
        if code_file_name in i:
            current_code_metrics += " - "
            current_code_metrics += i
    current_code_metrics += "\n"

    # Handle the case where no smells were found
    if current_code_metrics == "\n":
        current_code_metrics = "No smells were found\n"

    prompt += current_code_metrics

    # Add a description of code smells
    prompt += prompt_file["checkstyle_metrics"]

    # Add the ending part of the prompt
    prompt += prompt_file["prompt_ending"]

    return prompt
