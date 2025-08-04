# 🧹 Git Ignore Clean History

**Remove previously committed files that should have been ignored via `.gitignore`** — interactively and safely.

### 🔗 npx:

```bash
npx @scripting-bear/git-ignore-clean-history
````

---

## 💡 Why?

Ever cloned a repo and realized:

* Someone committed `node_modules`, `.env`, `.DS_Store`, or `Pods/`?
* Now the repo is **bloated**, slow, and filled with junk?

This tool helps you:

✅ Analyze your Git history
✅ Match committed files against `.gitignore`
✅ Confirm what should be deleted
✅ Safely rewrite history with [`git-filter-repo`](https://github.com/newren/git-filter-repo)

---

## ⚙️ What It Does (Steps)

1. **Extract all files ever committed** in Git history
2. **Match them against `.gitignore` rules** (including deep paths)
3. Prompt you to confirm
4. Run `git-filter-repo` to **remove them from history**
5. You force-push a clean repo ✨

---

## 🧪 Example

```bash
npx @scripting-bear/git-ignore-clean-history --verbose
```

Interactive output:

```
📦 Step 1: Extracting all files ever committed...
✅ Extracted 20,387 unique file paths to 'all-ever-files.txt'.

👀 Do you want to continue to match these files with .gitignore? [y/N]: y
✅ Found 37 ignore patterns.
✅ Matched 643 files.
📝 Matches written to 'files-to-remove.txt'.

⚠️ Do you want to clean them from history? [y/N]: y
```

---

## 🛠 Requirements

* Git installed
* Python 3.6+
* [`git-filter-repo`](https://github.com/newren/git-filter-repo)

If `git-filter-repo` is missing, the tool will prompt to download it.

---

## 👤 Author

Made with frustration by [@scripting-bear](https://github.com/scripting-bear)

🤝 With technical assistance, scripting support & optimization from ChatGPT by OpenAI.

---

## 🙌 Inspired by

* [git-filter-repo](https://github.com/newren/git-filter-repo)
* [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)

---

> 🔒 Note: This tool rewrites history. Push your cleaned repo **with force**, and share a note with collaborators.
