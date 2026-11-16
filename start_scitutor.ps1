
# ============================================
# SciTutor Workbench - Hotspot Launcher
# Automatically detects current Wi-Fi IPv4
# Updates only the SciTutor firewall rule
# ============================================

$ErrorActionPreference = "Stop"

$ProjectDir = $PSScriptRoot
$Python = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$FirewallRuleName = "SciTutor-Hotspot-8000"
$InterfaceAlias = "Wi-Fi"
$Port = 8000

Write-Host "`n=== SciTutor Workbench Launcher ===" -ForegroundColor Cyan

# 1. Check Administrator
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = [Security.Principal.WindowsPrincipal]::new($identity)

$isAdmin = $principal.IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

if (-not $isAdmin) {
    throw "Please run PowerShell as Administrator."
}

# 2. Check project files
if (-not (Test-Path $Python)) {
    throw "Project Python executable not found: $Python"
}

if (-not (Test-Path (Join-Path $ProjectDir "backend\main.py"))) {
    throw "backend\main.py not found."
}

if (-not (Test-Path (Join-Path $ProjectDir "frontend\index.html"))) {
    throw "frontend\index.html not found."
}

# 3. Detect current Wi-Fi IPv4 and gateway
$ipConfig = Get-NetIPConfiguration -InterfaceAlias $InterfaceAlias

$ipv4 = $ipConfig.IPv4Address |
    Where-Object { $_.IPAddress -notlike "169.254.*" } |
    Select-Object -First 1

$gateway = $ipConfig.IPv4DefaultGateway |
    Select-Object -First 1

if ($null -eq $ipv4 -or $null -eq $gateway) {
    throw "Wi-Fi has no valid IPv4 address or default gateway."
}

$CurrentIP = $ipv4.IPAddress
$PrefixLength = [int]$ipv4.PrefixLength

if ($PrefixLength -lt 1 -or $PrefixLength -gt 30) {
    throw "Unexpected Wi-Fi subnet prefix: /$PrefixLength"
}

# 4. Calculate current IPv4 subnet
$ipBytes = [System.Net.IPAddress]::Parse($CurrentIP).GetAddressBytes()
$networkBytes = New-Object byte[] 4

for ($i = 0; $i -lt 4; $i++) {
    $remainingBits = $PrefixLength - ($i * 8)

    if ($remainingBits -ge 8) {
        $mask = 255
    }
    elseif ($remainingBits -le 0) {
        $mask = 0
    }
    else {
        $mask = 256 - [math]::Pow(2, 8 - $remainingBits)
    }

    $networkBytes[$i] = [byte]($ipBytes[$i] -band [int]$mask)
}

$NetworkIP = ([System.Net.IPAddress]::new($networkBytes)).ToString()
$CurrentSubnet = "$NetworkIP/$PrefixLength"

# 5. Confirm Public firewall profile is enabled
$publicProfile = Get-NetFirewallProfile -Profile Public

if (-not $publicProfile.Enabled) {
    throw "Windows Firewall Public profile is disabled. No automatic changes made."
}

# Confirm the currently connected Wi-Fi uses the Public profile
$connectionProfiles = @(
    Get-NetConnectionProfile -InterfaceAlias $InterfaceAlias -ErrorAction Stop
)

if ($connectionProfiles.Count -ne 1) {
    throw "Could not identify exactly one active Wi-Fi network profile."
}

if ($connectionProfiles[0].NetworkCategory -ne "Public") {
    throw "Current Wi-Fi network is not Public. No network profile changes were made."
}

# 6. Check port availability
$listener = Get-NetTCPConnection `
    -LocalPort $Port `
    -State Listen `
    -ErrorAction SilentlyContinue

if ($listener) {
    throw "Port $Port is already in use. Stop the existing server before continuing."
}

# 7. Find existing SciTutor firewall rule
$rule = Get-NetFirewallRule `
    -Name $FirewallRuleName `
    -ErrorAction SilentlyContinue

if ($null -eq $rule) {

    # Create only the dedicated SciTutor rule
    New-NetFirewallRule `
        -Name $FirewallRuleName `
        -DisplayName "SciTutor FastAPI - Hotspot Wi-Fi only" `
        -Description "Allow SciTutor FastAPI from the current Wi-Fi subnet only" `
        -Direction Inbound `
        -Action Allow `
        -Enabled True `
        -Profile Public `
        -Program $Python `
        -Protocol TCP `
        -LocalPort $Port `
        -LocalAddress $CurrentIP `
        -RemoteAddress $CurrentSubnet `
        -InterfaceAlias $InterfaceAlias | Out-Null

}
else {

    # Verify the existing rule targets this project's Python
    $appFilter = $rule | Get-NetFirewallApplicationFilter

    if ($appFilter.Program -ne $Python) {
        throw "Existing SciTutor firewall rule has an unexpected program path. No changes made."
    }

    # Verify the existing rule targets TCP port 8000
    $portFilter = $rule | Get-NetFirewallPortFilter

    if (
        $portFilter.Protocol -ne "TCP" -or
        "$($portFilter.LocalPort)" -ne "$Port"
    ) {
        throw "Existing SciTutor firewall rule has an unexpected port configuration. No changes made."
    }

    # Update only this rule
    Set-NetFirewallRule `
        -Name $FirewallRuleName `
        -Enabled True `
        -Profile Public `
        -Direction Inbound `
        -Action Allow

    $rule | Get-NetFirewallAddressFilter |
        Set-NetFirewallAddressFilter `
            -LocalAddress $CurrentIP `
            -RemoteAddress $CurrentSubnet

    $rule | Get-NetFirewallInterfaceFilter |
        Set-NetFirewallInterfaceFilter `
            -InterfaceAlias $InterfaceAlias
}

# 8. Display current network information
Write-Host "`n=== Current Network ===" -ForegroundColor Cyan
Write-Host "Interface : $InterfaceAlias"
Write-Host "IPv4      : $CurrentIP"
Write-Host "Gateway   : $($gateway.NextHop)"
Write-Host "Subnet    : $CurrentSubnet"
Write-Host "Port      : $Port"

Write-Host "`n=== SciTutor URL ===" -ForegroundColor Green
Write-Host "http://${CurrentIP}:$Port/" -ForegroundColor Green
Write-Host "http://${CurrentIP}:$Port/health" -ForegroundColor Green

Write-Host "`nStarting FastAPI..." -ForegroundColor Cyan

# 9. Start Uvicorn using the current DHCP address
Set-Location $ProjectDir

& $Python -m uvicorn backend.main:app `
    --host $CurrentIP `
    --port $Port
