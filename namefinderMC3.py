import requests
import time
import os
import subprocess

# Paths to the input and output files
file_path = r"TestNameCheck.txt"
output_file_path = r"found_urls.txt"

# GitHub configuration (replace with your details)
username = "AaronTFrederick"
token = os.getenv("GITHUB_TOKEN")  # Store this securely
repo = "found_urls"
branch = "main"  # Adjust if necessary

# GitHub repository URL with token for authentication
repo_url = f"https://{username}:{token}@github.com/{username}/{repo}.git"

# Function to remove duplicate URLs from the output file
def remove_duplicates(output_file):
    if os.path.exists(output_file):
        with open(output_file, 'r') as file:
            urls = file.readlines()

        # Use a set to remove duplicates, then sort them (optional)
        unique_urls = sorted(set(url.strip() for url in urls))

        # Write the unique URLs back to the file
        with open(output_file, 'w') as file:
            for url in unique_urls:
                file.write(url + '\n')

# Function to commit and push changes to GitHub
def commit_and_push(file_path):
    commands = [
        ["git", "add", file_path],
        ["git", "commit", "-m", "Update found_urls.txt with new URLs"],
        ["git", "push", "origin", branch]
    ]

    # Initialize repository and set the remote URL if needed
    if not os.path.exists(".git"):
        subprocess.run(["git", "init"])
        subprocess.run(["git", "remote", "add", "origin", repo_url])

    # Execute Git commands
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Command {' '.join(command)} succeeded.")
        else:
            print(f"Command {' '.join(command)} failed with error:\n{result.stderr}")
            break

# Read URLs from the file
try:
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file.readlines()]
except FileNotFoundError:
    print(f"Error: The file at {file_path} was not found.")
    urls = []
except Exception as e:
    print(f"Error reading the file: {e}")
    urls = []

# Delay between requests in seconds
delay = 1

# Continuous loop
while True:
    # List to store found URLs for this loop iteration
    found_urls = []

    if urls:
        for url in urls:
            try:
                response = requests.get(url, verify=False)  # Disable SSL verification
                if response.status_code == 200:
                    content = response.text.lower()  # Convert content to lowercase
                elif response.status_code == 429:
                    print(f"Rate limited for {url}. Waiting before retrying...")
                    time.sleep(delay)
                    response = requests.get(url, verify=False)  # Retry the request
                    if response.status_code == 200:
                        content = response.text.lower()  # Convert content to lowercase
                        print(f"Successfully retrieved {url} after retry.")
                    else:
                        print(f"Failed to retrieve {url} after retry: Status Code {response.status_code}")
                else:
                    print(f"Found available name or locked {url}")
                    # Add the URL to the list of found URLs
                    found_urls.append(url)
            except requests.exceptions.RequestException as e:
                print(f"Error fetching {url}: {e}")

            time.sleep(delay)  # Introduce delay between requests

        # Append found URLs to the output file at the end of the loop
        with open(output_file_path, 'a') as output_file:
            for found_url in found_urls:
                output_file.write(found_url + '\n')

        print(f"Loop completed. Found URLs saved to {output_file_path}. Restarting...")

        # Remove duplicates from the output file
        remove_duplicates(output_file_path)

        # Commit and push the changes to GitHub
        commit_and_push(output_file_path)

    else:
        print("No URLs to process. Exiting loop.")
        break
