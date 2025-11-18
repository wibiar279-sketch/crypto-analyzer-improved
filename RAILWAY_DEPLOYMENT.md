# Railway Deployment Guide

This guide explains how to deploy the Crypto Analyzer application on Railway.app.

## Architecture

The application consists of 4 services:

1. **Backend** (Flask API) - Main application service
2. **PostgreSQL** - Database for storing historical data
3. **Redis** - Caching and session storage
4. **Frontend** (React) - User interface (optional, can be deployed separately)

## Automatic Deployment

Railway will automatically detect and build the backend service using the configuration files:

- `railway.toml` - Railway-specific configuration
- `nixpacks.toml` - Build configuration
- `Procfile` - Process definition
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version

## Environment Variables

Set these environment variables in Railway dashboard:

### Required Variables

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=<generate-a-secure-random-key>
FLASK_DEBUG=0

# Database (automatically provided by Railway PostgreSQL)
DATABASE_URL=${POSTGRES_URL}

# Redis (automatically provided by Railway Redis)
REDIS_URL=${REDIS_URL}

# API Configuration
INDODAX_API_URL=https://indodax.com/api
INDODAX_RATE_LIMIT=10

# CORS (update with your frontend URL)
CORS_ORIGINS=https://your-frontend-domain.com

# Port (automatically set by Railway)
PORT=${PORT}
```

### Optional Variables

```env
# Celery (for background tasks)
CELERY_BROKER_URL=${REDIS_URL}
CELERY_RESULT_BACKEND=${REDIS_URL}

# Logging
LOG_LEVEL=INFO

# Sentry (error tracking)
SENTRY_DSN=your-sentry-dsn-here
```

## Deployment Steps

### 1. Deploy Backend Service

1. Go to Railway dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `crypto-analyzer-improved` repository
5. Railway will automatically detect Python and start building

### 2. Add PostgreSQL Database

1. In your project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create `POSTGRES_URL` variable
4. The backend will automatically use this database

### 3. Add Redis Cache

1. In your project, click "+ New"
2. Select "Database" → "Redis"
3. Railway will automatically create `REDIS_URL` variable
4. The backend will automatically use this cache

### 4. Configure Environment Variables

1. Go to backend service → "Variables" tab
2. Add the required variables listed above
3. Use Railway's provided variables for DATABASE_URL and REDIS_URL:
   - `DATABASE_URL` → Reference `${POSTGRES_URL}`
   - `REDIS_URL` → Reference `${REDIS_URL}`

### 5. Enable Public Access

1. Go to backend service → "Settings" tab
2. Click "Generate Domain" to get a public URL
3. Your API will be available at: `https://your-service.up.railway.app`

## Health Check

After deployment, verify the service is running:

```bash
curl https://your-service.up.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-11-17T12:00:00Z"
}
```

## API Documentation

Once deployed, access the Swagger documentation at:

```
https://your-service.up.railway.app/api/docs
```

## Monitoring

### View Logs

1. Go to backend service
2. Click "Logs" tab
3. Monitor real-time application logs

### View Metrics

1. Go to backend service
2. Click "Metrics" tab
3. Monitor CPU, memory, and network usage

## Troubleshooting

### Build Fails

If build fails, check:
- Python version in `runtime.txt` is compatible
- All dependencies in `requirements.txt` are available
- Build logs for specific error messages

### Application Crashes

If application crashes after deployment:
- Check environment variables are set correctly
- Verify DATABASE_URL and REDIS_URL are connected
- Check logs for error messages
- Ensure PORT variable is used in the application

### Database Connection Issues

- Verify PostgreSQL service is running
- Check DATABASE_URL variable is set
- Ensure backend can connect to database (check logs)

### Redis Connection Issues

- Verify Redis service is running
- Check REDIS_URL variable is set
- Ensure backend can connect to Redis (check logs)

## Scaling

### Vertical Scaling (More Resources)

1. Go to backend service → "Settings"
2. Upgrade to a higher plan for more CPU/RAM

### Horizontal Scaling (More Instances)

1. Go to backend service → "Settings"
2. Increase "Replicas" count
3. Railway will load balance across instances

## Cost Optimization

- Use Railway's free tier for development
- Enable "Sleep on Idle" for non-production environments
- Monitor usage in the billing dashboard
- Consider upgrading to Pro for production workloads

## Security Best Practices

1. **Never commit secrets** - Use environment variables
2. **Rotate SECRET_KEY** regularly
3. **Use HTTPS** - Railway provides SSL automatically
4. **Enable CORS** properly - Only allow your frontend domain
5. **Monitor logs** for suspicious activity
6. **Keep dependencies updated** - Regularly update packages

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: https://github.com/wibiar279-sketch/crypto-analyzer-improved/issues

## Next Steps

1. Deploy frontend separately (React app)
2. Set up custom domain
3. Configure CI/CD for automatic deployments
4. Set up monitoring and alerts
5. Configure backup strategy for PostgreSQL

---

**Made with ❤️ for crypto traders**
