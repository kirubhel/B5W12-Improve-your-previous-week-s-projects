# 🚀 Production Deployment Guide
## CrediTrust Complaint Analysis System

This guide provides comprehensive instructions for deploying the complaint analysis system in production environments.

---

## 📋 **Prerequisites**

### **System Requirements**
- **OS**: Linux (Ubuntu 20.04+ recommended) or macOS
- **CPU**: 4+ cores (8+ recommended for production)
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 100GB+ available space
- **Network**: Stable internet connection for model downloads

### **Software Requirements**
- **Python**: 3.8+ (3.11 recommended)
- **Docker**: 20.10+ (for containerized deployment)
- **Docker Compose**: 2.0+ (for multi-service deployment)
- **Git**: Latest version

---

## 🐳 **Docker Deployment (Recommended)**

### **Quick Start**
```bash
# Clone the repository
git clone https://github.com/kirubhel/B5W12-Improve-your-previous-week-s-projects.git
cd B5W12-Improve-your-previous-week-s-projects

# Build and start the system
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f complaint-analysis
```

### **Access the System**
- **Main Dashboard**: http://localhost:8501
- **Monitoring**: http://localhost:9090 (Prometheus)
- **Visualization**: http://localhost:3000 (Grafana)

### **Stop the System**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: This will delete data)
docker-compose down -v
```

---

## 🔧 **Manual Deployment**

### **1. Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export COMPLIANCE_MODE=true
export AUDIT_TRAIL_ENABLED=true
export DATA_RETENTION_DAYS=90
export MAX_RESPONSE_TIME_MS=3000
export MIN_CONFIDENCE_THRESHOLD=0.7
```

### **2. Data Preparation**
```bash
# Create necessary directories
mkdir -p data vector_store reports logs

# Place your complaints data in the data/ directory
# Ensure you have filtered_complaints.csv in data/

# Build vector store (first time only)
python -m src.embedding_indexing
```

### **3. Start the System**
```bash
# Start the dashboard
streamlit run dashboard.py --server.port=8501 --server.address=0.0.0.0

# Or start the legacy interface
python app.py
```

---

## 🏗️ **Production Configuration**

### **Environment Variables**
Create a `.env` file for production:
```bash
# Compliance Settings
COMPLIANCE_MODE=true
AUDIT_TRAIL_ENABLED=true
DATA_RETENTION_DAYS=90

# Performance Settings
MAX_RESPONSE_TIME_MS=3000
MIN_CONFIDENCE_THRESHOLD=0.7

# Security Settings
ENABLE_LOGGING=true
LOG_LEVEL=INFO

# Model Settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
QA_MODEL=google/flan-t5-base
CHUNK_SIZE=300
CHUNK_OVERLAP=50
TOP_K_RETRIEVAL=5
```

### **Systemd Service (Linux)**
Create `/etc/systemd/system/complaint-analysis.service`:
```ini
[Unit]
Description=CrediTrust Complaint Analysis System
After=network.target

[Service]
Type=simple
User=complaint-analysis
WorkingDirectory=/opt/complaint-analysis
Environment=PATH=/opt/complaint-analysis/venv/bin
ExecStart=/opt/complaint-analysis/venv/bin/streamlit run dashboard.py --server.port=8501
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable complaint-analysis
sudo systemctl start complaint-analysis
sudo systemctl status complaint-analysis
```

---

## 📊 **Monitoring & Logging**

### **Application Logs**
```bash
# View application logs
tail -f complaint_analysis.log

# View system logs (if using systemd)
sudo journalctl -u complaint-analysis -f

# View Docker logs
docker-compose logs -f complaint-analysis
```

### **Performance Monitoring**
- **Response Time**: Monitor via dashboard metrics
- **Memory Usage**: Check with `docker stats` or system monitoring
- **Error Rates**: Review logs for exceptions and failures
- **User Activity**: Track via Streamlit analytics

### **Health Checks**
```bash
# Check system health
curl -f http://localhost:8501/_stcore/health

# Check Docker health
docker-compose ps

# Check service status (systemd)
sudo systemctl status complaint-analysis
```

---

## 🔒 **Security Configuration**

### **Firewall Setup**
```bash
# Allow only necessary ports
sudo ufw allow 8501/tcp  # Main application
sudo ufw allow 22/tcp     # SSH (if needed)
sudo ufw enable
```

### **SSL/TLS Configuration**
For production HTTPS:
```bash
# Install nginx
sudo apt install nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/complaint-analysis

# Enable site
sudo ln -s /etc/nginx/sites-available/complaint-analysis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **Access Control**
```bash
# Restrict access to specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 8501
sudo ufw allow from 10.0.0.0/8 to any port 8501
```

---

## 📈 **Scaling & Performance**

### **Horizontal Scaling**
```bash
# Scale the service
docker-compose up -d --scale complaint-analysis=3

# Load balancer configuration (nginx)
upstream complaint_backend {
    server localhost:8501;
    server localhost:8502;
    server localhost:8503;
}
```

### **Resource Limits**
```bash
# Docker resource constraints
services:
  complaint-analysis:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### **Performance Tuning**
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize Python performance
export PYTHONOPTIMIZE=1
export PYTHONUNBUFFERED=1
```

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Port Already in Use**
```bash
# Find process using port 8501
sudo lsof -i :8501

# Kill the process
sudo kill -9 <PID>

# Or use different port
streamlit run dashboard.py --server.port=8502
```

#### **Memory Issues**
```bash
# Check memory usage
free -h
docker stats

# Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### **Model Loading Errors**
```bash
# Clear model cache
rm -rf ~/.cache/huggingface/

# Reinstall transformers
pip install --force-reinstall transformers

# Check disk space
df -h
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with verbose output
streamlit run dashboard.py --logger.level=debug

# Check configuration
python -c "from src.config import *; print('Config loaded successfully')"
```

---

## 🔄 **Updates & Maintenance**

### **System Updates**
```bash
# Update application
git pull origin main
pip install -r requirements.txt

# Restart services
docker-compose restart complaint-analysis
# or
sudo systemctl restart complaint-analysis
```

### **Data Backup**
```bash
# Create backup
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz \
    data/ vector_store/ reports/ logs/

# Restore backup
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz
```

### **Log Rotation**
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/complaint-analysis

# Add configuration
/opt/complaint-analysis/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 complaint-analysis complaint-analysis
}
```

---

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**
- **Daily**: Check system status and logs
- **Weekly**: Review performance metrics
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full system audit and compliance review

### **Emergency Procedures**
```bash
# Emergency stop
docker-compose down
# or
sudo systemctl stop complaint-analysis

# Emergency restart
docker-compose up -d
# or
sudo systemctl restart complaint-analysis

# Rollback to previous version
git checkout <previous-commit>
docker-compose up -d --build
```

---

## 📚 **Additional Resources**

### **Documentation**
- [Technical Documentation](docs/README.md)
- [API Reference](docs/api.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

### **Monitoring Dashboards**
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Application**: http://localhost:8501

### **Contact Information**
- **Technical Support**: tech-support@creditrust.com
- **Emergency**: oncall@creditrust.com
- **Documentation**: documentation@creditrust.com

---

**Deployment Status**: ✅ **Production Ready**  
**Last Updated**: January 2025  
**Next Review**: April 2025 