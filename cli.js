#!/usr/bin/env node

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

function checkCommandExists(cmd) {
    try {
        execSync(`${cmd} --version`, { stdio: "ignore" });
        return true;
    } catch {
        return false;
    }
}

function ensurePythonDependencies() {
    try {
        execSync('python -c "import inquirer, pathspec"', { stdio: "ignore" });
    } catch {
        console.log("🔧 Python packages not found. Installing...");
        try {
            execSync("pip install inquirer pathspec", { stdio: "inherit" });
        } catch (e) {
            console.error("❌ Failed to install required Python packages.");
            process.exit(1);
        }
    }
}

function runPythonScript() {
    const scriptPath = path.join(__dirname, "clean_git_history_step_by_step.py");
    const args = process.argv.slice(2).join(" ");
    try {
        execSync(`python "${scriptPath}" ${args}`, { stdio: "inherit" });
    } catch (err) {
        console.error("❌ Failed to run the Python script.");
        process.exit(1);
    }
}

// --- Main Flow ---

if (!checkCommandExists("python")) {
    console.error("❌ Python is not installed or not in PATH.");
    process.exit(1);
}

if (!checkCommandExists("pip")) {
    console.error("❌ pip is not installed or not in PATH.");
    process.exit(1);
}

ensurePythonDependencies();
runPythonScript();
