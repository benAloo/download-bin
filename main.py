import os
import re
import requests

def parse_github_url(url):
    """
    Parses a standard GitHub browser URL to extract the owner, repo, branch, and path.
    Supported format: https://github.com
    """
    # Regex to extract owner, repo, branch, and folder path
    pattern = r"https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.*)"
    match = re.match(pattern, url)
    
    if not match:
        raise ValueError("Invalid GitHub URL format. Use the browser URL format: "
                         "https://github.com")
        
    return {
        "owner": match.group(1),
        "repo": match.group(2),
        "branch": match.group(3),
        "path": match.group(4)
    }

def download_github_folder(repo_url, target_folder, github_token=None):
    """
    Downloads all files from a specific GitHub folder using the GitHub API.
    """
    # Parse the URL
    url_parts = parse_github_url(repo_url)
    
    # FIX: Correct API Base URL (api.github.com) and proper slashes
    api_url = f"https://api.github.com/repos/{url_parts['owner']}/{url_parts['repo']}/contents/{url_parts['path']}"
    
    # Setup headers (including branch/ref and optional authentication token)
    # Added a standard User-Agent required by the GitHub API
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) GitHub Folder Downloader"
    }
    if github_token:
        headers["Authorization"] = f"token {github_token}"
        
    params = {"ref": url_parts["branch"]}
    
    print("Fetching folder contents from API...")
    response = requests.get(api_url, headers=headers, params=params)
    
    if response.status_code == 403:
        print("Error: API rate limit exceeded or access forbidden. "
              "If it's a private repo or rate limit issue, pass a github_token.")
        response.raise_for_status()
    elif response.status_code != 200:
        print(f"Error fetching data from GitHub API. Status code: {response.status_code}")
        response.raise_for_status()
        
    items = response.json()
    
    # Ensure local target directory exists
    os.makedirs(target_folder, exist_ok=True)
    
    # Download files loop
    downloaded_count = 0
    for item in items:
        # Only download files, skipping directories if any exist
        if item['type'] == 'file':
            file_name = item['name']
            download_url = item['download_url']
            local_file_path = os.path.join(target_folder, file_name)
            
            print(f"Downloading: {file_name}...")
            file_response = requests.get(download_url, headers=headers)
            
            if file_response.status_code == 200:
                with open(local_file_path, 'wb') as f:
                    f.write(file_response.content)
                downloaded_count += 1
            else:
                print(f"Failed to download {file_name}")
                
    print(f"\nSuccess! Downloaded {downloaded_count} files to '{target_folder}'.")

# --- Run Configuration ---
if __name__ == "__main__":
    # Your target URL containing the winutils binaries
    GITHUB_FOLDER_URL = "https://github.com/kontext-tech/winutils/tree/master/hadoop-3.4.0-win10-x64/bin"
    
    # The destination directory where files will be outputted
    TARGET_DIR = r"C:\Users\Admin\hadoop\bin"
    
    try:
        download_github_folder(GITHUB_FOLDER_URL, TARGET_DIR)
    except Exception as e:
        print(f"An error occurred: {e}")
