
$ErrorActionPreference = "Stop"

# ============================================================
# CONFIGURATION
# ============================================================

$project = "C:\Users\Tarot Club\Documents\SciTutor-Workbench02"
Set-Location -LiteralPath $project

$pythonExe = Join-Path $project ".venv\Scripts\python.exe"

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $project "backups\ollama-cleanup-$timestamp"

$configPath = Join-Path $project "backend\core\config.py"
$architecturePath = Join-Path $project "docs\architecture.md"
$viewerPath = Join-Path $project "frontend\js\code-viewer.js"

$targets = @(
    $configPath,
    $architecturePath,
    $viewerPath
)

$backupFiles = @(
    @{
        Source = $configPath
        Name = "config.py"
    },
    @{
        Source = $architecturePath
        Name = "architecture.md"
    },
    @{
        Source = $viewerPath
        Name = "code-viewer.js"
    }
)

$modified = $false
$backupComplete = $false

# ============================================================
# PRE-CHECK
# ============================================================

Write-Host "`n========== PRE-CHECK ==========" -ForegroundColor Cyan

if (-not (Test-Path -LiteralPath $project -PathType Container)) {
    throw "Project directory not found: $project"
}

if (-not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    throw "Project Python not found: $pythonExe"
}

foreach ($path in $targets) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required file not found: $path"
    }

    Write-Host "FOUND: $path"
}

Write-Host "`nPython executable:"
Write-Host $pythonExe

& $pythonExe --version

if ($LASTEXITCODE -ne 0) {
    throw "Project Python could not run. No project files changed."
}

# ============================================================
# READ ORIGINAL FILES
# ============================================================

$configText = Get-Content -LiteralPath $configPath -Raw
$architectureText = Get-Content -LiteralPath $architecturePath -Raw
$viewerText = Get-Content -LiteralPath $viewerPath -Raw

# ============================================================
# PREPARE CHANGES
# ============================================================

Write-Host "`n========== CHANGE PREVIEW ==========" -ForegroundColor Cyan

# ต้องพบ gemini_api_key assignment เพียงหนึ่งรายการ
$configPattern = '(?im)^[ \t]*gemini_api_key[ \t]*=.*(?:\r?\n|$)'
$configMatches = [regex]::Matches($configText, $configPattern)

if ($configMatches.Count -ne 1) {
    throw "Expected exactly one gemini_api_key assignment. Found: $($configMatches.Count). No files changed."
}

# ตรวจว่า architecture มีข้อความเดิมจริง
if ($architectureText -notmatch '(?i)Gemini') {
    throw "Expected Gemini reference not found in architecture.md. No files changed."
}

# เตรียม Config ใหม่
$newConfigText = [regex]::Replace(
    $configText,
    $configPattern,
    '',
    [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
)

# เปลี่ยนคำอธิบายใน Architecture
$newArchitectureText = [regex]::Replace(
    $architectureText,
    '(?i)Gemini',
    'Ollama'
)

# เปลี่ยนเฉพาะข้อความเดิมใน Code Viewer
$viewerPattern = '(?i)Gemini grounded response service'
$viewerFound = [regex]::IsMatch($viewerText, $viewerPattern)

$newViewerText = [regex]::Replace(
    $viewerText,
    $viewerPattern,
    'Ollama grounded response service'
)

Write-Host "Config: remove gemini_api_key"
Write-Host "Architecture: Gemini -> Ollama"
Write-Host "Code Viewer target found: $viewerFound"

# ============================================================
# BACKUP
# ============================================================

Write-Host "`n========== BACKUP ==========" -ForegroundColor Cyan

New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

foreach ($item in $backupFiles) {
    Copy-Item `
        -LiteralPath $item.Source `
        -Destination (Join-Path $backupDir $item.Name) `
        -Force

    Write-Host "BACKED UP: $($item.Name)"
}

# ตรวจสอบว่า Backup ครบทั้งสามไฟล์
foreach ($item in $backupFiles) {
    $backupPath = Join-Path $backupDir $item.Name

    if (-not (Test-Path -LiteralPath $backupPath -PathType Leaf)) {
        throw "Backup verification failed: $($item.Name)"
    }

    $originalHash = (Get-FileHash -LiteralPath $item.Source -Algorithm SHA256).Hash
    $backupHash = (Get-FileHash -LiteralPath $backupPath -Algorithm SHA256).Hash

    if ($originalHash -ne $backupHash) {
        throw "Backup hash mismatch: $($item.Name)"
    }

    Write-Host "BACKUP VERIFIED: $($item.Name)"
}

$backupComplete = $true

Write-Host "Backup folder: $backupDir"

# ============================================================
# APPLY CLEANUP AND VALIDATE
# ============================================================

try {

    Write-Host "`n========== APPLY CLEANUP ==========" -ForegroundColor Cyan

    # เปิดสิทธิ์ Rollback ก่อนเขียนไฟล์แรก
    $modified = $true

    Set-Content -LiteralPath $configPath -Value $newConfigText -Encoding UTF8
    Write-Host "REMOVED: gemini_api_key assignment"

    Set-Content -LiteralPath $architecturePath -Value $newArchitectureText -Encoding UTF8
    Write-Host "UPDATED: architecture.md Gemini -> Ollama"

    if ($viewerFound) {
        Set-Content -LiteralPath $viewerPath -Value $newViewerText -Encoding UTF8
        Write-Host "UPDATED: code-viewer.js Gemini -> Ollama"
    }
    else {
        Write-Host "UNCHANGED: code-viewer.js"
    }

    # ========================================================
    # PYTHON VALIDATION
    # ========================================================

    Write-Host "`n========== PYTHON VALIDATION ==========" -ForegroundColor Cyan

    $validatorPath = Join-Path $backupDir "validate_cleanup.py"

    $validatorCode = @'
import ast
import importlib
import pathlib
import sys

project = pathlib.Path(sys.argv[1])
sys.path.insert(0, str(project))

files = [
    project / "backend" / "core" / "config.py",
    project / "backend" / "services" / "ollama_service.py",
    project / "backend" / "api" / "routes.py",
]

for path in files:
    source = path.read_text(encoding="utf-8-sig")
    ast.parse(source, filename=str(path))
    print(f"SYNTAX PASSED: {path.relative_to(project)}")

for module_name in (
    "backend.core.config",
    "backend.services.ollama_service",
    "backend.api.routes",
):
    importlib.import_module(module_name)
    print(f"IMPORT PASSED: {module_name}")

print("INFERENCE: NOT CALLED")
'@

    Set-Content -LiteralPath $validatorPath -Value $validatorCode -Encoding UTF8

    & $pythonExe $validatorPath $project

    if ($LASTEXITCODE -ne 0) {
        throw "Python validation failed with exit code $LASTEXITCODE"
    }

    # ========================================================
    # FILE VERIFICATION
    # ========================================================

    Write-Host "`n========== CLEANUP VERIFICATION ==========" -ForegroundColor Cyan

    $configAfter = Get-Content -LiteralPath $configPath -Raw
    $architectureAfter = Get-Content -LiteralPath $architecturePath -Raw
    $viewerAfter = Get-Content -LiteralPath $viewerPath -Raw

    if ($configAfter -match '(?i)gemini_api_key') {
        throw "gemini_api_key still exists in config.py"
    }

    if ($architectureAfter -match '(?i)Gemini') {
        throw "Gemini reference still exists in architecture.md"
    }

    if ($viewerAfter -match '(?i)Gemini') {
        throw "Gemini reference still exists in code-viewer.js"
    }

    Write-Host "CONFIG: PASSED"
    Write-Host "ARCHITECTURE: PASSED"
    Write-Host "CODE VIEWER: PASSED"

    # ========================================================
    # PROJECT-WIDE TEXT AUDIT
    # ========================================================

    Write-Host "`n========== PROJECT-WIDE GEMINI AUDIT ==========" -ForegroundColor Cyan

    $excluded = @(
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "vector_db",
        "uploads",
        "backups"
    )

    $extensions = @(
        ".py", ".pyw", ".js", ".mjs", ".cjs",
        ".ts", ".tsx", ".jsx", ".html", ".htm",
        ".css", ".json", ".jsonc", ".toml", ".ini",
        ".cfg", ".yaml", ".yml", ".md", ".txt",
        ".rst", ".ps1", ".bat", ".cmd", ".sh",
        ".sql", ".xml", ".svg", ".properties",
        ".lock"
    )

    $remaining = @()

    Get-ChildItem -LiteralPath $project -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object {
        $relative = $_.FullName.Substring($project.Length).TrimStart('\')
        $parts = $relative -split '\\'

        ($extensions -contains $_.Extension.ToLower()) -and
        -not ($parts | Where-Object { $excluded -contains $_ }) -and
        $_.Length -le 5MB
    } |
    ForEach-Object {

        $file = $_

        $hits = Select-String `
            -LiteralPath $file.FullName `
            -Pattern 'gemini' `
            -ErrorAction SilentlyContinue

        foreach ($hit in $hits) {
            $remaining += [PSCustomObject]@{
                File = $file.FullName.Substring($project.Length + 1)
                Line = $hit.LineNumber
            }
        }
    }

    Write-Host "Remaining Gemini matching lines: $($remaining.Count)"

    if ($remaining.Count -gt 0) {
        $remaining | Format-Table -AutoSize

        Write-Host "REVIEW REQUIRED: remaining references may be historical or active." -ForegroundColor Yellow
    }
    else {
        Write-Host "No Gemini text references found in scanned current project files."
    }

    # ========================================================
    # SUCCESS
    # ========================================================

    Write-Host "`n========== CLEANUP SUCCESS ==========" -ForegroundColor Green

    Write-Host "Backup: $backupDir"
    Write-Host "Files modified: YES"
    Write-Host "Files deleted: NO"
    Write-Host "Backup files deleted: NO"
    Write-Host "Inference: NOT CALLED"
    Write-Host "Backend restart: NOT PERFORMED"

}
catch {

    Write-Host "`n========== VALIDATION FAILED ==========" -ForegroundColor Red
    Write-Host $_.Exception.Message

    if ($modified -and $backupComplete) {

        Write-Host "`nRestoring original files from verified backup..." -ForegroundColor Yellow

        foreach ($item in $backupFiles) {

            $backupPath = Join-Path $backupDir $item.Name

            Copy-Item `
                -LiteralPath $backupPath `
                -Destination $item.Source `
                -Force

            $restoredHash = (Get-FileHash -LiteralPath $item.Source -Algorithm SHA256).Hash
            $backupHash = (Get-FileHash -LiteralPath $backupPath -Algorithm SHA256).Hash

            if ($restoredHash -ne $backupHash) {
                throw "ROLLBACK VERIFICATION FAILED: $($item.Name)"
            }

            Write-Host "RESTORED AND VERIFIED: $($item.Name)"
        }

        Write-Host "ROLLBACK COMPLETE" -ForegroundColor Green
        Write-Host "Backup retained: $backupDir"
    }
    else {
        Write-Host "No project files were modified."
    }

    throw "Cleanup did not pass validation. Do not restart backend."
}
