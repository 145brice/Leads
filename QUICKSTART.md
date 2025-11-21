# 🚀 QUICK START GUIDE

## Get Running in 5 Minutes

### 1. Install Dependencies

```bash
cd /tmp/contractor-leads-saas

# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

Or manually:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials. **Minimum required:**

```env
# For testing, you can use placeholder values
SECRET_KEY=test-secret-key-change-in-production
FLASK_ENV=development

# These need real credentials:
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com
STRIPE_SECRET_KEY=sk_test_...
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Get Credentials

#### Firebase (Required)
1. Go to https://console.firebase.google.com
2. Create new project
3. Enable Firestore Database
4. Enable Authentication > Email/Password
5. Project Settings > Service Accounts > Generate New Private Key
6. Save as `firebase-credentials.json` in project root

#### Stripe (Required for payments)
1. Go to https://dashboard.stripe.com/register
2. Get test API keys from Dashboard > Developers > API Keys
3. Create a Product ($20/month)
4. Copy Price ID

#### Email (Required for sending leads)
1. Use Gmail with App Password
2. Enable 2FA: https://myaccount.google.com/security
3. Generate App Password: https://myaccount.google.com/apppasswords
4. Use app password in `.env`

### 4. Test Setup

```bash
source venv/bin/activate
python test_setup.py
```

This will check all components.

### 5. Run the App

**Terminal 1 - Web App:**
```bash
source venv/bin/activate
python app.py
```

**Terminal 2 - Scheduler (Optional for testing):**
```bash
source venv/bin/activate
python scheduler.py
```

### 6. Open Browser

Visit: http://localhost:5000

- Sign up for account
- Subscribe (test mode)
- View dashboard

### 7. Manual Test Run

Test the scraping/scoring/email pipeline:

```bash
source venv/bin/activate
python -c "from scheduler import LeadScheduler; LeadScheduler().run_nightly_job()"
```

---

## 📝 Important Notes

### Scrapers Are Templates

The county scrapers are **skeleton code**. You must:

1. Visit actual county websites
2. Inspect HTML/PDF structure
3. Update selectors and parsing logic
4. Test thoroughly

Example counties:
- Nashville: https://www.nashville.gov/departments/codes/building-permits
- Rutherford: https://www.rutherfordcountytn.gov/building_codes
- Wilson: https://www.wilsoncountytn.gov/building
- Sumner: https://www.sumnercountytn.gov/building

### Production Checklist

Before going live:

- [ ] Switch to production Firebase project
- [ ] Use production Stripe keys
- [ ] Set strong `SECRET_KEY`
- [ ] Use production email service
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Add monitoring
- [ ] Test payment flow
- [ ] Test email delivery
- [ ] Verify scraper accuracy

---

## 🆘 Troubleshooting

### Import Errors

```bash
pip install -r requirements.txt
```

### Firebase Connection Failed

- Check `firebase-credentials.json` exists
- Verify path in `.env`
- Check Firebase project URL

### Stripe Errors

- Verify API keys in `.env`
- Use test keys (start with `sk_test_`)
- Check Price ID is correct

### Email Not Sending

- Use Gmail App Password (not regular password)
- Enable "Less secure app access" if needed
- Check SMTP settings

### AI Model Loading Slow

First time loading HuggingFace model downloads ~250MB. This is normal.

---

## 📚 Next Steps

1. **Customize Scrapers**: Update parsing logic for real county websites
2. **Adjust AI Scoring**: Modify weights and criteria in `ai_scorer.py`
3. **Brand Dashboard**: Customize HTML templates
4. **Add Analytics**: Track user engagement
5. **Improve Email**: Design better templates
6. **Scale**: Add more counties, deploy to cloud

---

## 🎯 File Structure

```
contractor-leads-saas/
├── app.py                  # Flask web app (START HERE)
├── scheduler.py            # Nightly jobs
├── config.py               # Configuration
├── scrapers/               # County scrapers
├── templates/              # HTML pages
├── requirements.txt        # Dependencies
├── .env                    # Your credentials
└── README.md              # Full documentation
```

---

**Questions?** Check `README.md` for detailed docs.

**Ready to launch?** Update scrapers, test thoroughly, deploy!
