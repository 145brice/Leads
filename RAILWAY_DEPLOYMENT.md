# Railway Deployment Guide for Edge Permits SaaS

## Prerequisites
- Railway account (https://railway.app)
- GitHub repository with this project

## Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

## Step 2: Deploy to Railway
1. Go to https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Connect your GitHub account and select the repository
4. Railway will auto-detect Python and deploy

## Step 3: Configure Environment Variables
In Railway dashboard, go to your project → Variables and add:

```
SECRET_KEY=your_secret_key_here
STRIPE_SECRET_KEY=sk_live_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_PRICE_ID=price_your_price_id
FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project.firebaseio.com/
SENDGRID_API_KEY=SG.your_sendgrid_api_key
FROM_EMAIL=noreply@edgepermits.com
FLASK_ENV=production
DATABASE_PATH=contractor_leads.db
```

## Step 4: Upload Firebase Credentials
1. In Railway, go to your project → Files
2. Upload your `firebase-credentials.json` file
3. Make sure the path matches the environment variable

## Step 5: Set up Database (Optional)
If you need persistent data, add a PostgreSQL database in Railway:
1. Add PostgreSQL plugin
2. Update config.py to use Railway's DATABASE_URL

## Step 6: Get Your App URL
Railway will provide a URL like: `https://edge-permits-production.up.railway.app`

## Troubleshooting
- Check Railway logs for errors
- Ensure all environment variables are set
- Verify Firebase credentials are uploaded
- Test Stripe webhooks if using payment features

## Cost
Railway has a generous free tier, then $5/month for the hobby plan.
