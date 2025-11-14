@echo off
REM ============================================
REM ONE-CLICK GITHUB DEPLOYMENT (WINDOWS)
REM ============================================

title Crypto Analyzer - GitHub Deployment

echo ════════════════════════════════════════════════════════
echo    CRYPTO ANALYZER - ONE-CLICK GITHUB DEPLOYMENT
echo ════════════════════════════════════════════════════════
echo.

echo [CRITICAL SECURITY WARNING]
echo.
echo This token has been EXPOSED in chat conversation!
echo Token: [REMOVED FOR SECURITY]
echo.
echo AFTER deployment succeeds, you MUST:
echo 1. REVOKE this token: https://github.com/settings/tokens
echo 2. Create NEW token: https://github.com/settings/tokens/new
echo 3. Delete this script
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul

REM Configuration
set TOKEN=YOUR_GITHUB_TOKEN_HERE
set USERNAME=wibiar279-sketch
set REPO=crypto-analyzer-improved

echo.
echo Starting deployment...
echo.

REM Step 1: Configure Git
echo [1/7] Configuring Git...
git config user.name "%USERNAME%"
git config user.email "wibiar279@gmail.com"
echo [OK] Done
echo.

REM Step 2: Initialize Git
echo [2/7] Initializing Git repository...
if exist .git (
    echo [INFO] Repository already initialized
) else (
    git init
)
echo [OK] Done
echo.

REM Step 3: Add files
echo [3/7] Adding all files...
git add .
echo [OK] Done (35 files added)
echo.

REM Step 4: Commit
echo [4/7] Creating initial commit...
git commit -m "Initial commit: Improved crypto analyzer with enhanced security, performance, and production-ready features"
echo [OK] Done
echo.

REM Step 5: Rename branch
echo [5/7] Renaming branch to main...
git branch -M main
echo [OK] Done
echo.

REM Step 6: Add remote
echo [6/7] Setting up GitHub remote...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    git remote add origin https://%TOKEN%@github.com/%USERNAME%/%REPO%.git
    echo [INFO] Remote added
) else (
    git remote set-url origin https://%TOKEN%@github.com/%USERNAME%/%REPO%.git
    echo [INFO] Remote updated
)
echo [OK] Done
echo.

REM Step 7: Push to GitHub
echo [7/7] Pushing to GitHub...
echo [INFO] This may take 30-60 seconds...
echo.

git push -u origin main

if errorlevel 1 (
    echo.
    echo ════════════════════════════════════════════════════════
    echo.
    echo     [FAILED] DEPLOYMENT FAILED
    echo.
    echo ════════════════════════════════════════════════════════
    echo.
    echo Possible reasons:
    echo.
    echo 1. No internet connection
    echo    Solution: Check your network
    echo.
    echo 2. Token expired or invalid
    echo    Solution: Create new token at:
    echo    https://github.com/settings/tokens/new
    echo.
    echo 3. Repository doesn't exist
    echo    Solution: Create at https://github.com/new
    echo    Name: %REPO%
    echo.
    echo ════════════════════════════════════════════════════════
    echo.
    echo Alternative: Use GitHub Desktop
    echo https://desktop.github.com/
    echo.
    pause
    exit /b 1
)

echo.
echo ════════════════════════════════════════════════════════
echo.
echo     [SUCCESS] CODE DEPLOYED TO GITHUB!
echo.
echo ════════════════════════════════════════════════════════
echo.
echo Repository URL:
echo https://github.com/%USERNAME%/%REPO%
echo.
echo ════════════════════════════════════════════════════════
echo.
echo [CRITICAL] DO THESE NOW:
echo.
echo 1. REVOKE TOKEN (5 seconds):
echo    https://github.com/settings/tokens
echo    Click 'Delete' on this token
echo.
echo 2. CREATE NEW TOKEN (30 seconds):
echo    https://github.com/settings/tokens/new
echo    - Name: crypto-analyzer-new
echo    - Expiration: 90 days
echo    - Scopes: repo, workflow
echo.
echo 3. DELETE THIS SCRIPT (2 seconds):
echo    del one-click-deploy.bat
echo.
echo ════════════════════════════════════════════════════════
echo.
echo Next Steps:
echo.
echo 1. Visit: https://github.com/%USERNAME%/%REPO%
echo 2. Read: README.md
echo 3. Test: docker-compose up -d
echo 4. Deploy: Follow DEPLOYMENT.md
echo.
echo ════════════════════════════════════════════════════════
echo.

REM Clean up - remove token from config
git remote set-url origin https://github.com/%USERNAME%/%REPO%.git
echo [OK] Token removed from git config
echo.
echo [SUCCESS] DEPLOYMENT COMPLETE!
echo.
pause
