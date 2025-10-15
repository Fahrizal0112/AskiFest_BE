# QR Scanner Backend - Docker Deployment

Panduan lengkap untuk menjalankan QR Scanner Backend menggunakan Docker.

## Prerequisites

1. **Docker & Docker Compose**
   ```bash
   # macOS (Homebrew)
   brew install --cask docker
   
   # Atau download dari https://www.docker.com/products/docker-desktop
   ```

2. **Git** (untuk clone repository)

## Quick Start

### 1. Development Mode
```bash
# Menggunakan script
./docker-run.sh dev

# Atau menggunakan Makefile
make dev

# Atau manual
docker-compose -f docker-compose.dev.yml up --build -d
```

**Akses:**
- API: http://localhost:5001
- Database: localhost:5433

### 2. Production Mode
```bash
# Setup environment
cp .env.docker .env
# Edit .env sesuai kebutuhan

# Jalankan
./docker-run.sh prod
# atau
make prod
```

**Akses:**
- API: http://localhost:5000
- Nginx: http://localhost:80
- Database: localhost:5432

## Struktur Docker

### Services

1. **postgres** - PostgreSQL Database
   - Image: `postgres:15-alpine`
   - Port: 5432 (prod) / 5433 (dev)
   - Volume: Persistent data storage

2. **app** - Flask Application
   - Build: Custom Dockerfile
   - Port: 5000
   - Depends: postgres

3. **nginx** - Reverse Proxy (Production only)
   - Image: `nginx:alpine`
   - Port: 80, 443
   - Features: Rate limiting, CORS, Security headers

### Files

- `Dockerfile` - Production image
- `Dockerfile.dev` - Development image dengan hot reload
- `docker-compose.yml` - Production setup
- `docker-compose.dev.yml` - Development setup
- `nginx.conf` - Nginx configuration
- `docker-run.sh` - Helper script
- `Makefile` - Make commands

## Commands

### Menggunakan Script Helper

```bash
# Development
./docker-run.sh dev

# Production
./docker-run.sh prod

# Build ulang images
./docker-run.sh build

# Stop containers
./docker-run.sh stop

# Clean up (hapus containers + volumes)
./docker-run.sh clean

# Lihat logs
./docker-run.sh logs

# Akses database
./docker-run.sh db

# Run tests
./docker-run.sh test
```

### Menggunakan Makefile

```bash
make dev      # Development mode
make prod     # Production mode
make build    # Build images
make stop     # Stop containers
make clean    # Clean up
make logs     # Show logs
make db       # Database access
make test     # Run tests
```

### Manual Docker Commands

```bash
# Development
docker-compose -f docker-compose.dev.yml up -d

# Production
docker-compose up -d

# View logs
docker-compose logs -f app

# Access database
docker exec -it qr_scanner_db psql -U postgres -d aski_scan

# Run tests
docker exec qr_scanner_app python test_api.py
```

## Environment Variables

### Development (.env.dev)
```env
DB_HOST=postgres
DB_NAME=aski_scan_dev
DB_PASSWORD=dev_password_123
DEBUG=True
```

### Production (.env)
```env
DB_HOST=postgres
DB_NAME=aski_scan
DB_PASSWORD=secure_password_123
SECRET_KEY=your-production-secret-key
DEBUG=False
```

## Volumes & Data Persistence

- **postgres_data**: Database files
- **logs**: Application logs
- **ssl**: SSL certificates (untuk HTTPS)

## Networking

- **qr_scanner_network**: Internal network untuk services
- **qr_scanner_dev_network**: Development network

## Health Checks

### Application Health Check
```bash
curl http://localhost:5000/api/health
```

### Database Health Check
```bash
docker exec qr_scanner_db pg_isready -U postgres
```

## Monitoring & Logs

### View Logs
```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres

# Nginx logs
docker-compose logs -f nginx

# All services
docker-compose logs -f
```

### Container Status
```bash
docker-compose ps
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Check what's using the port
   lsof -i :5000
   
   # Kill process or change port in docker-compose.yml
   ```

2. **Database connection failed**
   ```bash
   # Check database container
   docker-compose logs postgres
   
   # Restart database
   docker-compose restart postgres
   ```

3. **Permission denied**
   ```bash
   # Make script executable
   chmod +x docker-run.sh
   ```

### Reset Everything
```bash
# Stop and remove everything
./docker-run.sh clean

# Start fresh
./docker-run.sh dev
```

## Production Deployment

### 1. Server Setup
```bash
# Clone repository
git clone <repository-url>
cd ASKIFEST_SCANQR

# Setup environment
cp .env.docker .env
nano .env  # Edit configuration
```

### 2. SSL Setup (Optional)
```bash
# Create SSL directory
mkdir ssl

# Add your certificates
cp your-cert.pem ssl/
cp your-key.pem ssl/

# Update nginx.conf for HTTPS
```

### 3. Deploy
```bash
# Production deployment
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Backup Database
```bash
# Create backup
docker exec qr_scanner_db pg_dump -U postgres aski_scan > backup.sql

# Restore backup
docker exec -i qr_scanner_db psql -U postgres aski_scan < backup.sql
```

## Security Considerations

1. **Change default passwords** dalam .env
2. **Use strong SECRET_KEY** untuk production
3. **Enable HTTPS** dengan SSL certificates
4. **Configure firewall** untuk production server
5. **Regular updates** untuk Docker images
6. **Monitor logs** untuk suspicious activity

## Performance Tuning

1. **Database**
   - Adjust PostgreSQL configuration
   - Monitor connection pool
   - Regular VACUUM and ANALYZE

2. **Application**
   - Use Gunicorn untuk production
   - Configure worker processes
   - Enable caching

3. **Nginx**
   - Enable gzip compression
   - Configure caching headers
   - Optimize worker processes