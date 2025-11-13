# Live Reddit Leads Feed

A premium Flask application powered by PRAW (Python Reddit API Wrapper) that monitors Reddit in real-time and displays posts in a beautiful feed with animations.

## Features

- 🔴 **Real-time Reddit monitoring** using PRAW
- 💎 **Premium UI** with Reddit-themed orange animations
- 🔄 **Auto-refresh** every 30 seconds
- ✨ **Flash animations** for new posts
- 🔍 **Unique users filter**
- 📈 **Sortable columns** (username, subreddit, title, score, created date)
- 🔗 **Clickable Reddit links**
- 🎯 **Keyword search** within subreddits
- 🌐 **Multi-subreddit monitoring**

## Prerequisites

1. **Reddit App Credentials**: You need to create a Reddit app to get API credentials
   - Go to https://www.reddit.com/prefs/apps
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Fill in the name and description
   - Set redirect URI to `http://localhost:8080` (not used but required)
   - Click "Create app"
   - Note your `client_id` (under the app name) and `client_secret`

## Setup

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
# Required: Reddit API credentials
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=Live Leads Feed v1.0

# Optional: Configuration
SUBREDDITS=python,programming,webdev          # Comma-separated list of subreddits
SEARCH_KEYWORDS=help,question,hiring           # Optional: Comma-separated keywords to search for
POST_LIMIT=50                                  # Number of posts to fetch per subreddit
```

**Configuration Options:**

- `SUBREDDITS`: Comma-separated list of subreddit names (without r/). Default: `all`
- `SEARCH_KEYWORDS`: If specified, searches for these keywords in the subreddits. If empty, fetches new posts.
- `POST_LIMIT`: Maximum number of posts to fetch per subreddit. Default: `50`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (or create .env file)
export REDDIT_CLIENT_ID=your_client_id
export REDDIT_CLIENT_SECRET=your_client_secret
export SUBREDDITS=python,programming
export POST_LIMIT=50

# Run the app
python app.py
```

Visit `http://localhost:5000`

## Deploy to Vercel

1. **Push your code to GitHub**

2. **Import repository to Vercel**
   - Go to https://vercel.com
   - Click "Import Project"
   - Select your repository

3. **Set Environment Variables in Vercel**
   - In your Vercel project settings, go to "Environment Variables"
   - Add the following:
     - `REDDIT_CLIENT_ID`
     - `REDDIT_CLIENT_SECRET`
     - `REDDIT_USER_AGENT` (optional)
     - `SUBREDDITS` (optional)
     - `SEARCH_KEYWORDS` (optional)
     - `POST_LIMIT` (optional)

4. **Deploy**
   - Vercel will automatically deploy your app
   - Your app will be live at `https://your-project.vercel.app`

## Usage Examples

### Monitor specific subreddits for new posts
```bash
export SUBREDDITS=learnprogramming,python,javascript
export POST_LIMIT=30
```

### Search for specific keywords
```bash
export SUBREDDITS=forhire,slavelabour
export SEARCH_KEYWORDS=python,flask,api
export POST_LIMIT=25
```

### Monitor r/all for everything
```bash
export SUBREDDITS=all
export POST_LIMIT=100
```

## UI Features

- **Show Uniques Button**: Toggle between all posts and unique users only
- **Sortable Headers**: Click column headers to sort by username, subreddit, title, score, or date
- **Live Stats**: See total posts, unique users, and new posts in the current cycle
- **Auto-refresh**: Data refreshes every 30 seconds automatically
- **Visual Indicators**: New posts flash with orange animations

## Requirements

- Python 3.9+
- Flask 2.3.3
- PRAW 7.7.1
- requests 2.31.0
- Werkzeug 2.3.7

## Troubleshooting

### "Reddit API credentials not configured"
- Make sure you've set the `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` environment variables
- Verify your credentials are correct from https://www.reddit.com/prefs/apps

### "No posts found"
- Check that the subreddit names are correct (without r/ prefix)
- Verify your Reddit app has proper permissions
- Try increasing `POST_LIMIT`
- Make sure the subreddits are public and accessible

### Rate Limiting
- PRAW respects Reddit's rate limits automatically
- If you're hitting rate limits, increase the refresh interval or reduce `POST_LIMIT`

## API Endpoints

- `GET /` - Main web interface
- `GET /api/leads` - JSON API endpoint returning Reddit posts

## License

MIT License
