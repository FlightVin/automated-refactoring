import openai

# print the version of the openai library, assert it to be equal to 0.28.0
print(openai.__version__)

import os
import git
from git import Repo

openai.api_key = os.environ["OPENAI_API_KEY"]
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
        # Structure the prompt as a series of messages for a chat-like interaction
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

clone_or_pull_repo(GITHUB_REPO_URL, LOCAL_REPO_PATH)
print("Repository cloned successfully")
file_path = os.path.join(LOCAL_REPO_PATH, 'books-core/src/main/java/com/sismics/books/core/model/jpa/UserBookTag.java')
print("Analyzing code in file:", file_path)

with open(file_path, 'r') as file:
    code = file.read()
    design_smells = analyze_code_for_design_smells(code)
    print("Design Smells Found:", design_smells)
    print('\n')
    print("Code Analysis Complete")