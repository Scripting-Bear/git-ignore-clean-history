import subprocess
import pathlib
import fnmatch
import os
import sys
import urllib.request

ALL_FILES = "all-ever-files.txt"
FILES_TO_REMOVE = "files-to-remove.txt"
FILTER_REPO_SCRIPT = "git-filter-repo.py"
FILTER_REPO_URL = "https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo"

# Set global verbose flag
VERBOSE = "--verbose" in sys.argv

def confirm(prompt):
    return input(f"{prompt} [y/N]: ").strip().lower() == 'y'

def get_all_git_files(output_file):
    print("\n📦 Step 1: Extracting all files ever committed...")
    cmd = ["git", "log", "--all", "--pretty=format:", "--name-only"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    files = set(line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip())
    with open(output_file, "w", encoding="utf-8") as f:
        for file in sorted(files):
            f.write(f"{file}\n")
    print(f"✅ Extracted {len(files)} unique file paths to '{output_file}'.")

def parse_gitignore(gitignore_path):
    if VERBOSE:
        print("\n🔍 Reading .gitignore patterns...")
    patterns = []
    with open(gitignore_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line.replace("\\", "/"))
    if VERBOSE:
        print(f"✅ Found patterns: {patterns}")
    else:
        print(f"✅ Found {len(patterns)} ignore patterns.")
    return patterns

def match_files_to_ignore(all_files_path, patterns):
    if VERBOSE:
        print("\n🔎 Matching files against .gitignore...")
    matches = []
    with open(all_files_path, "r", encoding="utf-8") as f:
        for path in f:
            path = path.strip().replace("\\", "/")
            if not path:
                continue
            for pattern in patterns:
                if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"**/{pattern}"):
                    matches.append(path)
                    break
    print(f"✅ Matched {len(matches)} files.")
    return sorted(set(matches))

def write_matches(matches, output_file):
    with open(output_file, "w", encoding="utf-8") as f:
        for path in matches:
            f.write(f"{path}\n")

    if VERBOSE and matches:
        print(f"\n📝 Preview of matches to be removed from history:")
        for path in matches[:20]:
            print(f"  - {path}")
        if len(matches) > 20:
            print(f"  ...and {len(matches)-20} more.")
    else:
        print(f"📝 Matches written to '{output_file}'.")

def download_filter_repo(script_path):
    print(f"\n🌐 Downloading '{FILTER_REPO_SCRIPT}' from official GitHub...")
    try:
        urllib.request.urlretrieve(FILTER_REPO_URL, script_path)
        print(f"✅ Downloaded and saved as '{script_path}'.")
    except Exception as e:
        print(f"❌ Failed to download filter-repo script: {e}")
        sys.exit(1)

def run_git_filter_repo(files_to_remove):
    print("\n⚙️ Step 4: Running git-filter-repo...")
    cmd = [
        sys.executable, FILTER_REPO_SCRIPT,
        "--paths-from-file", files_to_remove,
        "--invert-paths",
        "--force"
    ]
    result = subprocess.run(cmd)
    if result.returncode == 0:
        print("✅ Repo history successfully cleaned.")
    else:
        print("❌ Error running git-filter-repo.")

def main():
    if not pathlib.Path(".gitignore").exists():
        print("❌ No .gitignore file found. Exiting.")
        sys.exit(1)

    if not pathlib.Path(FILTER_REPO_SCRIPT).exists():
        print(f"⚠️ '{FILTER_REPO_SCRIPT}' not found in the current directory.")
        if confirm("🌍 Do you want to download it now from GitHub?"):
            download_filter_repo(FILTER_REPO_SCRIPT)
        else:
            print("🛑 Aborting.")
            sys.exit(0)

    # Step 1
    get_all_git_files(ALL_FILES)
    if not confirm("👀 Do you want to continue to match these files with .gitignore?"):
        print("🛑 Aborting.")
        sys.exit(0)

    # Step 2
    patterns = parse_gitignore(".gitignore")
    matches = match_files_to_ignore(ALL_FILES, patterns)
    write_matches(matches, FILES_TO_REMOVE)

    if not matches:
        print("🎉 No matched files found in history. Nothing to clean.")
        sys.exit(0)

    if not confirm("❗ Do you want to proceed and remove these files from history? This rewrites the repo."):
        print("🛑 Aborting before modifying history.")
        sys.exit(0)

    # Step 3
    run_git_filter_repo(FILES_TO_REMOVE)

    print("\n💡 Final step: You can now force push to update the remote (optional):")
    print("   git push origin --force --all")
    print("✅ Done.")

if __name__ == "__main__":
    main()
