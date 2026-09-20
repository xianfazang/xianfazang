# Package the PyInstaller one-file exe into a user-friendly zip.
# Zip filename is ASCII-safe for GitHub Release asset URLs; exe inside stays Chinese.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Dist = Join-Path $Root "dist"
$ExeName = "测功机上位机.exe"
$ZipName = "dynamometer-host-Mock.zip"
$ExePath = Join-Path $Dist $ExeName
$ZipPath = Join-Path $Dist $ZipName
$Stage = Join-Path $Dist "package-stage"

if (-not (Test-Path -LiteralPath $ExePath)) {
    throw "Missing exe: $ExePath — run pyinstaller build_exe.spec first"
}

if (Test-Path -LiteralPath $Stage) { Remove-Item -LiteralPath $Stage -Recurse -Force }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null
Copy-Item -LiteralPath $ExePath -Destination (Join-Path $Stage $ExeName)

if (Test-Path -LiteralPath $ZipPath) { Remove-Item -LiteralPath $ZipPath -Force }
Compress-Archive -LiteralPath (Join-Path $Stage $ExeName) -DestinationPath $ZipPath -Force
Write-Host "Created $ZipPath"
Get-Item -LiteralPath $ZipPath | Format-List Name, Length, FullName
