# Automated Refactoring Pipeline

## Tasks

- **Automated Design Smell Detection:** Develop a script or tool that
periodically scans the GitHub repository for design smells. This can include
metrics analysis, code pattern recognition, or any other relevant approach.
Utilize the capabilities of LLMs to assist in identifying potential design
issues in the codebase.

- **Automated Refactoring:** Implement an automated refactoring module that
takes the identified design smells and generates refactored code using LLMs.
Ensure that the refactoring process is robust, preserving the functionality of
the code while enhancing its design.

- **Pull Request Generation:** Design a mechanism to automatically create a
pull request with the refactored code changes.
Include detailed information in the pull request, such as the detected design
smells, the applied refactoring techniques, and any relevant metrics.

## High level overview of pipeline

- We have setup a cron job that runs `scripts/script.py` every few hours
- It pulls the `main` branch and finds design smells
- We refactor based on the design smells on a per-file basis
- We create a pull request with the new code

## TODO

- [x] Get basic GitHub stuff like pull requests working
- [x] Get checkstyle working and format the output
- [x] Form the prompt for single file refactoring.
- [x] Design smell detection
- [x] Write API code (pulls latest code after checking for changes in the specified repository to check for smells)
- [x] Write script for periodically checking repo
- [x] Write code for actually refactoring the code based on the smells suggested.
- [x] Compare with other gpt models (codex?)
- [x] Integrate code for creating branch and making pull request with `script.py` in scripts.
- [x] Modify the cronjob for making pull requests and publishing the new branch.
