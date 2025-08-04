#!/usr/bin/env node

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

try {
    const scriptPath = path.join(__dirname, "clean_git_history_step_by_step.py");
    execSync(`python "${scriptPath}" ${process.argv.slice(2).join(" ")}`, {
        stdio: "inherit",
    });
} catch (err) {
    console.error("❌ Failed to run the Python script.");
    process.exit(1);
}
