import requests
import json

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
