@echo off
REM ============================================
REM AUTOMATED GITHUB SETUP SCRIPT (WINDOWS)
REM ============================================

echo ========================================
echo Crypto Analyzer - GitHub Setup Script
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed!
    echo.
    echo Please install Git first from: https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [OK] Git is installed
echo.

REM Check if in correct directory
if not exist "README.md" (
    echo [ERROR] README.md not found!
    echo Please run this script from the crypto-analyzer-improved directory
    pause
    exit /b 1
)

if not exist "backend" (
    echo [ERROR] backend directory not found!
    echo Please run this script from the crypto-analyzer-improved directory
    pause
    exit /b 1
)

echo [OK] Running in correct directory
echo.

REM Get GitHub username
set /p GITHUB_USERNAME="Enter your GitHub username: "

if "%GITHUB_USERNAME%"=="" (
    echo [ERROR] Username cannot be empty!
    pause
    exit /b 1
)

REM Get repository name
set REPO_NAME=crypto-analyzer-improved
set /p REPO_INPUT="Enter repository name (press Enter for 'crypto-analyzer-improved'): "
if not "%REPO_INPUT%"=="" set REPO_NAME=%REPO_INPUT%

echo.
echo Repository will be created at:
echo https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
set /p CONFIRM="Is this correct? (y/n): "

if /i not "%CONFIRM%"=="y" (
    echo [CANCELLED] Setup cancelled
    pause
    exit /b 0
)

REM Initialize git repository
echo.
echo [INFO] Initializing Git repository...

if exist ".git" (
    echo [WARNING] Git repository already exists
) else (
    git init
    echo [OK] Git initialized
)

REM Configure git user if needed
git config user.name >nul 2>&1
if errorlevel 1 (
    echo.
    echo [INFO] Git user not configured. Let's set it up!
    set /p GIT_NAME="Enter your name: "
    set /p GIT_EMAIL="Enter your email: "
    
    git config user.name "!GIT_NAME!"
    git config user.email "!GIT_EMAIL!"
    echo [OK] Git user configured
)

REM Add all files
echo.
echo [INFO] Adding files to git...
git add .
echo [OK] Files added

REM Create initial commit
echo.
echo [INFO] Creating initial commit...
git commit -m "Initial commit: Improved crypto analyzer with enhanced security and features"
echo [OK] Commit created

REM Rename branch to main
echo.
echo [INFO] Renaming branch to 'main'...
git branch -M main
echo [OK] Branch renamed

REM Add remote
echo.
echo [INFO] Adding GitHub remote...
set REMOTE_URL=https://github.com/%GITHUB_USERNAME%/%REPO_NAME%.git

git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin %REMOTE_URL%
) else (
    git remote set-url origin %REMOTE_URL%
)

echo [OK] Remote added: %REMOTE_URL%

REM Instructions
echo.
echo ============================================
echo IMPORTANT: Create GitHub Repository First!
echo ============================================
echo.
echo 1. Open this URL in your browser:
echo    https://github.com/new
echo.
echo 2. Fill in the form:
echo    - Repository name: %REPO_NAME%
echo    - Description: Professional cryptocurrency analyzer
echo    - Visibility: Public (or Private)
echo    - DO NOT initialize with README, .gitignore, or license
echo.
echo 3. Click 'Create repository'
echo.
pause

REM Push to GitHub
echo.
echo [INFO] Pushing to GitHub...
echo.
echo You will be asked for credentials:
echo   - Username: %GITHUB_USERNAME%
echo   - Password: Use Personal Access Token (NOT password)
echo.
echo Create token: https://github.com/settings/tokens/new
echo.
pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed!
    echo.
    echo Common issues:
    echo.
    echo 1. Authentication failed
    echo    - Use Personal Access Token, not password
    echo    - Create: https://github.com/settings/tokens/new
    echo.
    echo 2. Repository doesn't exist
    echo    - Create it first: https://github.com/new
    echo.
    echo 3. Permission denied
    echo    - Check username and repository name
    echo.
    echo To retry: git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo SUCCESS!
echo ============================================
echo.
echo Your code is now on GitHub!
echo.
echo Repository: https://github.com/%GITHUB_USERNAME%/%REPO_NAME%
echo.
echo Next steps:
echo   1. Visit your repository
echo   2. Read README.md
echo   3. Follow DEPLOYMENT.md
echo.
pause
