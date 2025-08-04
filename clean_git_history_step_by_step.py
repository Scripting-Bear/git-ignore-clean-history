#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import shutil
import inquirer
import fnmatch
import argparse
from pathlib import Path

# ----------------- Config -------------------

GIT_FILTER_REPO_URL = "https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo"
GIT_FILTER_REPO_SCRIPT = "git-filter-repo.py"

# --------------------------------------------

def run(command, **kwargs):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **kwargs)
    if result.returncode != 0:
        print(result.stderr.strip())
        sys.exit(result.returncode)
    return result.stdout.strip()

def extract_all_paths(temp_dir, verbose=False):
    all_files_path = os.path.join(temp_dir, "all-ever-files.txt")
    if verbose:
        print("📦 Step 1: Extracting all files ever committed...")

    with open(all_files_path, "w", encoding="utf-8") as f:
        subprocess.run(["git", "log", "--all", "--pretty=format:", "--name-only"], stdout=f)

    with open(all_files_path, encoding="utf-8") as f:
        paths = sorted(set(line.strip() for line in f if line.strip()))

    if verbose:
        print(f"✅ Extracted {len(paths)} unique file paths.")
    return paths, all_files_path

def parse_gitignore_patterns(verbose=False):
    ignore_file = ".gitignore"
    if not os.path.exists(ignore_file):
        print("⚠️ No .gitignore found.")
        return []

    with open(ignore_file, encoding="utf-8") as f:
        patterns = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if verbose:
        print(f"✅ Found {len(patterns)} ignore patterns.")
    return patterns

def match_paths(paths, patterns, verbose=False):
    matched = []
    for path in paths:
        for pattern in patterns:
            if fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch(path, f"**/{pattern}"):
                matched.append(path)
                break
    if verbose:
        print(f"✅ Matched {len(matched)} files.")
    return matched

def write_to_file(lines, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def ensure_git_filter_repo(temp_dir, verbose=False):
    if not shutil.which("git-filter-repo"):
        target_path = os.path.join(temp_dir, GIT_FILTER_REPO_SCRIPT)
        if verbose:
            print("📥 Downloading git-filter-repo...")
        run(["curl", "-sSL", "-o", target_path, GIT_FILTER_REPO_URL])
        return ["python", target_path]
    return ["git-filter-repo"]

def confirm(prompt):
    answer = input(f"{prompt} [y/N]: ").strip().lower()
    return answer == "y"

def main():
    parser = argparse.ArgumentParser(description="Clean Git history of files that should be ignored.")
    parser.add_argument("--verbose", action="store_true", help="Show verbose logs")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temp files after execution")
    args = parser.parse_args()

    temp_dir = tempfile.mkdtemp(prefix="git-clean-")

    try:
        paths, all_file_path = extract_all_paths(temp_dir, verbose=args.verbose)

        if not confirm("👀 Do you want to continue to match these files with .gitignore?"):
            print("❌ Cancelled.")
            return

        patterns = parse_gitignore_patterns(verbose=args.verbose)
        matched = match_paths(paths, patterns, verbose=args.verbose)

        files_to_remove_path = os.path.join(temp_dir, "files-to-remove.txt")
        write_to_file(matched, files_to_remove_path)

        if matched:
            print(f"📝 Matches written to: {files_to_remove_path}")
            if confirm("⚠️ Do you want to clean them from history?"):
                filter_repo_cmd = ensure_git_filter_repo(temp_dir, verbose=args.verbose)
                run(filter_repo_cmd + [
                    "--paths-from-file", files_to_remove_path,
                    "--invert-paths", "--force"
                ])
                print("✅ History cleaned. You may now force-push.")
            else:
                print("❌ Skipped history cleaning.")
        else:
            print("🎉 No matched files found in history. Nothing to clean.")

    finally:
        if args.keep_temp:
            print(f"🗂️ Temporary files kept at: {temp_dir}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
