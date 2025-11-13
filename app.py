from flask import Flask, render_template_string, jsonify
import praw
import os
from datetime import datetime

app = Flask(__name__)

# Reddit API credentials from environment variables
REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID', '')
REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET', '')
REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT', 'Live Leads Feed v1.0')

# Configuration for what to search
SUBREDDITS = os.environ.get('SUBREDDITS', 'all').split(',')  # Comma-separated list
SEARCH_KEYWORDS = os.environ.get('SEARCH_KEYWORDS', '').split(',') if os.environ.get('SEARCH_KEYWORDS') else []
POST_LIMIT = int(os.environ.get('POST_LIMIT', '50'))

# Store last seen leads for detecting new ones
last_leads = []
last_fetch_time = None

def get_reddit_instance():
    """Create and return a Reddit instance"""
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        return reddit
    except Exception as e:
        print(f"Error creating Reddit instance: {e}")
        return None

def fetch_leads():
    """Fetch leads from Reddit using PRAW"""
    try:
        reddit = get_reddit_instance()
        if not reddit:
            return []
        
        leads = []
        
        # Fetch posts from specified subreddits
        for subreddit_name in SUBREDDITS:
            subreddit_name = subreddit_name.strip()
            if not subreddit_name:
                continue
                
            try:
                subreddit = reddit.subreddit(subreddit_name)
                
                # If search keywords are specified, search for them
                if SEARCH_KEYWORDS and SEARCH_KEYWORDS[0]:
                    for keyword in SEARCH_KEYWORDS:
                        keyword = keyword.strip()
                        if not keyword:
                            continue
                        
                        for submission in subreddit.search(keyword, limit=POST_LIMIT, sort='new'):
                            lead = {
                                'Username': str(submission.author) if submission.author else '[deleted]',
                                'Subreddit': str(submission.subreddit),
                                'Title': submission.title,
                                'Link': f"https://reddit.com{submission.permalink}",
                                'Score': str(submission.score),
                                'Created': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                            }
                            leads.append(lead)
                else:
                    # Just get new posts from the subreddit
                    for submission in subreddit.new(limit=POST_LIMIT):
                        lead = {
                            'Username': str(submission.author) if submission.author else '[deleted]',
                            'Subreddit': str(submission.subreddit),
                            'Title': submission.title,
                            'Link': f"https://reddit.com{submission.permalink}",
                            'Score': str(submission.score),
                            'Created': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        leads.append(lead)
                        
            except Exception as e:
                print(f"Error fetching from r/{subreddit_name}: {e}")
                continue
        
        return leads
        
    except Exception as e:
        print(f"Error fetching leads: {e}")
        return []

def get_new_leads(current_leads, previous_leads):
    """Identify new leads that weren't in the previous fetch"""
    if not previous_leads:
        return current_leads
    
    # Create a set of previous lead signatures for comparison
    prev_signatures = set()
    for lead in previous_leads:
        # Create a unique signature from all values
        sig = tuple(sorted([str(v) for v in lead.values() if v]))
        prev_signatures.add(sig)
    
    new_leads = []
    for lead in current_leads:
        sig = tuple(sorted([str(v) for v in lead.values() if v]))
        if sig not in prev_signatures:
            new_leads.append(lead)
    
    return new_leads

def get_unique_leads(leads):
    """Filter out duplicate leads - based on username only"""
    seen = set()
    unique = []
    
    for lead in leads:
        # Get the username field
        username_value = lead.get('Username', '').strip()
        
        # Use username as unique identifier
        if username_value and username_value not in seen:
            seen.add(username_value)
            unique.append(lead)
        elif not username_value:
            # If no username found, include it anyway
            unique.append(lead)
    
    return unique

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Reddit Leads Feed</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
            color: #fff;
            overflow-x: hidden;
            min-height: 100vh;
            position: relative;
        }
        
        /* Animated background particles */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(255, 69, 0, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 69, 0, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255, 69, 0, 0.06) 0%, transparent 50%);
            animation: pulse 8s ease-in-out infinite;
            pointer-events: none;
            z-index: 0;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        .container {
            position: relative;
            z-index: 1;
            padding: 40px 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 50px;
            position: relative;
        }
        
        .header h1 {
            font-size: 3.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #FF4500 0%, #FF8C00 50%, #FF4500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(255, 69, 0, 0.5);
            margin-bottom: 10px;
            letter-spacing: -1px;
            animation: shimmer 3s ease-in-out infinite;
        }
        
        @keyframes shimmer {
            0%, 100% { filter: brightness(1); }
            50% { filter: brightness(1.3); }
        }
        
        .header p {
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.7);
            font-weight: 300;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 15px 40px;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #FF4500 0%, #FF8C00 100%);
            color: #fff;
            box-shadow: 0 8px 25px rgba(255, 69, 0, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(255, 69, 0, 0.5);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn.active {
            background: linear-gradient(135deg, #FF8C00 0%, #FFA500 100%);
            box-shadow: 0 8px 25px rgba(255, 140, 0, 0.5);
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 69, 0, 0.2);
            border-radius: 20px;
            padding: 20px 30px;
            text-align: center;
            min-width: 150px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #FF4500;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .feed-container {
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 69, 0, 0.3);
            border-radius: 25px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 50px rgba(255, 69, 0, 0.05);
            position: relative;
            overflow: hidden;
        }
        
        .feed-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 69, 0, 0.1), transparent);
            animation: scan 3s infinite;
        }
        
        @keyframes scan {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .feed-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid rgba(255, 69, 0, 0.3);
        }
        
        .feed-column-headers {
            display: grid;
            grid-template-columns: 150px 120px 1fr 80px 150px;
            gap: 15px;
            padding: 15px 20px;
            background: rgba(255, 69, 0, 0.1);
            border-bottom: 1px solid rgba(255, 69, 0, 0.3);
            margin-bottom: 10px;
            border-radius: 8px;
        }
        
        .feed-column-header {
            font-size: 0.85rem;
            color: #FF4500;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
            cursor: pointer;
            user-select: none;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .feed-column-header:hover {
            color: #FF8C00;
            text-shadow: 0 0 10px rgba(255, 69, 0, 0.5);
        }
        
        .feed-column-header.sort-asc::after {
            content: ' ▲';
            font-size: 0.7rem;
            opacity: 0.8;
        }
        
        .feed-column-header.sort-desc::after {
            content: ' ▼';
            font-size: 0.7rem;
            opacity: 0.8;
        }
        
        .feed-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #FF4500;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .refresh-indicator {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .refresh-indicator.active {
            color: #FF4500;
            animation: pulse-dot 1s infinite;
        }
        
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        #leadsFeed {
            max-height: 600px;
            overflow-y: auto;
            padding-right: 10px;
        }
        
        #leadsFeed::-webkit-scrollbar {
            width: 8px;
        }
        
        #leadsFeed::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        
        #leadsFeed::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #FF4500, #FF8C00);
            border-radius: 10px;
        }
        
        .lead-item {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid rgba(255, 69, 0, 0.5);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-50px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .lead-item.new-lead {
            animation: flashIn 0.8s ease-out;
            border-left-color: #FF4500;
            box-shadow: 0 0 30px rgba(255, 69, 0, 0.5);
            background: rgba(255, 69, 0, 0.1);
        }
        
        @keyframes flashIn {
            0% {
                opacity: 0;
                transform: translateX(-100px) scale(0.9);
                box-shadow: 0 0 0 rgba(255, 69, 0, 0);
            }
            50% {
                box-shadow: 0 0 50px rgba(255, 69, 0, 0.8);
                transform: translateX(10px) scale(1.02);
            }
            100% {
                opacity: 1;
                transform: translateX(0) scale(1);
                box-shadow: 0 0 30px rgba(255, 69, 0, 0.5);
            }
        }
        
        .lead-item:hover {
            transform: translateX(5px);
            border-left-color: #FF4500;
            background: rgba(255, 255, 255, 0.05);
            box-shadow: 0 5px 20px rgba(255, 69, 0, 0.2);
        }
        
        .lead-fields {
            display: grid;
            grid-template-columns: 150px 120px 1fr 80px 150px;
            gap: 15px;
            align-items: center;
        }
        
        .lead-field {
            display: flex;
            flex-direction: column;
        }
        
        .lead-label {
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
            font-weight: 600;
        }
        
        .lead-value {
            font-size: 1rem;
            color: #fff;
            font-weight: 500;
            word-break: break-word;
        }
        
        .lead-value.highlight {
            color: #FF4500;
            font-weight: 700;
        }
        
        .lead-value a {
            color: #FF4500;
            text-decoration: none;
            border-bottom: 1px solid rgba(255, 69, 0, 0.5);
            transition: all 0.2s ease;
            display: inline-block;
        }
        
        .lead-value a:hover {
            color: #FF8C00;
            border-bottom-color: #FF4500;
            transform: translateY(-1px);
            text-shadow: 0 0 10px rgba(255, 69, 0, 0.5);
        }
        
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: rgba(255, 255, 255, 0.5);
        }
        
        .empty-state svg {
            width: 80px;
            height: 80px;
            margin-bottom: 20px;
            opacity: 0.3;
        }
        
        .reddit-particles {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 2;
            overflow: hidden;
        }
        
        .particle {
            position: absolute;
            width: 4px;
            height: 4px;
            background: #FF4500;
            border-radius: 50%;
            opacity: 0;
            animation: fall 3s linear infinite;
            box-shadow: 0 0 10px #FF4500;
        }
        
        @keyframes fall {
            0% {
                opacity: 1;
                transform: translateY(-100px) translateX(0);
            }
            100% {
                opacity: 0;
                transform: translateY(100vh) translateX(50px);
            }
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5rem;
            }
            
            .lead-fields, .feed-column-headers {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="reddit-particles" id="particles"></div>
    
    <div class="container">
        <div class="header">
            <h1>🔴 Live Reddit Leads</h1>
            <p>Real-time Reddit monitoring powered by PRAW</p>
        </div>
        
        <div class="controls">
            <button class="btn" id="toggleUniques">Show Uniques</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalLeads">0</div>
                <div class="stat-label">Total Posts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uniqueLeads">0</div>
                <div class="stat-label">Unique Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="newLeads">0</div>
                <div class="stat-label">New This Cycle</div>
            </div>
        </div>
        
        <div class="feed-container">
            <div class="feed-header">
                <div class="feed-title">📊 Live Feed</div>
                <div class="refresh-indicator" id="refreshIndicator">Refreshing every 30s</div>
            </div>
            <div class="feed-column-headers">
                <div class="feed-column-header" data-sort="username">Username</div>
                <div class="feed-column-header" data-sort="subreddit">Subreddit</div>
                <div class="feed-column-header" data-sort="title">Title</div>
                <div class="feed-column-header" data-sort="score">Score</div>
                <div class="feed-column-header" data-sort="created">Created</div>
            </div>
            <div id="leadsFeed">
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <p>Loading Reddit posts...</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let showUniques = false;
        let currentLeads = [];
        let previousLeads = [];
        let sortColumn = null;
        let sortDirection = 'asc';
        
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 20; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = Math.random() * 3 + 's';
                particle.style.animationDuration = (Math.random() * 2 + 2) + 's';
                particlesContainer.appendChild(particle);
            }
        }
        
        function getFieldValue(lead, sortKey) {
            const keyMap = {
                'username': 'Username',
                'subreddit': 'Subreddit',
                'title': 'Title',
                'score': 'Score',
                'created': 'Created'
            };
            const actualKey = keyMap[sortKey] || sortKey;
            return (lead[actualKey] || '').toString().toLowerCase();
        }
        
        function sortLeads(leads, column, direction) {
            if (!column) return leads;
            
            const sorted = [...leads].sort((a, b) => {
                const aVal = getFieldValue(a, column);
                const bVal = getFieldValue(b, column);
                
                // For score, compare as numbers
                if (column === 'score') {
                    const aNum = parseInt(aVal) || 0;
                    const bNum = parseInt(bVal) || 0;
                    return direction === 'asc' ? aNum - bNum : bNum - aNum;
                }
                
                if (aVal < bVal) return direction === 'asc' ? -1 : 1;
                if (aVal > bVal) return direction === 'asc' ? 1 : -1;
                return 0;
            });
            
            return sorted;
        }
        
        function updateSortHeaders() {
            const headers = document.querySelectorAll('.feed-column-header');
            headers.forEach(header => {
                header.classList.remove('sort-asc', 'sort-desc');
                if (header.dataset.sort === sortColumn) {
                    header.classList.add(sortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
                }
            });
        }
        
        function renderLeads(leads, isNewFetch = false, error = null) {
            const feed = document.getElementById('leadsFeed');
            
            if (error) {
                feed.innerHTML = `<div class="empty-state" style="color: #FF4500;"><p style="font-size: 1.2rem; margin-bottom: 10px;">⚠️ ${error}</p><p style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Please check your Reddit API credentials</p></div>`;
                return;
            }
            
            if (leads.length === 0) {
                feed.innerHTML = '<div class="empty-state"><p>No posts found</p></div>';
                return;
            }
            
            const sortedLeads = sortLeads(leads, sortColumn, sortDirection);
            
            const newLeadSignatures = new Set();
            if (isNewFetch && previousLeads.length > 0) {
                previousLeads.forEach(lead => {
                    newLeadSignatures.add(JSON.stringify(lead));
                });
            }
            
            feed.innerHTML = sortedLeads.map((lead, index) => {
                const leadSignature = JSON.stringify(lead);
                const isNew = isNewFetch && !newLeadSignatures.has(leadSignature);
                
                return `
                    <div class="lead-item ${isNew ? 'new-lead' : ''}" data-index="${index}">
                        <div class="lead-fields">
                            <div class="lead-field">
                                <div class="lead-label">Username</div>
                                <div class="lead-value ${isNew ? 'highlight' : ''}">${lead.Username || 'N/A'}</div>
                            </div>
                            <div class="lead-field">
                                <div class="lead-label">Subreddit</div>
                                <div class="lead-value ${isNew ? 'highlight' : ''}">r/${lead.Subreddit || 'N/A'}</div>
                            </div>
                            <div class="lead-field">
                                <div class="lead-label">Title</div>
                                <div class="lead-value ${isNew ? 'highlight' : ''}">${lead.Title || 'N/A'}</div>
                            </div>
                            <div class="lead-field">
                                <div class="lead-label">Score</div>
                                <div class="lead-value ${isNew ? 'highlight' : ''}">${lead.Score || '0'}</div>
                            </div>
                            <div class="lead-field">
                                <div class="lead-label">Link</div>
                                <div class="lead-value ${isNew ? 'highlight' : ''}">
                                    <a href="${lead.Link}" target="_blank" rel="noopener noreferrer">View Post</a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
            
            document.getElementById('totalLeads').textContent = currentLeads.length;
            document.getElementById('uniqueLeads').textContent = getUniqueLeads(currentLeads).length;
            
            if (isNewFetch) {
                const newCount = leads.length - previousLeads.length;
                document.getElementById('newLeads').textContent = Math.max(0, newCount);
            }
        }
        
        function getUniqueLeads(leads) {
            const seen = new Set();
            const unique = [];
            
            leads.forEach(lead => {
                const username = (lead.Username || '').trim();
                if (username && !seen.has(username)) {
                    seen.add(username);
                    unique.push(lead);
                } else if (!username) {
                    unique.push(lead);
                }
            });
            
            return unique;
        }
        
        async function fetchLeads() {
            try {
                const indicator = document.getElementById('refreshIndicator');
                indicator.textContent = 'Refreshing...';
                indicator.classList.add('active');
                
                const response = await fetch('/api/leads');
                const data = await response.json();
                
                previousLeads = [...currentLeads];
                currentLeads = data.leads;
                
                const leadsToShow = showUniques ? getUniqueLeads(currentLeads) : currentLeads;
                renderLeads(leadsToShow, true, data.error);
                
                if (data.error) {
                    indicator.textContent = 'Error accessing Reddit';
                    indicator.style.color = '#ff6b6b';
                } else {
                    indicator.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
                    indicator.style.color = '';
                }
                indicator.classList.remove('active');
                
                if (data.new_leads_count > 0) {
                    createParticleBurst();
                }
            } catch (error) {
                console.error('Error fetching leads:', error);
                document.getElementById('refreshIndicator').textContent = 'Error refreshing';
                document.getElementById('refreshIndicator').style.color = '#ff6b6b';
            }
        }
        
        function createParticleBurst() {
            const particlesContainer = document.getElementById('particles');
            for (let i = 0; i < 30; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = '20%';
                particle.style.animationDelay = '0s';
                particle.style.animationDuration = (Math.random() * 1 + 1.5) + 's';
                particlesContainer.appendChild(particle);
                
                setTimeout(() => particle.remove(), 3000);
            }
        }
        
        document.getElementById('toggleUniques').addEventListener('click', function() {
            showUniques = !showUniques;
            this.textContent = showUniques ? 'Show All' : 'Show Uniques';
            this.classList.toggle('active', showUniques);
            
            const leadsToShow = showUniques ? getUniqueLeads(currentLeads) : currentLeads;
            renderLeads(leadsToShow, false, null);
        });
        
        document.querySelectorAll('.feed-column-header').forEach(header => {
            header.addEventListener('click', function() {
                const column = this.dataset.sort;
                
                if (sortColumn === column) {
                    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    sortColumn = column;
                    sortDirection = 'asc';
                }
                
                updateSortHeaders();
                
                const leadsToShow = showUniques ? getUniqueLeads(currentLeads) : currentLeads;
                renderLeads(leadsToShow, false, null);
            });
        });
        
        fetchLeads();
        createParticles();
        setInterval(fetchLeads, 30000);
    </script>
</body>
</html>
    ''')

@app.route('/api/leads')
def api_leads():
    global last_leads, last_fetch_time
    
    # Check if credentials are configured
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        return jsonify({
            'leads': [],
            'new_leads_count': 0,
            'timestamp': datetime.now().isoformat(),
            'error': 'Reddit API credentials not configured. Please set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables.'
        })
    
    current_leads = fetch_leads()
    new_leads = get_new_leads(current_leads, last_leads)
    
    error_msg = None
    if not current_leads:
        error_msg = "No posts found. Check your subreddit configuration and Reddit API credentials."
    
    last_leads = current_leads
    last_fetch_time = datetime.now()
    
    return jsonify({
        'leads': current_leads,
        'new_leads_count': len(new_leads),
        'timestamp': last_fetch_time.isoformat(),
        'error': error_msg
    })

# For local development only
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
