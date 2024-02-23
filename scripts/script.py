import openai
from dotenv import load_dotenv
import requests

import os
from pathlib import Path
import sys
import git
from git import Repo
import time

# Set the "./../" from the script folder
# dir_name = None
# try:
#     dir_name = os.path.dirname(os.path.realpath(__file__))
# except NameError:
#     print("WARNING: __file__ not found, trying local")
#     dir_name = os.path.abspath('')
# lib_path = os.path.realpath(f"{Path(dir_name).parent}")
# # Add to path
# if lib_path not in sys.path:
#     print(f"Adding library path: {lib_path} to PYTHONPATH")
#     sys.path.append(lib_path)
# else:
#     print(f"Library path {lib_path} already in PYTHONPATH")

# import utilities
# design choice - rewrite all necessary functions here again

# Loading environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
github_api_token = os.getenv("API_GITHUB_TOKEN")

# constants
GITHUB_REPO_URL = "https://github.com/FlightVin/refactoring-test-repo"
LOCAL_REPO_PATH = "./temp"

# utility functions
def clone_or_pull_repo(repo_url, local_path):
    """
    Clone a Git repository if it doesn't exist locally, or pull the latest changes if it already exists.
    Checks out to main/master branch

    Parameters:
        repo_url (str): The URL of the Git repository.
        local_path (str): The local path where the repository should be cloned or pulled.

    Returns:
        None
    """
    if os.path.isdir(local_path):
        print("Repository already cloned. Pulling latest changes...")
        repo = Repo(local_path)
        print(repo)
        try:
            repo.git.checkout('main')
        except:
            raise
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("Cloning repository...")
        repo = Repo.clone_from(repo_url, local_path)
        print(repo)
        try:
            repo.git.checkout('main')
        except:
            repo.git.checkout('master')

def analyze_code_for_design_smells(code, code_smells):
    """
    Analyze code for potential design smells using OpenAI's ChatGPT.

    Parameters:
        code (str): The code to be analyzed.

    Returns:
        str: The analysis result.
    """
    try:
        messages = [{
            "role": "system",
            "content": "You are a senior software engineer tasked with reviewing code for potential design smells."
        }, {
            "role": "user",
            "content": f"Here are the code smells that you found earlier-\n \
                {code_smells}\n\
                Use this and your general understanding to review this java code for design smells:\
                    \n\n\
                    ```\
                    {code}\n\
                    ```\
                    "
        }]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-3.5-turbo model
            messages=messages,
            max_tokens=max(50, len(code) + 100),
            temperature=0.5
        )
        # Assuming the last message contains the analysis
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error analyzing code: {str(e)}"
    
def analyze_code_for_code_smells(code):
    """
    Analyze code for potential code smells using OpenAI's ChatGPT.

    Parameters:
        code (str): The code to be analyzed.

    Returns:
        str: The analysis result.
    """
    try:
        messages = [{
            "role": "system",
            "content": "You are a senior software engineer tasked with reviewing code for potential code smells. Use metrics such as\n \
                - Cyclomatic Complexity\n\
                - Class Data Abstraction Coupling\n\
                - Class Fan Out Complexity\n\
                - Boolean Expression Complexity\n\
                - NPath Complexity\n\
                - JavaNCSS\n\
                and other forms of code smells and metrics that you can think of."
        }, {
            "role": "user",
            "content": f"Review this code:\n\n{code}"
        }]
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use gpt-3.5-turbo model
            messages=messages,
            max_tokens=max(50, len(code) + 100),
            temperature=0.5
        )
        # Assuming the last message contains the analysis
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

def list_java_files(directory):
    """
    List paths to all Java files (.java) in a directory and its subdirectories.

    Parameters:
        directory (str): The root directory to start listing Java files.

    Returns:
        List[str]: A list of paths to Java files.
    """
    java_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files

def refactor_code(code, smells):
    try:
        refactoring_prompt = f"""
        You are a senior software engineer who is trying to refactor a project. Do not reply with ANYTHING besides the source code in the new language.
        Make SURE the syntax is correct, and the new code matches the functionality of the source code exactly. Write the code in a modern, functional, clean manner. Do NOT include any markdown syntax. Do NOT include any explanations, or any other text besides the source code.
        If you refactor anything, add a comment explaining the changes made.

        Design smells found:
        {smells}

        Source code to refactor:
        {code}
        """

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "Refactor the following code."
            }, {
                "role": "user",
                "content": refactoring_prompt
            }],
            max_tokens=1024,
            temperature=0.5
        )

        refactored_code = response['choices'][0]['message']['content']
        return refactored_code
    except Exception as e:
        return f"Error refactoring code: {str(e)}"

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

def create_and_checkout_branch(repo_path, new_branch_name):
    """
    Create a new branch and check out into it using GitPython.

    Args:
        repo_path (str): Path to the local repository.
        new_branch_name (str): Name of the new branch.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        repo = git.Repo(repo_path)
        
        # Create a new branch and check out into it
        repo.git.checkout(b=new_branch_name)

        print(f"Branch '{new_branch_name}' created and checked out successfully!")
        return True
    except git.GitCommandError as e:
        print(f"Failed to create and check out branch. Error: {e}")
        return False

# clone repo
clone_or_pull_repo(GITHUB_REPO_URL, LOCAL_REPO_PATH)
print("Repository cloned successfully")

java_file_paths = list_java_files(LOCAL_REPO_PATH)

timestamp = int(time.time())
new_branch_name = f"branch_{timestamp}"
new_branch_formed = create_and_checkout_branch(LOCAL_REPO_PATH, new_branch_name)
if new_branch_formed:
    print(f"Formed new branch {new_branch_name}")
else:
    print("Could not form new branch")
    raise

for (i, file_path) in enumerate(java_file_paths):
    print("Analyzing code in file:", file_path)

    # code metrics
    with open(file_path, 'r') as file:
        code = file.read()
        code_smells = analyze_code_for_code_smells(code)
        print("Code Smells Found:", code_smells)
        print('\n')
        print("Code smells Analysis Complete")
    
    # finding design smells
    with open(file_path, 'r') as file:
        code = file.read()
        design_smells = analyze_code_for_design_smells(code, code_smells)
        print("Design Smells Found:", design_smells)
        print('\n')
        print("Code smells Analysis Complete")

    # Refactoring code
    with open(file_path, 'r') as file:
        code = file.read()
        refactored_code = refactor_code(design_smells, code)

    # writing the refactored code
    with open(file_path, 'w') as file:
        file.write(refactored_code)

    if i == 5:
        print(f"\nBreaking to preserve API limit after {i} files\n")
        break

repo_owner = 'FlightVin'
repo_name = 'refactoring-test-repo'
base_branch = 'main'
head_branch = new_branch_name
title = 'Refactor'
body = 'The code has been refactored based on smells detected.'

pull_request_info = create_pull_request(repo_owner, repo_name, base_branch, head_branch, title, body, github_api_token)
print(pull_request_info)
