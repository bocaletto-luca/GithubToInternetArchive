#!/usr/bin/env python3
"""
main.py

Mirror all repositories of a GitHub user/org and upload them to Internet Archive.

This is a single‐file tool. It will:
  1. Query GitHub for all repos of a user/org.
  2. Clone each repo as a bare mirror (or update it if exists).
  3. Create a tarball of the mirror.
  4. Upload the tarball to archive.org under your specified collection,
     embedding metadata (title, description, license, topics).

Dependencies (install in a venv):
  pip install PyGithub internetarchive

Usage:
  ./main.py \
    --github-user YOUR_GH_USER \
    --github-token YOUR_GH_TOKEN \
    --ia-collection YOUR_IA_COLLECTION \
    [--output-dir ./backups] \
    [--keep-mirror] 

Options:
  --github-user       GitHub username or org name
  --github-token      GitHub Personal Access Token (with repo scope)
  --ia-collection     Archive.org collection name (e.g. github-archive)
  --output-dir        Local directory to store mirrors & tarballs (default: ./backups)
  --keep-mirror       Do not delete the local mirror after upload
  -h, --help          Show this help message and exit

Example:
  ./main.py \
    --github-user bocaletto-luca \
    --github-token ghp_xxx123 \
    --ia-collection github-archive \
    --output-dir ./backups
"""

import os
import sys
import argparse
import subprocess
import tempfile
import shutil
from pathlib import Path

from github import Github
import internetarchive as ia

def die(msg, code=1):
    """Print error and exit."""
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)

def run(cmd, cwd=None):
    """Run a shell command, die on non-zero exit."""
    print(f"> {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd)
    if res.returncode != 0:
        die(f"Command failed: {' '.join(cmd)}")

def fetch_repos(user, token):
    """Return a list of all repos for the given GitHub user/org."""
    gh = Github(token)
    try:
        org = gh.get_user(user)
    except Exception as e:
        die(f"GitHub lookup failed for '{user}': {e}")
    return list(org.get_repos())

def mirror_repo(repo, mirror_base, token):
    """
    Clone or update a bare mirror.
    Returns Path to the .git mirror directory.
    """
    dest = mirror_base / f"{repo.name}.git"
    clone_url = repo.clone_url.replace('https://',
        f"https://{token}@")
    if dest.exists():
        print(f"Updating mirror '{repo.name}'")
        run(["git", "remote", "update"], cwd=dest)
    else:
        print(f"Cloning mirror '{repo.name}'")
        run(["git", "clone", "--mirror", clone_url, str(dest)])
    return dest

def make_tarball(mirror_path, output_dir):
    """
    Create a tar.gz archive of the mirror directory.
    Returns Path to the tarball.
    """
    name = mirror_path.name  # e.g. "repo.git"
    tarball = output_dir / f"{name}.tar.gz"
    if tarball.exists():
        print(f"Removing old tarball {tarball.name}")
        tarball.unlink()
    print(f"Creating tarball {tarball.name}")
    run([
        "tar", "czf", str(tarball),
        "-C", str(output_dir), name
    ])
    return tarball

def upload_to_ia(tarball, repo, collection, user):
    """
    Upload the tarball to archive.org, embedding metadata.
    Metadata is taken from GitHub repo fields.
    """
    item_id = f"{collection}__{repo.name}"
    print(f"Uploading '{tarball.name}' to Archive.org as '{item_id}'")
    metadata = {
        "collection": collection,
        "title":      f"{user}/{repo.name} mirror",
        "description": repo.description or "",
        "mediatype":  "data",
    }
    # Include license if available
    if repo.license and repo.license.spdx_id != "NOASSERTION":
        metadata["licenseurl"] = f"https://spdx.org/licenses/{repo.license.spdx_id}.html"
    # Include topics/tags
    topics = repo.get_topics()
    if topics:
        metadata["subject"] = topics

    ia.upload(
        item_id,
        files=[str(tarball)],
        metadata=metadata,
        retries=3
    )
    print(f"✔ Successfully uploaded '{item_id}'\n")

def main():
    parser = argparse.ArgumentParser(
        description="Mirror GitHub repos and upload to archive.org"
    )
    parser.add_argument("--github-user", required=True,
                        help="GitHub username or org")
    parser.add_argument("--github-token", required=True,
                        help="GitHub Personal Access Token with repo scope")
    parser.add_argument("--ia-collection", required=True,
                        help="Archive.org collection name")
    parser.add_argument("--output-dir", default="./backups",
                        help="Local directory to store mirrors & tarballs")
    parser.add_argument("--keep-mirror", action="store_true",
                        help="Do not delete local mirror directories")
    args = parser.parse_args()

    # Prepare local directory
    base = Path(args.output_dir).absolute()
    base.mkdir(parents=True, exist_ok=True)

    # Load repos
    repos = fetch_repos(args.github_user, args.github_token)
    print(f"Found {len(repos)} repos in '{args.github_user}'\n")

    for repo in repos:
        try:
            mirror_dir = mirror_repo(repo, base, args.github_token)
            tarball = make_tarball(mirror_dir, base)
            upload_to_ia(tarball, repo,
                         args.ia_collection,
                         args.github_user)
            if not args.keep_mirror:
                print(f"Cleaning up mirror '{mirror_dir.name}'")
                shutil.rmtree(mirror_dir, ignore_errors=True)
        except Exception as e:
            print(f"❌ Error processing '{repo.name}': {e}", file=sys.stderr)

    print("All done.")

if __name__ == "__main__":
    main()
