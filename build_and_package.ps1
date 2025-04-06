#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Builds the Millennium Faceit Stats plugin and packages it into a ZIP file.
.DESCRIPTION
    This script performs the following operations:
    1. Builds the plugin using npm run build
    2. Creates a temporary directory for packaging
    3. Copies essential files to the temporary directory
    4. Creates a ZIP archive with the package
    5. Cleans up temporary files
.NOTES
    Version:        1.0
    Author:         Script Generator
    Creation Date:  2025-04-06
#>

# Enable strict mode to catch common scripting errors
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Configuration variables
$tempDirName = "temp_package"
$pluginFolderName = "alowave.faceit_stats"  # Folder name inside the ZIP (from plugin.json "name" field)

# Function to display status messages
function Write-Status {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] $Message" -ForegroundColor Cyan
}

# Function to display error messages
function Write-ErrorMessage {
    param([string]$Message)
    Write-Host "[$((Get-Date).ToString('HH:mm:ss'))] ERROR: $Message" -ForegroundColor Red
}

# Install and use pnpm for dependencies
Write-Status "Checking for pnpm..."
if (-not (Get-Command "pnpm" -ErrorAction SilentlyContinue)) {
    try {
        Write-Status "Installing pnpm "
        npm install 
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to install pnpm."
        }
    } catch {
        Write-ErrorMessage "Failed to install pnpm. Please install it manually."
        exit 1
    }
}

# Install dependencies with pnpm
Write-Status "Installing dependencies using pnpm..."
try {
    pnpm install
    if ($LASTEXITCODE -ne 0) {
        throw "pnpm install failed."
    }
} catch {
    Write-ErrorMessage "Failed to install dependencies: $($_.Exception.Message)"
    exit 1
}
# Read package.json to get the name and version
if (-not (Test-Path "package.json")) {
    throw "package.json file not found in the current directory."
}
try {
    $packageJson = Get-Content -Path "package.json" -Raw | ConvertFrom-Json
    
    # Check if required fields exist
    if (-not (Get-Member -InputObject $packageJson -Name "name" -MemberType Properties)) {
        throw "The 'name' field is missing from package.json."
    }
    if (-not (Get-Member -InputObject $packageJson -Name "version" -MemberType Properties)) {
        throw "The 'version' field is missing from package.json."
    }
    
    $packageName = $packageJson.name
    $packageVersion = $packageJson.version
    
    Write-Status "Using package name: '$packageName' and version: '$packageVersion' from package.json"
} 
catch {
    throw "Failed to parse package.json: $($_.Exception.Message)"
}

$zipFileName = "$packageName-$packageVersion.zip"

# Main script execution
try {
    # Step 1: Build the plugin
    Write-Status "Building the plugin using 'npm run build'..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }
    Write-Status "Build completed successfully."
    
    # Step 2: Create temporary directory for packaging
    Write-Status "Creating temporary directory for packaging..."
    if (Test-Path $tempDirName) {
        Remove-Item -Path $tempDirName -Recurse -Force
    }
    New-Item -Path $tempDirName -ItemType Directory | Out-Null
    
    # Create the plugin folder inside the temp directory
    Write-Status "Creating plugin folder '$pluginFolderName' inside temporary directory..."
    New-Item -Path "$tempDirName/$pluginFolderName" -ItemType Directory | Out-Null
    
    # Step 3: Copy essential files to the plugin folder in the temporary directory
    Write-Status "Copying plugin.json to plugin folder..."
    Copy-Item -Path "plugin.json" -Destination "$tempDirName/$pluginFolderName"
    
    Write-Status "Copying compiled JavaScript files from .millennium/Dist/..."
    if (-not (Test-Path ".millennium/Dist")) {
        throw "Directory .millennium/Dist not found. Build may have failed."
    }
    
    # Create the necessary directory structure in the plugin folder
    New-Item -Path "$tempDirName/$pluginFolderName/.millennium/Dist" -ItemType Directory -Force | Out-Null
    Copy-Item -Path ".millennium/Dist/*" -Destination "$tempDirName/$pluginFolderName/.millennium/Dist" -Recurse
    
    Write-Status "Copying static directory and its contents..."
    if (-not (Test-Path "static")) {
        throw "Static directory not found."
    }
    Copy-Item -Path "static" -Destination "$tempDirName/$pluginFolderName" -Recurse
    
    Write-Status "Copying backend directory and its contents..."
    if (-not (Test-Path "backend")) {
        throw "Backend directory not found."
    }
    Copy-Item -Path "backend" -Destination "$tempDirName/$pluginFolderName" -Recurse
    
    # Step 4: Create ZIP archive
    Write-Status "Creating ZIP archive '$zipFileName'..."
    if (Test-Path $zipFileName) {
        Remove-Item -Path $zipFileName -Force
    }
    
    # Use Compress-Archive to create the ZIP file
    Compress-Archive -Path "$tempDirName/*" -DestinationPath $zipFileName
    
    if (-not (Test-Path $zipFileName)) {
        throw "Failed to create ZIP archive."
    }
    
    Write-Status "ZIP archive created successfully: $zipFileName"
    
    # Step 5: Clean up temporary directory
    Write-Status "Cleaning up temporary directory..."
    Remove-Item -Path $tempDirName -Recurse -Force
    
    Write-Status "Plugin packaging completed successfully!"
}
catch {
    Write-ErrorMessage $_.Exception.Message
    
    # Cleanup on error
    if (Test-Path $tempDirName) {
        Write-Status "Cleaning up temporary directory after error..."
        Remove-Item -Path $tempDirName -Recurse -Force
    }
    
    exit 1
}

