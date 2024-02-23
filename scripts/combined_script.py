import openai
from dotenv import load_dotenv
from github import Github

print("deprecated")
raise

# print the version of the openai library, assert it to be equal to 0.28.0
print(openai.__version__)

import os
import git
from git import Repo

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

print("OpenAI API Key:", openai.api_key)

GITHUB_REPO_URL = "https://github.com/FlightVin/refactoring-test-repo"
LOCAL_REPO_PATH = "./clone_repo"

DESIGN_SMELL_CHECK_PROMPT = """
You are a senior software engineer. Analyze this code for design smells after reading relevant documentation and codebase:
"""

def clone_or_pull_repo(repo_url, local_path):
    if os.path.isdir(local_path):
        print("Repository already cloned. Pulling latest changes...")
        repo = Repo(local_path)
        origin = repo.remotes.origin
        origin.pull()
    else:
        print("Cloning repository...")
        Repo.clone_from(repo_url, local_path)

def analyze_code_for_design_smells(code):
    try:
        messages = [{
            "role": "system",
            "content": "You are a senior software engineer tasked with reviewing code for potential design smells."
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

def create_pull_request(repo_name, base_branch, new_branch_name, file_path, refactored_code):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)

    base_ref = repo.get_git_ref(f"heads/{base_branch}")
    repo.create_git_ref(ref=f"refs/heads/{new_branch_name}", sha=base_ref.object.sha)

    contents = repo.get_contents(file_path, ref=new_branch_name)
    repo.update_file(contents.path, "Refactor code based on design smells", refactored_code, contents.sha, branch=new_branch_name)

    pr = repo.create_pull(title="Refactor Code Based on Design Smells", body="Automated refactoring based on identified design smells.", head=new_branch_name, base=base_branch)
    print(f"Pull Request created: {pr.html_url}")

clone_or_pull_repo(GITHUB_REPO_URL, LOCAL_REPO_PATH)
print("Repository cloned successfully")
file_path = os.path.join(LOCAL_REPO_PATH, 
    'books-core/src/main/java/com/sismics/books/core/model/jpa/UserBookTag.java')
print("Analyzing code in file:", file_path)

with open(file_path, 'r') as file:
    code = file.read()
    design_smells = analyze_code_for_design_smells(code)
    print("Design Smells Found:", design_smells)
    print('\n')
    print("Code smells Analysis Complete")

smell_description = design_smells

with open(file_path, 'r') as file:
    code = file.read()
    refactored_code = refactor_code(smell_description, code)
    with open('refactored_code.java', 'w') as file:
        file.write(refactored_code)