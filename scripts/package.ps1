param(
	[string]$Version = "1.2.1"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$addonDir = Join-Path $root ".addon"
$distDir = Join-Path $root "dist"
$buildDir = Join-Path $root "build"
$stageDir = Join-Path $buildDir "addon-package"
$packagePath = Join-Path $distDir "Video-ve-Ses-Indirici-$Version.nvda-addon"
$zipPath = Join-Path $distDir "Video-ve-Ses-Indirici-$Version.zip"

if (-not (Test-Path -LiteralPath $addonDir)) {
	throw "Add-on directory not found: $addonDir"
}

$manifestPath = Join-Path $addonDir "manifest.ini"
$manifestVersionLine = Get-Content -LiteralPath $manifestPath -Encoding UTF8 |
	Where-Object { $_ -match '^version\s*=\s*(.+)\s*$' } |
	Select-Object -First 1
if (-not $manifestVersionLine) {
	throw "Version not found in manifest: $manifestPath"
}
$manifestVersion = ([regex]::Match($manifestVersionLine, '^version\s*=\s*(.+?)\s*$')).Groups[1].Value
if ($Version -ne $manifestVersion) {
	throw "Package version '$Version' does not match manifest version '$manifestVersion'."
}

New-Item -ItemType Directory -Force -Path $distDir | Out-Null
New-Item -ItemType Directory -Force -Path $buildDir | Out-Null

if (Test-Path -LiteralPath $stageDir) {
	Remove-Item -LiteralPath $stageDir -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $stageDir | Out-Null

Get-ChildItem -LiteralPath $addonDir -Force | ForEach-Object {
	Copy-Item -LiteralPath $_.FullName -Destination $stageDir -Recurse -Force
}

# License and third-party notices must travel with the installed add-on, not
# only live beside the source repository.
Copy-Item -LiteralPath (Join-Path $root "LICENSE") -Destination (Join-Path $stageDir "LICENSE.txt") -Force
Copy-Item -LiteralPath (Join-Path $root "THIRD_PARTY_NOTICES.md") -Destination $stageDir -Force
Copy-Item -LiteralPath (Join-Path $root "thirdPartyLicenses") -Destination $stageDir -Recurse -Force

Get-ChildItem -LiteralPath $stageDir -Directory -Recurse -Force |
	Where-Object { $_.Name -eq "__pycache__" } |
	ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }

$unusedFfprobe = Join-Path $stageDir "bin\ffprobe.exe"
if (Test-Path -LiteralPath $unusedFfprobe) {
	Remove-Item -LiteralPath $unusedFfprobe -Force
}

if (Test-Path -LiteralPath $packagePath) {
	Remove-Item -LiteralPath $packagePath -Force
}
if (Test-Path -LiteralPath $zipPath) {
	Remove-Item -LiteralPath $zipPath -Force
}

$previousLocation = Get-Location
try {
	Set-Location -LiteralPath $stageDir
	Compress-Archive -Path * -DestinationPath $zipPath -CompressionLevel Optimal -Force
} finally {
	Set-Location $previousLocation
}

Move-Item -LiteralPath $zipPath -Destination $packagePath -Force

$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $packagePath
Write-Host "Package: $packagePath"
Write-Host "SHA256:  $($hash.Hash)"
