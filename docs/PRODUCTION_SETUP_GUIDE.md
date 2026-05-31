# Production-Grade Flask Setup Guide

This guide explains how to use the production-grade features added to the Flask application.

## Features Added

### 1. Rate Limiting (Flask-Limiter)
Prevents brute-force attacks and API abuse by limiting request rates.

**Configuration in `config.py`:**
```python
RATELIMIT_ENABLED = True
RATELIMIT_STORAGE_URL = "redis://localhost:6379/1"
RATELIMIT_DEFAULT = "100 per hour"
RATELIMIT_AUTHENTICATED = "200 per hour"
```

**Usage in routes:**
```python
from extensions import limiter
from flask_limiter import limiter

@users_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Strict limit for login
def login():
    # Your login logic
    pass
```

### 2. Caching (Redis + Flask-Caching)
Caches expensive database queries and computations.

**Configuration in `config.py`:**
```python
CACHE_TYPE = 'RedisCache'
CACHE_REDIS_URL = "redis://localhost:6379/0"
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
```

**Usage:**
```python
from extensions import cache

@users_bp.route('/profile/<int:user_id>')
@cache.cached(timeout=300)
def profile(user_id):
    # Expensive database query
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

# To invalidate cache
@users_bp.route('/update-profile', methods=['POST'])
def update_profile():
    # Update logic
    cache.delete(f'view_profile_{user_id}')
```

### 3. Task Queue (Celery)
Handles background tasks like sending emails/SMS without blocking requests.

**Example tasks in `celery_app.py`:**
- `send_email_task(recipient, subject, body)` - Send emails asynchronously
- `send_sms_task(phone_number, message)` - Send SMS asynchronously
- `process_heavy_data_task(data_id)` - Process heavy computations

**Usage in routes:**
```python
from celery_app import send_email_task, send_sms_task

@users_bp.route('/register', methods=['POST'])
def register():
    # Create user
    user = create_user(request.form)
    
    # Send confirmation email in background
    send_email_task.delay(
        recipient=user.email,
        subject='Welcome!',
        body='Thank you for registering.'
    )
    
    return redirect(url_for('users.login'))
```

**Start Celery worker:**
```bash
celery -A celery_app worker --loglevel=info
```

### 4. Monitoring

#### Health Check Endpoint
Access `/health` to check application status:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "celery": "ok"
  }
}
```

#### Metrics Endpoint
Access `/metrics` for basic metrics:
```json
{
  "uptime_seconds": 3600,
  "active_users": 150,
  "total_orders": 500,
  "timestamp": "2024-01-01T00:00:00"
}
```

#### Response Time Tracking
All responses include `X-Response-Time` header. Slow requests (>1s) are logged as warnings.

#### Structured Logging
Logs are in JSON format in `logs/app.log` for easy parsing by log aggregation tools.

## Docker Compose Setup

### Services Included:
- **web**: Flask application with Gunicorn (4 workers)
- **celery_worker**: Celery worker for background tasks
- **celery_beat**: Celery beat for scheduled tasks
- **flower**: Celery monitoring dashboard (port 5555)
- **redis**: Redis for caching, rate limiting, and Celery broker
- **db**: PostgreSQL database

### Start All Services:
```bash
docker-compose up -d
```

### View Logs:
```bash
docker-compose logs -f web
docker-compose logs -f celery_worker
docker-compose logs -f flower
```

### Access Services:
- **Web App**: http://localhost:5000
- **Flower Dashboard**: http://localhost:5555
- **Redis**: localhost:6379
- **PostgreSQL**: localhost:5432

### Stop All Services:
```bash
docker-compose down
```

### Stop and Remove Volumes:
```bash
docker-compose down -v
```

## Environment Variables

Create a `.env` file:
```env
# Security
SECRET_KEY=your-super-secret-key-change-in-production

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/flask_app

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
CACHE_REDIS_URL=redis://localhost:6379/0
RATELIMIT_STORAGE_URL=redis://localhost:6379/1

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# SMS
KAVENEGAR_API_KEY=your-kavenegar-api-key
AMOOTSMS_TOKEN=your-amootsms-token

# Feature Flags
FLASK_DEBUG=False
RATELIMIT_ENABLED=True
```

## Installation Steps

### Local Development (without Docker):

1. **Install Redis:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install redis-server
   
   # macOS
   brew install redis
   
   # Windows (WSL)
   sudo apt-get install redis-server
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Redis:**
   ```bash
   redis-server
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Start Celery worker (separate terminal):**
   ```bash
   celery -A celery_app worker --loglevel=info --pool=solo
   ```

6. **Start Flower for monitoring (optional):**
   ```bash
   celery -A celery_app flower --port=5555
   ```

### Production (with Docker):

1. **Build and start all services:**
   ```bash
   docker-compose up -d --build
   ```

2. **Run database migrations:**
   ```bash
   docker-compose exec web flask db upgrade
   ```

3. **Create admin user:**
   ```bash
   docker-compose exec web flask create-admin
   ```

## Best Practices

### Rate Limiting:
- Use stricter limits for authentication endpoints (e.g., `5 per minute`)
- Use relaxed limits for public APIs (e.g., `100 per hour`)
- Monitor rate limit hits in logs

### Caching:
- Cache expensive database queries
- Set appropriate timeout values based on data freshness requirements
- Invalidate cache when data changes
- Use `cache.memoize` for function-level caching

### Celery Tasks:
- Keep tasks idempotent (safe to retry)
- Set appropriate retry policies
- Monitor task failures in Flower dashboard
- Use task chains/groups for complex workflows

### Monitoring:
- Set up alerts for unhealthy status
- Monitor response times and set thresholds
- Review structured logs regularly
- Track Celery task success/failure rates

## Troubleshooting

### Redis Connection Issues:
```bash
# Check if Redis is running
redis-cli ping

# Should return: PONG
```

### Celery Worker Not Processing Tasks:
```bash
# Check worker logs
docker-compose logs celery_worker

# Verify Redis connection
docker-compose exec redis redis-cli ping
```

### Health Check Failing:
```bash
# Check individual components
curl http://localhost:5000/health

# Check database connection
docker-compose exec db pg_isready
```

## Performance Tips

1. **Database**: Use connection pooling, add indexes, optimize queries
2. **Redis**: Use separate databases for different purposes (0 for cache, 1 for rate limiting)
3. **Gunicorn**: Adjust worker count based on CPU cores (`workers = 2-4 x CPU cores`)
4. **Celery**: Use `gevent` or `eventlet` pool for I/O-bound tasks
5. **Caching**: Cache at multiple levels (view, function, query)

## Security Considerations

1. Change default passwords in production
2. Use environment variables for secrets
3. Enable HTTPS in production
4. Configure CORS properly
5. Keep dependencies updated
6. Use non-root user in Docker containers
