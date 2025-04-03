import os
import requests
import zipfile
import io
import sys

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
GITHUB_REPO = os.environ.get("GITHUB_REPO", "yourusername/yourrepo")
PR_NUMBER = os.environ.get("READTHEDOCS_GIT_IDENTIFIER")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

runs_resp = requests.get(
    f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs",
    headers=headers,
    params={"event": "pull_request", "branch": f"refs/pull/{PR_NUMBER}/merge"}
)
runs_resp.raise_for_status()
runs_data = runs_resp.json()

if not runs_data["workflow_runs"]:
    print("No workflow runs found for this PR.")
    sys.exit(1)

run_id = runs_data["workflow_runs"][0]["id"]
artifacts_resp = requests.get(
    f"https://api.github.com/repos/{GITHUB_REPO}/actions/runs/{run_id}/artifacts",
    headers=headers
)
artifacts_resp.raise_for_status()
artifacts_data = artifacts_resp.json()

wheel_artifact = next(
    (a for a in artifacts_data["artifacts"] if a["name"] == "wheel"), None
)

if not wheel_artifact:
    print("Wheel artifact not found.")
    sys.exit(1)

download_resp = requests.get(
    wheel_artifact["archive_download_url"], headers=headers
)
download_resp.raise_for_status()

with zipfile.ZipFile(io.BytesIO(download_resp.content)) as zf:
    zf.extractall("wheel_artifact")

print("Artifact downloaded and extracted successfully.")