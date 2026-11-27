# 02 Global Installer for Antigravity
# Copies/links the 02 skill into ~/.gemini/config/plugins/02 so it is available globally in any project.

$ErrorActionPreference = "Stop"

$sourceDir = $PSScriptRoot
$geminiConfigDir = Join-Path $env:USERPROFILE ".gemini\config\plugins\02"
$geminiSkillsDir = Join-Path $geminiConfigDir "skills\02"

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "      Installing 02 Skill Globally into Antigravity      " -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan

# 1. Create global plugin target directory
if (-not (Test-Path $geminiSkillsDir)) {
    New-Item -ItemType Directory -Path $geminiSkillsDir -Force | Out-Null
    Write-Host "[+] Created plugin directory: $geminiSkillsDir" -ForegroundColor Green
}

# 2. Write plugin.json manifest
$pluginManifest = @{
    "name" = "02-autonomous-team"
    "description" = "Universal 02 Autonomous Production Team Engine"
    "version" = "1.0.0"
} | ConvertTo-Json

Set-Content -Path (Join-Path $geminiConfigDir "plugin.json") -Value $pluginManifest
Write-Host "[+] Generated plugin.json manifest" -ForegroundColor Green

# 3. Copy files to global plugin location
Copy-Item -Path (Join-Path $sourceDir "SKILL.md") -Destination $geminiSkillsDir -Force
Copy-Item -Path (Join-Path $sourceDir "scripts") -Destination $geminiSkillsDir -Recurse -Force
Copy-Item -Path (Join-Path $sourceDir "references") -Destination $geminiSkillsDir -Recurse -Force

Write-Host "[+] Copied SKILL.md, scripts, and references to global plugin location." -ForegroundColor Green
Write-Host ""
Write-Host "[OK] 02 Autonomous Team is now installed globally!" -ForegroundColor Yellow
Write-Host "     You can now call 'activate 02' or '/02' in ANY project or directory." -ForegroundColor Yellow
Write-Host "=========================================================" -ForegroundColor Cyan
