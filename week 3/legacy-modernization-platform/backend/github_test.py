import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_MODEL_REPO = os.getenv("GITHUB_MODEL_REPO")

if not GITHUB_TOKEN or not GITHUB_MODEL_REPO:
    print("ERROR: GITHUB_TOKEN or GITHUB_MODEL_REPO not set in .env")
    sys.exit(1)

def test_github_access():
    print(f"Testing access to GitHub Repository: {GITHUB_MODEL_REPO}...")
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    
    url = f"https://api.github.com/repos/{GITHUB_MODEL_REPO}"
    
    with httpx.Client() as client:
        response = client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(" GitHub PAT Authentication Successful!")
            print(f"Repository Full Name: {data.get('full_name')}")
            print(f"Default Branch: {data.get('default_branch')}")
            
            # Check for systems directory structure
            contents_url = f"https://api.github.com/repos/{GITHUB_MODEL_REPO}/contents/systems/system-demo/as-is"
            contents_res = client.get(contents_url, headers=headers)
            if contents_res.status_code == 200:
                layers = [item['name'] for item in contents_res.json() if item['type'] == 'dir']
                print(f" Discovered ArchiMate Layers: {', '.join(layers)}")
                return True
            else:
                print(f" Warning: Could not find /systems/system-demo/as-is path. Status: {contents_res.status_code}")
                return True
        else:
            print(f"GitHub API Request Failed ({response.status_code}): {response.text}")
            return False

if __name__ == "__main__":
    success = test_github_access()
    if not success:
        sys.exit(1)
