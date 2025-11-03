# ⚡ Quick Reference Card

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
docker-compose logs -f backend  # Specific service

# Stop services
docker-compose stop

# Stop and remove
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Restart specific service
docker-compose restart backend

# View running containers
docker-compose ps

# Execute command in container
docker-compose exec backend flask db upgrade
docker-compose exec backend python

# Access database
docker-compose exec db psql -U postgres -d crypto_analyzer

# Access Redis CLI
docker-compose exec redis redis-cli
```

## 🐍 Python/Flask Commands

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
python src/main.py

# Run with environment variables
FLASK_ENV=development python src/main.py

# Database migrations
flask db init              # First time only
flask db migrate -m "description"
flask db upgrade
flask db downgrade

# Run tests
pytest
pytest -v                  # Verbose
pytest --cov=src          # With coverage
pytest tests/test_api.py  # Specific file

# Code quality
black src/                # Format code
flake8 src/              # Lint code
pylint src/              # Detailed lint
```

## 📦 Node/Frontend Commands

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Lint
npm run lint
```

## 🗃️ Database Commands

```bash
# PostgreSQL
psql -U postgres -d crypto_analyzer

# Common SQL queries
SELECT * FROM trading_pairs LIMIT 10;
SELECT COUNT(*) FROM analysis_results;
SELECT * FROM analysis_results ORDER BY timestamp DESC LIMIT 5;

# Backup database
pg_dump -U postgres crypto_analyzer > backup.sql

# Restore database
psql -U postgres crypto_analyzer < backup.sql
```

## 🔴 Redis Commands

```bash
# Connect to Redis
redis-cli

# Common Redis commands
KEYS *                    # List all keys
GET key_name             # Get value
DEL key_name             # Delete key
FLUSHALL                 # Clear all data
INFO                     # Server info
MONITOR                  # Watch commands in real-time
```

## 🐙 Git Commands

```bash
# Initial setup
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USER/REPO.git
git push -u origin main

# Daily workflow
git status
git add .
git commit -m "Description of changes"
git push

# Branch operations
git checkout -b feature-name
git checkout main
git merge feature-name
git branch -d feature-name

# Undo changes
git reset --hard HEAD     # Discard all changes
git reset HEAD~1          # Undo last commit
git revert <commit-hash>  # Revert specific commit

# View history
git log
git log --oneline
git diff
```

## 🔧 Troubleshooting Commands

```bash
# Check what's running on ports
lsof -i :5000   # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill process on port
kill -9 <PID>   # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Check disk space
df -h           # Mac/Linux
dir             # Windows

# Check memory usage
free -h         # Linux
top             # Mac/Linux
htop            # Linux (if installed)

# Check system info
uname -a        # Mac/Linux
systeminfo      # Windows

# Network diagnostics
ping google.com
curl http://localhost:5000/api/v1/health
wget http://example.com
```

## 🌐 API Testing with curl

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Get tickers
curl http://localhost:5000/api/v1/tickers

# Get specific ticker
curl http://localhost:5000/api/v1/ticker/btcidr

# Get analysis
curl http://localhost:5000/api/v1/analysis/btcidr

# With pretty printing
curl http://localhost:5000/api/v1/health | jq

# Test rate limiting
for i in {1..60}; do curl http://localhost:5000/api/v1/health; done
```

## 📊 Monitoring Commands

```bash
# View application logs
tail -f backend/logs/app.log

# Docker container stats
docker stats

# PostgreSQL activity
docker-compose exec db psql -U postgres -c "SELECT * FROM pg_stat_activity;"

# Redis stats
docker-compose exec redis redis-cli INFO stats

# Disk usage by container
docker system df
```

## 🚀 Deployment Commands

```bash
# Railway
railway login
railway init
railway up
railway logs

# Heroku
heroku login
heroku create app-name
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini
git push heroku main
heroku logs --tail

# General
ssh user@server
scp file.txt user@server:/path/
rsync -avz local/ user@server:/remote/
```

## 🔐 Security Commands

```bash
# Generate secret key (Python)
python -c "import secrets; print(secrets.token_hex(32))"

# Check for security vulnerabilities
pip install safety
safety check

# Update dependencies
pip list --outdated
pip install --upgrade package-name

# Scan Docker image
docker scan crypto-analyzer-backend:latest
```

## 📈 Performance Testing

```bash
# Apache Bench
ab -n 1000 -c 10 http://localhost:5000/api/v1/health

# wrk (if installed)
wrk -t12 -c400 -d30s http://localhost:5000/api/v1/tickers

# Simple load test
for i in {1..100}; do
  time curl http://localhost:5000/api/v1/health &
done
```

---

## 💡 Tips & Tricks

1. **Use aliases** for common commands:
```bash
# Add to ~/.bashrc or ~/.zshrc
alias dcu='docker-compose up -d'
alias dcd='docker-compose down'
alias dcl='docker-compose logs -f'
alias dcr='docker-compose restart'
```

2. **Environment shortcuts**:
```bash
export FLASK_ENV=development
export DATABASE_URL=postgresql://localhost/dbname
```

3. **Quick test script**:
```bash
#!/bin/bash
# test.sh
curl http://localhost:5000/api/v1/health
curl http://localhost:5000/api/v1/tickers | head -n 20
```

---

**Save this file for quick reference! 📌**
