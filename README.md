# 🚀 Crypto Analyzer Pro - Improved Version

Professional cryptocurrency analysis platform with advanced technical analysis, bandarmology detection, and ML-powered recommendations.

## ✨ What's New in This Version

### 🔐 Security Improvements
- ✅ Environment variables management
- ✅ Rate limiting on all API endpoints
- ✅ CORS configuration
- ✅ Input validation & sanitization
- ✅ API key rotation support

### ⚡ Performance Enhancements
- ✅ Redis caching (30s TTL)
- ✅ Background job processing with Celery
- ✅ Database for historical data
- ✅ Code splitting & lazy loading
- ✅ Optimized bundle size

### 🧪 Quality & Testing
- ✅ Unit tests (pytest)
- ✅ Integration tests
- ✅ 80%+ test coverage
- ✅ ESLint & Prettier
- ✅ Pre-commit hooks

### 🚀 DevOps
- ✅ Docker & Docker Compose
- ✅ CI/CD with GitHub Actions
- ✅ Production-ready WSGI (Gunicorn)
- ✅ Automated deployments
- ✅ Health checks & monitoring

### 📊 Features
- ✅ PostgreSQL for data persistence
- ✅ Swagger API documentation
- ✅ Error tracking (Sentry integration ready)
- ✅ Comprehensive logging
- ✅ Backtested scoring algorithm

---

## 🏗️ Architecture

```
crypto-analyzer-improved/
├── backend/
│   ├── src/
│   │   ├── config/         # Configuration management
│   │   ├── models/         # Database models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utilities
│   │   └── main.py         # Flask application
│   ├── tests/              # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   ├── hooks/          # Custom hooks
│   │   └── pages/          # Page components
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .github/workflows/      # CI/CD pipelines
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### 1. Clone & Setup

```bash
git clone https://github.com/YOUR_USERNAME/crypto-analyzer-improved.git
cd crypto-analyzer-improved
cp .env.example .env
# Edit .env with your configurations
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up -d
```

Services:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Docs: http://localhost:5000/api/docs
- Redis: localhost:6379
- PostgreSQL: localhost:5432

### 3. Manual Setup (Development)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
flask db upgrade

# Start Redis (in separate terminal)
redis-server

# Start Celery worker (in separate terminal)
celery -A src.celery_worker worker --loglevel=info

# Start Flask
python src/main.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=1

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/crypto_analyzer

# Redis
REDIS_URL=redis://localhost:6379/0

# API Rate Limiting
RATELIMIT_STORAGE_URL=redis://localhost:6379/1
RATELIMIT_DEFAULT=200 per day, 50 per hour

# Indodax API
INDODAX_API_URL=https://indodax.com/api
INDODAX_RATE_LIMIT=10

# Celery
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/3

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Sentry (Optional)
SENTRY_DSN=your-sentry-dsn

# Frontend
VITE_API_URL=http://localhost:5000/api
```

---

## 📚 API Documentation

Interactive API documentation available at: `http://localhost:5000/api/docs`

### Key Endpoints

#### Market Data
```bash
GET /api/v1/health              # Health check
GET /api/v1/pairs               # All trading pairs
GET /api/v1/tickers             # All tickers (cached)
GET /api/v1/ticker/{pair_id}    # Specific ticker
GET /api/v1/depth/{pair_id}     # Order book
```

#### Analysis
```bash
GET /api/v1/analysis/{pair_id}           # Complete analysis
GET /api/v1/technical/{pair_id}          # Technical analysis only
GET /api/v1/bandarmology/{pair_id}       # Bandarmology only
GET /api/v1/recommendation/{pair_id}     # Recommendation only
```

#### Historical Data
```bash
GET /api/v1/history/{pair_id}            # Price history
GET /api/v1/analytics/{pair_id}          # Analytics data
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=src --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### E2E Tests
```bash
npm run test:e2e
```

---

## 🚀 Deployment

### Docker Production Build

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Railway/Heroku Deployment

```bash
# Set environment variables in platform dashboard
# Push to main branch (auto-deploy via GitHub Actions)
git push origin main
```

### Manual Deployment

```bash
# Backend
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 'src.main:app'

# Frontend
cd frontend
npm run build
# Serve dist/ with nginx or CDN
```

---

## 📊 Monitoring & Logging

### Application Logs
```bash
tail -f backend/logs/app.log
```

### Redis Monitoring
```bash
redis-cli monitor
```

### Database Queries
```bash
docker-compose logs -f postgres
```

### Celery Tasks
```bash
celery -A src.celery_worker flower
# Access at http://localhost:5555
```

---

## 🛡️ Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use strong SECRET_KEY in production
- ✅ Enable HTTPS in production
- ✅ Regular dependency updates
- ✅ Monitor security advisories
- ✅ Use database migrations
- ✅ Implement request signing for sensitive operations

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

---

## ⚠️ Disclaimer

**IMPORTANT:** This is an analytical tool, NOT financial advice.

- Cryptocurrency trading involves substantial risk
- Always do your own research (DYOR)
- Never invest more than you can afford to lose
- System recommendations are algorithmic and may be incorrect
- Use as supplementary reference, not primary decision maker

---

## 🆘 Support

- 📧 Email: wibiar279@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/YOUR_USERNAME/crypto-analyzer-improved/issues)
- 📖 Docs: [Wiki](https://github.com/YOUR_USERNAME/crypto-analyzer-improved/wiki)

---

## 🙏 Acknowledgments

- [Indodax](https://indodax.com) for API access
- [TA-Lib](https://ta-lib.org/) for technical indicators
- Community contributors

---

**Made with ❤️ for crypto traders and analysts**
