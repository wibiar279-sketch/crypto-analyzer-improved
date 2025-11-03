#!/bin/bash

# ============================================
# AUTOMATED GITHUB SETUP SCRIPT
# ============================================

echo "🚀 Crypto Analyzer - GitHub Setup Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed!"
    echo "Please install Git first:"
    echo "  - Windows: https://git-scm.com/download/win"
    echo "  - Mac: brew install git"
    echo "  - Linux: sudo apt-get install git"
    exit 1
fi

print_success "Git is installed"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    print_error "Please run this script from the crypto-analyzer-improved directory!"
    exit 1
fi

print_success "Running in correct directory"

# Get GitHub username
echo ""
print_info "Enter your GitHub username:"
read -p "Username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    print_error "Username cannot be empty!"
    exit 1
fi

# Get repository name (default: crypto-analyzer-improved)
echo ""
print_info "Enter repository name (press Enter for 'crypto-analyzer-improved'):"
read -p "Repository name: " REPO_NAME
REPO_NAME=${REPO_NAME:-crypto-analyzer-improved}

# Confirm
echo ""
print_warning "Repository will be created at:"
echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
read -p "Is this correct? (y/n): " CONFIRM

if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
    print_error "Setup cancelled"
    exit 1
fi

# Initialize git repository
echo ""
print_info "Initializing Git repository..."

if [ -d ".git" ]; then
    print_warning "Git repository already exists. Skipping initialization."
else
    git init
    print_success "Git initialized"
fi

# Configure git user (if not configured)
if [ -z "$(git config user.name)" ]; then
    echo ""
    print_info "Git user not configured. Let's set it up!"
    read -p "Enter your name: " GIT_NAME
    read -p "Enter your email: " GIT_EMAIL
    
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    print_success "Git user configured"
fi

# Add all files
echo ""
print_info "Adding files to git..."
git add .
print_success "Files added"

# Create initial commit
echo ""
print_info "Creating initial commit..."
git commit -m "Initial commit: Improved crypto analyzer with enhanced security and features"
print_success "Commit created"

# Rename branch to main (if needed)
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_info "Renaming branch to 'main'..."
    git branch -M main
    print_success "Branch renamed to 'main'"
fi

# Add remote
echo ""
print_info "Adding GitHub remote..."
REMOTE_URL="https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"

# Check if remote already exists
if git remote get-url origin &> /dev/null; then
    print_warning "Remote 'origin' already exists. Updating..."
    git remote set-url origin "$REMOTE_URL"
else
    git remote add origin "$REMOTE_URL"
fi

print_success "Remote added: $REMOTE_URL"

# Instructions for creating repository
echo ""
echo "============================================"
print_warning "IMPORTANT: Create GitHub Repository First!"
echo "============================================"
echo ""
echo "1. Open this URL in your browser:"
echo "   ${BLUE}https://github.com/new${NC}"
echo ""
echo "2. Fill in the form:"
echo "   - Repository name: ${GREEN}$REPO_NAME${NC}"
echo "   - Description: Professional cryptocurrency analyzer"
echo "   - Visibility: ${YELLOW}Public${NC} (or Private if you prefer)"
echo "   - ${RED}DO NOT${NC} initialize with README, .gitignore, or license"
echo ""
echo "3. Click '${GREEN}Create repository${NC}'"
echo ""
read -p "Press Enter after creating the repository on GitHub..."

# Push to GitHub
echo ""
print_info "Pushing to GitHub..."
echo ""
print_warning "You will be asked for your GitHub credentials:"
echo "  - Username: $GITHUB_USERNAME"
echo "  - Password: Use your ${YELLOW}Personal Access Token${NC} (NOT your GitHub password)"
echo ""
echo "Don't have a token? Create one here:"
echo "  ${BLUE}https://github.com/settings/tokens/new${NC}"
echo ""
read -p "Press Enter to continue..."

# Attempt push
if git push -u origin main; then
    echo ""
    echo "============================================"
    print_success "SUCCESS! 🎉"
    echo "============================================"
    echo ""
    print_success "Your code is now on GitHub!"
    echo ""
    echo "Repository URL:"
    echo "  ${GREEN}https://github.com/$GITHUB_USERNAME/$REPO_NAME${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Visit your repository"
    echo "  2. Read the README.md"
    echo "  3. Follow DEPLOYMENT.md to deploy"
    echo ""
else
    echo ""
    print_error "Push failed!"
    echo ""
    echo "Common issues and solutions:"
    echo ""
    echo "1. ${YELLOW}Authentication failed${NC}"
    echo "   - Make sure you're using a Personal Access Token, not your password"
    echo "   - Create token: https://github.com/settings/tokens/new"
    echo "   - Required scopes: 'repo', 'workflow'"
    echo ""
    echo "2. ${YELLOW}Repository doesn't exist${NC}"
    echo "   - Make sure you created the repository on GitHub first"
    echo "   - URL: https://github.com/new"
    echo ""
    echo "3. ${YELLOW}Permission denied${NC}"
    echo "   - Check that repository name matches: $REPO_NAME"
    echo "   - Check that username matches: $GITHUB_USERNAME"
    echo ""
    echo "To retry, run this script again or use:"
    echo "  ${BLUE}git push -u origin main${NC}"
    echo ""
fi
