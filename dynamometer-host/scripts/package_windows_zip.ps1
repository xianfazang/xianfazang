# Package the PyInstaller one-file exe into a user-friendly zip.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Dist = Join-Path $Root "dist"
$ExeName = "测功机上位机.exe"
$ZipName = "测功机上位机-Mock.zip"
$ExePath = Join-Path $Dist $ExeName
$ZipPath = Join-Path $Dist $ZipName
$Stage = Join-Path $Dist "package-stage"

if (-not (Test-Path $ExePath)) {
    throw "Missing exe: $ExePath — run pyinstaller build_exe.spec first"
}

if (Test-Path $Stage) { Remove-Item -Recurse -Force $Stage }
New-Item -ItemType Directory -Force -Path $Stage | Out-Null
Copy-Item -LiteralPath $ExePath -Destination (Join-Path $Stage $ExeName)

if (Test-Path $ZipPath) { Remove-Item -Force $ZipPath }
Compress-Archive -LiteralPath (Join-Path $Stage $ExeName) -DestinationPath $ZipPath -Force
Write-Host "Created $ZipPath"
Get-Item -LiteralPath $ZipPath | Format-List Name, Length, FullName
