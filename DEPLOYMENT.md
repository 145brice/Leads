# 🚀 Production Deployment Guide

## Cloud Deployment Options

### Option 1: DigitalOcean Droplet (Recommended)

**Cost**: ~$12/month (Basic Droplet)

#### Setup Steps

1. **Create Droplet**
   - Ubuntu 22.04 LTS
   - Basic plan ($12/month)
   - SSH key authentication

2. **SSH into Server**
```bash
ssh root@your-droplet-ip
```

3. **Install Dependencies**
```bash
apt update
apt upgrade -y
apt install python3 python3-pip python3-venv nginx -y
```

4. **Deploy Code**
```bash
cd /var/www
git clone your-repo contractor-leads
cd contractor-leads

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure Environment**
```bash
cp .env.example .env
nano .env  # Add production credentials
```

6. **Set Up Nginx**
```bash
nano /etc/nginx/sites-available/contractor-leads
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/contractor-leads /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

7. **Create Systemd Service for Flask**
```bash
nano /etc/systemd/system/contractor-leads.service
```

Add:
```ini
[Unit]
Description=Contractor Leads Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/contractor-leads
Environment="PATH=/var/www/contractor-leads/venv/bin"
ExecStart=/var/www/contractor-leads/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
systemctl daemon-reload
systemctl start contractor-leads
systemctl enable contractor-leads
```

8. **Create Systemd Service for Scheduler**
```bash
nano /etc/systemd/system/contractor-scheduler.service
```

Add:
```ini
[Unit]
Description=Contractor Leads Scheduler
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/contractor-leads
Environment="PATH=/var/www/contractor-leads/venv/bin"
ExecStart=/var/www/contractor-leads/venv/bin/python scheduler.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
systemctl start contractor-scheduler
systemctl enable contractor-scheduler
```

9. **Enable SSL with Let's Encrypt**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d yourdomain.com
```

10. **Monitor Services**
```bash
systemctl status contractor-leads
systemctl status contractor-scheduler
journalctl -u contractor-leads -f
```

---

### Option 2: Heroku

**Cost**: ~$7/month (Eco Dynos)

#### Setup Steps

1. **Install Heroku CLI**
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

2. **Create Procfile**
```bash
cat > Procfile << EOF
web: gunicorn app:app
worker: python scheduler.py
EOF
```

3. **Deploy**
```bash
heroku login
heroku create contractor-leads-app
git push heroku main
```

4. **Set Environment Variables**
```bash
heroku config:set STRIPE_SECRET_KEY=sk_live_...
heroku config:set FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
# etc...
```

5. **Scale Dynos**
```bash
heroku ps:scale web=1 worker=1
```

6. **Add Firebase Credentials**
Upload `firebase-credentials.json` via Heroku dashboard or use base64 encoding.

---

### Option 3: AWS EC2

Similar to DigitalOcean but with:
- EC2 t2.micro (~$10/month)
- Security groups for port 80/443
- Elastic IP for stable address
- Follow same Nginx + Systemd setup

---

### Option 4: Google Cloud Run

**Cost**: Pay per use (~$5-10/month for small traffic)

**Note**: Cloud Run is stateless, so scheduler needs separate solution (Cloud Scheduler + Cloud Functions).

---

## Database Considerations

### Firebase (Current Setup)
- **Pros**: Easy, managed, scales automatically
- **Cons**: Costs increase with usage
- **Best for**: MVP, small-medium scale

### Alternative: PostgreSQL
If you want to save costs at scale:

1. **Add PostgreSQL**
```bash
pip install psycopg2-binary sqlalchemy
```

2. **Update Backend**
Replace Firebase with SQLAlchemy models

3. **Use Managed DB**
- DigitalOcean Managed Database (~$15/month)
- AWS RDS (~$15/month)
- Heroku Postgres (~$9/month)

---

## Monitoring & Logging

### Logging Setup

```python
# Add to app.py and scheduler.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contractor-leads.log'),
        logging.StreamHandler()
    ]
)
```

### Monitor With:

**Sentry** (Error Tracking)
```bash
pip install sentry-sdk[flask]
```

Add to `app.py`:
```python
import sentry_sdk
sentry_sdk.init(dsn="your-sentry-dsn")
```

**UptimeRobot** (Free)
- Monitor app uptime
- Get alerts if site goes down

**Papertrail** (Log Management)
- Centralized log viewing
- Free tier available

---

## Backup Strategy

### Firebase Backups

1. **Automated Backups**
```bash
# Daily backup script
gcloud firestore export gs://your-bucket/$(date +%Y%m%d)
```

2. **Schedule with Cron**
```bash
0 3 * * * /path/to/backup-script.sh
```

### Application Backups

```bash
# Backup code and configs
tar -czf backup-$(date +%Y%m%d).tar.gz /var/www/contractor-leads
```

---

## Performance Optimization

### 1. Cache Scraped Data
```python
# Use Redis for caching
pip install redis
```

### 2. Async Scraping
```python
# Use asyncio for parallel scraping
import asyncio
import aiohttp
```

### 3. Database Indexes
- Index on `created_at`, `county`, `score`

### 4. CDN for Static Assets
- Use Cloudflare (free tier)

---

## Security Hardening

### 1. Firewall
```bash
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable
```

### 2. Fail2Ban (Prevent brute force)
```bash
apt install fail2ban -y
systemctl enable fail2ban
```

### 3. Security Headers
Add to Nginx:
```nginx
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

### 4. Rate Limiting
```python
# Add to app.py
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/leads')
@limiter.limit("10/minute")
def api_leads():
    ...
```

### 5. CSRF Protection
```bash
pip install flask-wtf
```

---

## Scaling Considerations

### When to Scale?

- **100+ users**: Current setup works fine
- **500+ users**: Add Redis cache, optimize DB queries
- **1000+ users**: Multiple app servers behind load balancer
- **5000+ users**: Kubernetes, separate scraper workers

### Horizontal Scaling

1. **Load Balancer**
   - Nginx load balancer
   - AWS ELB
   - DigitalOcean Load Balancer

2. **Multiple App Servers**
```nginx
upstream backend {
    server app1.example.com;
    server app2.example.com;
    server app3.example.com;
}
```

3. **Separate Scraper Workers**
- Run scrapers on dedicated servers
- Use job queue (Celery + Redis)

---

## Cost Breakdown (Monthly)

### Small Scale (0-100 users)
- **Server**: $12 (DigitalOcean Droplet)
- **Domain**: $12/year = $1/month
- **Firebase**: Free tier
- **Stripe**: 2.9% + 30¢ per transaction
- **Email**: Free (Gmail)
- **SSL**: Free (Let's Encrypt)
- **Total**: ~$13/month + Stripe fees

### Revenue
- 50 users × $20 = $1,000/month
- Costs: $13 + Stripe fees (~$30) = $43
- **Profit**: ~$957/month

### Medium Scale (500 users)
- **Server**: $48 (4GB Droplet)
- **Firebase**: ~$25
- **Monitoring**: $10 (Sentry, etc.)
- **Total**: ~$83/month + Stripe fees

### Revenue
- 500 users × $20 = $10,000/month
- Costs: $83 + Stripe fees (~$300) = $383
- **Profit**: ~$9,617/month

---

## Pre-Launch Checklist

- [ ] Update scrapers with real website parsing
- [ ] Test all 5 county scrapers
- [ ] Verify AI scoring accuracy
- [ ] Test email delivery to multiple providers
- [ ] Complete Stripe payment flow (test mode)
- [ ] Set up production Firebase project
- [ ] Get production Stripe keys
- [ ] Configure custom domain
- [ ] Enable SSL/HTTPS
- [ ] Set up monitoring and alerts
- [ ] Create backup strategy
- [ ] Write terms of service
- [ ] Write privacy policy
- [ ] Test full user journey (signup → pay → receive emails)
- [ ] Load test with 100 simulated users
- [ ] Set up customer support email
- [ ] Create FAQ page
- [ ] Launch! 🚀

---

## Post-Launch Tasks

### Week 1
- Monitor error logs daily
- Check scraper success rates
- Verify email delivery rates
- Respond to user feedback

### Month 1
- Analyze user retention
- Optimize scraper performance
- Add requested features
- Marketing and growth

### Ongoing
- Add new counties based on demand
- Improve AI scoring accuracy
- A/B test pricing
- Build contractor community

---

## Support & Maintenance

### Daily
- Check error logs
- Monitor scraper success
- Verify email delivery

### Weekly
- Review user feedback
- Update scrapers if websites change
- Check server resources

### Monthly
- Update dependencies
- Security patches
- Backup verification
- Review metrics and KPIs

---

**Ready to deploy?** Start with DigitalOcean Droplet, test thoroughly, then scale as you grow!
