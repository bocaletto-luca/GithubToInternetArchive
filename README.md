# GitHub Archiver to Internet Archive

A single-file Python tool (`main.py`) that mirrors every repository of a GitHub user or organization and uploads each mirror as a tarball to Internet Archive. Metadata (description, license, topics) are automatically pulled from GitHub and attached to each upload.

---

## Features

- Fetch all public repos for a GitHub user/org via the GitHub API  
- Clone or update each repo as a bare mirror (`git clone --mirror`)  
- Package each mirror into a `tar.gz` archive  
- Push archives to archive.org under your chosen collection  
- Embed rich metadata (repo description, SPDX license URL, topics)  
- Clean up local mirrors by default (optional `--keep-mirror`)  
- Zero external scripts—everything lives in one `main.py`  

---

## Prerequisites

- **Python 3.7+**  
- **git** CLI on your `PATH`  
- **A GitHub Personal Access Token (PAT)** with `repo` scope  
- **An Internet Archive account** with an Access Key & Secret Key  

Python dependencies (install in a virtual environment):

```bash
pip install PyGithub internetarchive
```

---

## Installation

1. Clone this repo:

   ```bash
   git clone https://github.com/bocaletto-luca/github-archiver.git
   cd github-archiver
   ```

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install Python requirements:

   ```bash
   pip install -r requirements.txt
   ```

4. Make the script executable:

   ```bash
   chmod +x main.py
   ```

---

## Configuration

### GitHub Token

Export your GitHub PAT to the environment:

```bash
export GITHUB_TOKEN="ghp_your_personal_access_token"
```

### Internet Archive Credentials

Configure the `internetarchive` CLI once:

```bash
pip install internetarchive
ia configure
```

You will be prompted for your **Access Key** and **Secret Key**—these are stored in `~/.netrc`.

---

## Usage

```bash
./main.py \
  --github-user bocaletto-luca \
  --github-token "${GITHUB_TOKEN}" \
  --ia-collection github-archive \
  [--output-dir ./backups] \
  [--keep-mirror]
```

Options:

- `--github-user`  GitHub username or org (e.g. `bocaletto-luca`)  
- `--github-token` GitHub PAT with `repo` scope  
- `--ia-collection` Target Internet Archive collection (e.g. `github-archive`)  
- `--output-dir`    Local folder to store mirrors & tarballs (default `./backups`)  
- `--keep-mirror`   Do not delete the local mirror after upload  

### Example: Full Run

```bash
export GITHUB_TOKEN="ghp_ABC123..."
ia configure     # set IA_ACCESS_KEY & IA_SECRET_KEY
./main.py \
  --github-user bocaletto-luca \
  --github-token "$GITHUB_TOKEN" \
  --ia-collection github-archive
```

This will:

1. Fetch all repos under `bocaletto-luca`  
2. Mirror or update each as `./backups/<repo>.git`  
3. Create `./backups/<repo>.git.tar.gz`  
4. Upload to `archive.org/details/github-archive__<repo>`  
5. Clean up the local mirror  

---

## How It Works

1. **GitHub API**  
   The script uses `PyGithub` to list all repositories for the given user/org.  

2. **Mirroring**  
   Each repo is cloned (or updated) as a bare mirror. This preserves all branches, tags, PR refs, etc.  

3. **Archiving**  
   Mirrors are compressed into `tar.gz` files for efficient upload.  

4. **Uploading**  
   The `internetarchive` Python client pushes the tarball to archive.org, adding:
   - **title**: `username/repo mirror`  
   - **description**: the repo’s GitHub description  
   - **licenseurl** (if SPDX license is set)  
   - **subject**: GitHub topics as tags  
   - **collection** and **mediatype**  

5. **Cleanup**  
   By default, local mirrors are removed after upload. Use `--keep-mirror` to retain them.

---

## Repository Structure

```text
github-archiver/
├── LICENSE
├── main.py
├── requirements.txt
└── README.md
```

- **main.py**         – all-in-one script  
- **requirements.txt** – Python dependencies  
- **LICENSE**          – GPL-3.0 License  
- **README.md**        – this documentation  

---

## Author

**Luca Bocaletto**  
GitHub: [@bocaletto-luca](https://github.com/bocaletto-luca)  

---

## License

Distributed under the **GPL-3.0 License**. See [LICENSE](LICENSE) for details.  
```
