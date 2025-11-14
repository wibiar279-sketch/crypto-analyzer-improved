#!/bin/bash

# ============================================
# AUTOMATED GITHUB DEPLOYMENT WITH TOKEN
# ============================================
# This script will deploy your code to GitHub automatically
# using your Personal Access Token

echo "🚀 Crypto Analyzer - Automated GitHub Deployment"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
GITHUB_TOKEN="YOUR_GITHUB_TOKEN_HERE"
GITHUB_USERNAME="wibiar279-sketch"
REPO_NAME="crypto-analyzer-improved"
REPO_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo -e "${YELLOW}⚠️  IMPORTANT SECURITY NOTICE ⚠️${NC}"
echo "This script contains your Personal Access Token."
echo "After deployment, you should:"
echo "1. Delete this script"
echo "2. Revoke the token: https://github.com/settings/tokens"
echo "3. Create a new token for future use"
echo ""
read -p "Press Enter to continue..."
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗ Git is not installed!${NC}"
    echo "Please install Git first:"
    echo "  - Mac: brew install git"
    echo "  - Linux: sudo apt-get install git"
    exit 1
fi

echo -e "${GREEN}✓ Git is installed${NC}"

# Check if in correct directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}✗ Please run this script from the crypto-analyzer-improved directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Running in correct directory${NC}"
echo ""

# Configure git user
echo "Configuring Git user..."
git config user.name "$GITHUB_USERNAME"
git config user.email "wibiar279@gmail.com"
echo -e "${GREEN}✓ Git user configured${NC}"
echo ""

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
    echo -e "${GREEN}✓ Git initialized${NC}"
else
    echo -e "${GREEN}✓ Git already initialized${NC}"
fi
echo ""

# Add all files
echo "Adding files..."
git add .
echo -e "${GREEN}✓ Files added${NC}"
echo ""

# Create commit
echo "Creating commit..."
git commit -m "Initial commit: Improved crypto analyzer with enhanced security and features"
echo -e "${GREEN}✓ Commit created${NC}"
echo ""

# Rename branch to main
echo "Renaming branch to main..."
git branch -M main
echo -e "${GREEN}✓ Branch renamed${NC}"
echo ""

# Add remote (or update if exists)
echo "Setting up remote repository..."
if git remote get-url origin &> /dev/null; then
    git remote set-url origin "$REPO_URL"
else
    git remote add origin "$REPO_URL"
fi
echo -e "${GREEN}✓ Remote configured${NC}"
echo ""

# Create repository on GitHub if it doesn't exist
echo "Checking if repository exists on GitHub..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME")

if [ "$HTTP_CODE" = "404" ]; then
    echo "Repository doesn't exist. Creating it..."
    
    CREATE_RESPONSE=$(curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"$REPO_NAME\",\"description\":\"Professional cryptocurrency analyzer with improved security and features\",\"private\":false}" \
        "https://api.github.com/user/repos")
    
    if echo "$CREATE_RESPONSE" | grep -q "\"full_name\""; then
        echo -e "${GREEN}✓ Repository created successfully${NC}"
    else
        echo -e "${YELLOW}⚠ Could not create repository automatically${NC}"
        echo "Please create it manually:"
        echo "1. Go to: https://github.com/new"
        echo "2. Repository name: $REPO_NAME"
        echo "3. Click 'Create repository'"
        echo ""
        read -p "Press Enter after creating the repository..."
    fi
elif [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Repository already exists${NC}"
else
    echo -e "${YELLOW}⚠ Could not verify repository (HTTP $HTTP_CODE)${NC}"
    echo "Continuing anyway..."
fi
echo ""

# Push to GitHub
echo "Pushing to GitHub..."
echo "This may take a moment..."
echo ""

if git push -u origin main; then
    echo ""
    echo "============================================"
    echo -e "${GREEN}✅ SUCCESS! Code deployed to GitHub!${NC}"
    echo "============================================"
    echo ""
    echo "Repository URL:"
    echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "1. ✅ Visit your repository"
    echo "2. ✅ Verify all files are there"
    echo "3. ⚠️  REVOKE this token: https://github.com/settings/tokens"
    echo "4. ✅ Create a new token for future use"
    echo "5. ✅ Delete this script (contains token!)"
    echo ""
    echo "To delete this script:"
    echo "  rm deploy-to-github.sh"
    echo ""
else
    echo ""
    echo -e "${RED}✗ Push failed!${NC}"
    echo ""
    echo "Possible issues:"
    echo "1. Network connectivity"
    echo "2. Repository permissions"
    echo "3. Token has expired or wrong scopes"
    echo ""
    echo "Manual alternative:"
    echo "1. Create repo: https://github.com/new"
    echo "2. Run: git push -u origin main"
    echo "3. When asked for password, use your token"
    echo ""
    exit 1
fi

# Clean up - remove token from git config
echo "Cleaning up..."
git remote set-url origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo -e "${GREEN}✓ Token removed from git config${NC}"
echo ""

echo "============================================"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "============================================"
echo ""
echo -e "${YELLOW}🔐 SECURITY REMINDER:${NC}"
echo "This script contains your token. Please:"
echo "1. Delete this script NOW: rm deploy-to-github.sh"
echo "2. Revoke the token: https://github.com/settings/tokens"
echo "3. Never share tokens in public"
echo ""
