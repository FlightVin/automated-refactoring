import openai
from dotenv import load_dotenv

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

def read_design_smells(file_path):
    with open(file_path, 'r') as file:
        design_smells = file.readlines()
    return design_smells

def refactor_code(code, smells):
    try:
        # Construct the refactoring prompt
        refactoring_prompt = f"""
        You are a senior software engineer who is trying to refactor a project. Do not reply with ANYTHING besides the source code in the new language.
        Make SURE the syntax is correct, and the new code matches the functionality of the source code exactly. Write the code in a modern, functional, clean manner. Do NOT include any markdown syntax. Do NOT include any explanations, or any other text besides the source code.
        If you refactor anything, add a comment explaining the changes made.

        Design smells found:
        {smells}

        Source code to refactor:
        {code}
        """

        # Call the OpenAI API with the refactoring prompt
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
    
smell_description = read_design_smells('output.txt')
file_path = os.path.join(LOCAL_REPO_PATH, 'books-core/src/main/java/com/sismics/books/core/model/jpa/UserBookTag.java')
print("Analyzing code in file:", file_path)

with open(file_path, 'r') as file:
    code = file.read()
    refactored_code = refactor_code(smell_description, code)
    with open('refactored_code.java', 'w') as file:
        file.write(refactored_code)