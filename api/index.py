from flask import Flask, render_template_string, jsonify
import requests
import csv
import io
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Configure for production
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
app.config['DEBUG'] = False

# Google Sheet ID from the URL
SHEET_ID = "1PSj_fW0ppLk2OdaRDH4IBTkeXptfxYRL21wF66N7x48"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Store last seen leads for detecting new ones
last_leads = []
last_fetch_time = None

def fetch_leads():
    """Fetch leads from Google Sheet"""
    try:
        response = requests.get(SHEET_URL, timeout=10)
        response.raise_for_status()
        
        # Check if we got HTML instead of CSV (means sheet is not public)
        if response.text.strip().startswith('<!DOCTYPE') or '<html' in response.text.lower():
            print("ERROR: Google Sheet is not publicly accessible. Please share it with 'Anyone with the link can view'")
            return []
        
        # Parse CSV
        csv_data = response.text
        reader = csv.DictReader(io.StringIO(csv_data))
        leads = []
        
        for row in reader:
            # Clean up the row data
            lead = {k.strip(): v.strip() if v else "" for k, v in row.items()}
            # Only add leads that have at least one non-empty field
            if any(v for v in lead.values()):
                leads.append(lead)
        
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
        # Get the first field value (which is the username)
        keys = list(lead.keys())
        username = keys[0] if keys else None
        username_value = lead[username].strip() if username and lead[username] else None
        
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
    <title>Live Leads Feed</title>
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
                radial-gradient(circle at 20% 50%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 215, 0, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 40% 20%, rgba(255, 215, 0, 0.06) 0%, transparent 50%);
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
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FFD700 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 40px rgba(255, 215, 0, 0.5);
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
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            color: #000;
            box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(255, 215, 0, 0.5);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn.active {
            background: linear-gradient(135deg, #FFA500 0%, #FF8C00 100%);
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
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 20px;
            padding: 20px 30px;
            text-align: center;
            min-width: 150px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #FFD700;
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
            border: 1px solid rgba(255, 215, 0, 0.3);
            border-radius: 25px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5), inset 0 0 50px rgba(255, 215, 0, 0.05);
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
            background: linear-gradient(90deg, transparent, rgba(255, 215, 0, 0.1), transparent);
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
            border-bottom: 2px solid rgba(255, 215, 0, 0.3);
        }
        
        .feed-column-headers {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 15px 20px;
            background: rgba(255, 215, 0, 0.1);
            border-bottom: 1px solid rgba(255, 215, 0, 0.3);
            margin-bottom: 10px;
            border-radius: 8px;
        }
        
        .feed-column-header {
            font-size: 0.85rem;
            color: #FFD700;
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
            color: #FFA500;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
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
            color: #FFD700;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .refresh-indicator {
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
        }
        
        .refresh-indicator.active {
            color: #FFD700;
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
            background: linear-gradient(180deg, #FFD700, #FFA500);
            border-radius: 10px;
        }
        
        .lead-item {
            background: rgba(255, 255, 255, 0.03);
            border-left: 4px solid rgba(255, 215, 0, 0.5);
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
            border-left-color: #FFD700;
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
            background: rgba(255, 215, 0, 0.1);
        }
        
        @keyframes flashIn {
            0% {
                opacity: 0;
                transform: translateX(-100px) scale(0.9);
                box-shadow: 0 0 0 rgba(255, 215, 0, 0);
            }
            50% {
                box-shadow: 0 0 50px rgba(255, 215, 0, 0.8);
                transform: translateX(10px) scale(1.02);
            }
            100% {
                opacity: 1;
                transform: translateX(0) scale(1);
                box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
            }
        }
        
        .lead-item:hover {
            transform: translateX(5px);
            border-left-color: #FFD700;
            background: rgba(255, 255, 255, 0.05);
            box-shadow: 0 5px 20px rgba(255, 215, 0, 0.2);
        }
        
        .lead-fields {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
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
            color: #FFD700;
            font-weight: 700;
        }
        
        .lead-value a {
            color: #FFD700;
            text-decoration: none;
            border-bottom: 1px solid rgba(255, 215, 0, 0.5);
            transition: all 0.2s ease;
            display: inline-block;
        }
        
        .lead-value a:hover {
            color: #FFA500;
            border-bottom-color: #FFD700;
            transform: translateY(-1px);
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
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
        
        .golden-particles {
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
            background: #FFD700;
            border-radius: 50%;
            opacity: 0;
            animation: fall 3s linear infinite;
            box-shadow: 0 0 10px #FFD700;
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
            
            .lead-fields {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="golden-particles" id="particles"></div>
    
    <div class="container">
        <div class="header">
            <h1>💰 Live Leads Feed</h1>
            <p>Real-time lead monitoring • Premium Edition</p>
        </div>
        
        <div class="controls">
            <button class="btn" id="toggleUniques">Show Uniques</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value" id="totalLeads">0</div>
                <div class="stat-label">Total Leads</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="uniqueLeads">0</div>
                <div class="stat-label">Unique Leads</div>
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
                <div class="feed-column-header" data-sort="sub">Sub</div>
                <div class="feed-column-header" data-sort="subject">Subject</div>
                <div class="feed-column-header" data-sort="link">Link</div>
            </div>
            <div id="leadsFeed">
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <p>Loading leads...</p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let showUniques = false;
        let currentLeads = [];
        let previousLeads = [];
        let sortColumn = null;
        let sortDirection = 'asc'; // 'asc' or 'desc'
        
        // Create golden particles
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
        
        function formatLead(lead) {
            // Detect field types and assign headers
            const fields = Object.entries(lead)
                .filter(([key, value]) => value && value.trim())
                .map(([key, value], index) => {
                    let label = key;
                    let displayValue = value.trim();
                    let isUrl = false;
                    let sortKey = null;
                    
                    // Detect if value is a URL
                    if (displayValue.includes('http') || displayValue.includes('reddit.com')) {
                        isUrl = true;
                    }
                    
                    // Assign proper headers based on field position and content
                    if (index === 0) {
                        // First field is username
                        label = 'Username';
                        sortKey = 'username';
                    } else if (index === 1 && !isUrl && displayValue.length < 50) {
                        // Second field is usually subreddit
                        label = 'Subreddit';
                        sortKey = 'sub';
                    } else if (isUrl) {
                        // URL field
                        label = 'Link';
                        sortKey = 'link';
                    } else if (key.includes('https://') || key.includes('reddit.com')) {
                        // Field name itself is a URL pattern
                        label = 'Link';
                        isUrl = true;
                        sortKey = 'link';
                    } else {
                        // Post title or other content
                        label = key.length > 50 ? 'Post Title' : key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                        sortKey = 'subject';
                    }
                    
                    return {
                        label: label,
                        value: displayValue,
                        isUrl: isUrl,
                        sortKey: sortKey
                    };
                });
            
            return fields;
        }
        
        function getFieldValue(lead, sortKey) {
            const fields = formatLead(lead);
            const field = fields.find(f => f.sortKey === sortKey);
            return field ? field.value.toLowerCase() : '';
        }
        
        function sortLeads(leads, column, direction) {
            if (!column) return leads;
            
            const sorted = [...leads].sort((a, b) => {
                const aVal = getFieldValue(a, column);
                const bVal = getFieldValue(b, column);
                
                // Compare values
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
                feed.innerHTML = `<div class="empty-state" style="color: #FFD700;"><p style="font-size: 1.2rem; margin-bottom: 10px;">⚠️ ${error}</p><p style="font-size: 0.9rem; color: rgba(255,255,255,0.7);">Make sure your Google Sheet is shared with "Anyone with the link can view"</p></div>`;
                return;
            }
            
            if (leads.length === 0) {
                feed.innerHTML = '<div class="empty-state"><p>No leads found</p></div>';
                return;
            }
            
            // Apply sorting
            const sortedLeads = sortLeads(leads, sortColumn, sortDirection);
            
            // Identify new leads
            const newLeadSignatures = new Set();
            if (isNewFetch && previousLeads.length > 0) {
                previousLeads.forEach(lead => {
                    const sig = JSON.stringify(lead);
                    newLeadSignatures.add(sig);
                });
            }
            
            feed.innerHTML = sortedLeads.map((lead, index) => {
                const fields = formatLead(lead);
                const leadSignature = JSON.stringify(lead);
                const isNew = isNewFetch && !newLeadSignatures.has(leadSignature);
                
                if (isNew) {
                    newLeadSignatures.add(leadSignature);
                }
                
                return `
                    <div class="lead-item ${isNew ? 'new-lead' : ''}" data-index="${index}">
                        <div class="lead-fields">
                            ${fields.map(field => `
                                <div class="lead-field">
                                    <div class="lead-label">${field.label}</div>
                                    <div class="lead-value ${isNew ? 'highlight' : ''}">
                                        ${field.isUrl ? `<a href="${field.value}" target="_blank" rel="noopener noreferrer">${field.value}</a>` : field.value}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }).join('');
            
            // Update stats
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
                // Uniqueness based on username only
                // Get the first field value (which is the username)
                const keys = Object.keys(lead);
                const username = keys.length > 0 ? (lead[keys[0]] || '').trim() : null;
                
                // Use username as the unique identifier
                if (username && !seen.has(username)) {
                    seen.add(username);
                    unique.push(lead);
                } else if (!username) {
                    // If no username found, include it anyway
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
                    indicator.textContent = 'Error accessing sheet';
                    indicator.style.color = '#ff6b6b';
                } else {
                    indicator.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
                    indicator.style.color = '';
                }
                indicator.classList.remove('active');
                
                // Create burst of particles for new leads
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
        
        // Toggle uniques
        document.getElementById('toggleUniques').addEventListener('click', function() {
            showUniques = !showUniques;
            this.textContent = showUniques ? 'Show All' : 'Show Uniques';
            this.classList.toggle('active', showUniques);
            
            const leadsToShow = showUniques ? getUniqueLeads(currentLeads) : currentLeads;
            renderLeads(leadsToShow, false, null);
        });
        
        // Sortable headers
        document.querySelectorAll('.feed-column-header').forEach(header => {
            header.addEventListener('click', function() {
                const column = this.dataset.sort;
                
                // If clicking the same column, reverse direction
                if (sortColumn === column) {
                    sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    // New column, start with ascending
                    sortColumn = column;
                    sortDirection = 'asc';
                }
                
                // Update header visuals
                updateSortHeaders();
                
                // Re-render with sorted leads
                const leadsToShow = showUniques ? getUniqueLeads(currentLeads) : currentLeads;
                renderLeads(leadsToShow, false, null);
            });
        });
        
        // Initial load
        fetchLeads();
        createParticles();
        
        // Auto-refresh every 30 seconds
        setInterval(fetchLeads, 30000);
    </script>
</body>
</html>
    ''')

@app.route('/api/leads')
def api_leads():
    global last_leads, last_fetch_time
    
    current_leads = fetch_leads()
    new_leads = get_new_leads(current_leads, last_leads)
    
    # Check if sheet is accessible
    error_msg = None
    if not current_leads:
        try:
            response = requests.get(SHEET_URL, timeout=10)
            if response.text.strip().startswith('<!DOCTYPE') or '<html' in response.text.lower():
                error_msg = "Google Sheet is not publicly accessible. Please share it with 'Anyone with the link can view'"
        except:
            error_msg = "Unable to access Google Sheet. Please check the sharing settings."
    
    last_leads = current_leads
    last_fetch_time = datetime.now()
    
    return jsonify({
        'leads': current_leads,
        'new_leads_count': len(new_leads),
        'timestamp': last_fetch_time.isoformat(),
        'error': error_msg
    })

# Export handler for Vercel
# Vercel's @vercel/python adapter automatically handles Flask WSGI apps
# The handler must be the Flask app instance
handler = app
