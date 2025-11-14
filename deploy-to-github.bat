@echo off
REM ============================================
REM AUTOMATED GITHUB DEPLOYMENT WITH TOKEN (WINDOWS)
REM ============================================

echo ================================================
echo Crypto Analyzer - Automated GitHub Deployment
echo ================================================
echo.

REM Configuration
set GITHUB_TOKEN=YOUR_GITHUB_TOKEN_HERE
set GITHUB_USERNAME=wibiar279-sketch
set REPO_NAME=crypto-analyzer-improved

echo [WARNING] SECURITY NOTICE
echo This script contains your Personal Access Token.
echo After deployment, you should:
echo 1. Delete this script
echo 2. Revoke the token: https://github.com/settings/tokens
echo 3. Create a new token for future use
echo.
pause
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo [OK] Git is installed
echo.

REM Check if in correct directory
if not exist "README.md" (
    echo [ERROR] Please run this script from crypto-analyzer-improved directory
    pause
    exit /b 1
)

echo [OK] Running in correct directory
echo.

REM Configure git user
echo Configuring Git user...
git config user.name "%GITHUB_USERNAME%"
git config user.email "wibiar279@gmail.com"
echo [OK] Git user configured
echo.

REM Initialize git if needed
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo [OK] Git initialized
) else (
    echo [OK] Git already initialized
)
echo.

REM Add all files
echo Adding files...
git add .
echo [OK] Files added
echo.

REM Create commit
echo Creating commit...
git commit -m "Initial commit: Improved crypto analyzer with enhanced security and features"
echo [OK] Commit created
echo.

REM Rename branch to main
echo Renaming branch to main...
git branch -M main
echo [OK] Branch renamed
echo.

REM Add remote
echo Setting up remote repository...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin https://%GITHUB_TOKEN%@github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
) else (
    git remote set-url origin https://%GITHUB_TOKEN%@github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
)
echo [OK] Remote configured
echo.

REM Try to create repository if it doesn't exist
echo Checking if repository exists...
echo Note: If repository doesn't exist, please create it manually at:
echo https://github.com/new
echo Repository name: %REPO_NAME%
echo Visibility: Public
echo.
pause
echo.

REM Push to GitHub
echo Pushing to GitHub...
echo This may take a moment...
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed!
    echo.
    echo Possible solutions:
    echo 1. Create repository manually: https://github.com/new
    echo 2. Check your internet connection
    echo 3. Verify token has correct permissions
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! Code deployed to GitHub!
echo ================================================
echo.
echo Repository URL:
echo https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
echo Next steps:
echo 1. Visit your repository
echo 2. Verify all files are there
echo 3. REVOKE this token: https://github.com/settings/tokens
echo 4. Create a new token for future use
echo 5. DELETE this script (contains token!)
echo.
echo To delete this script:
echo   del deploy-to-github.bat
echo.

REM Clean up - remove token from git config
echo Cleaning up...
git remote set-url origin https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git
echo [OK] Token removed from git config
echo.

echo ================================================
echo DEPLOYMENT COMPLETE!
echo ================================================
echo.
echo [SECURITY REMINDER]
echo This script contains your token. Please:
echo 1. Delete this script NOW: del deploy-to-github.bat
echo 2. Revoke the token: https://github.com/settings/tokens
echo 3. Never share tokens in public
echo.
pause
