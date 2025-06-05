import json
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import AWS integration (optional)
try:
    from aws_integration import AWSJournalBackup, DynamoDBJournalStore, check_aws_credentials
    aws_available = True
except ImportError:
    logger.warning("AWS integration not available. Running without cloud backup.")
    aws_available = False

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
PASSWORD = os.environ.get('PASSWORD', 'GVISIT')
JOURNAL_FILE = "journal_entries.json"
PPTX_FOLDER = 'secure_powerpoints'
PPTX_FILES = {'ppt1': 'presentation1.pptx', 'ppt2': 'presentation2.pptx'}

# Initialize AWS services if available
aws_backup = None
dynamodb_store = None

if aws_available and check_aws_credentials():
    # Initialize S3 backup if configured
    if os.environ.get('S3_BACKUP_BUCKET'):
        aws_backup = AWSJournalBackup(
            bucket_name=os.environ.get('S3_BACKUP_BUCKET'),
            region=os.environ.get('AWS_REGION', 'us-east-1')
        )
        logger.info("AWS S3 backup initialized")
    
    # Initialize DynamoDB if configured
    if os.environ.get('USE_DYNAMODB', 'false').lower() == 'true':
        dynamodb_store = DynamoDBJournalStore(
            table_name=os.environ.get('DYNAMODB_TABLE_NAME'),
            region=os.environ.get('AWS_REGION', 'us-east-1')
        )
        logger.info("DynamoDB storage initialized")

# Enhanced journal configuration
JOURNAL_FOCUSES = [
    "Daily Reflection",
    "Weekly Goals", 
    "Monthly Review",
    "Brain Dump",
    "Gratitude List",
    "Project Planning",
    "Learning Log"
]

MOOD_OPTIONS = [
    {"value": "excellent", "label": "😀 Excellent"},
    {"value": "good", "label": "🙂 Good"},
    {"value": "okay", "label": "😐 Okay"},
    {"value": "bad", "label": "🙁 Bad"},
    {"value": "awful", "label": "😩 Awful"}
]

ENERGY_LEVELS = ["High", "Medium", "Low"]

# Prompts for different focuses
FOCUS_PROMPTS = {
    "Daily Reflection": "What was a win today? What was a challenge? What did you learn?",
    "Weekly Goals": "What are your top 3 goals for this week? What steps will you take?",
    "Monthly Review": "What progress did you make this month? What habits served you well?",
    "Brain Dump": "What's on your mind? Get it all out here...",
    "Gratitude List": "List everything you're grateful for today, big or small.",
    "Project Planning": "What project are you working on? Break down the next steps.",
    "Learning Log": "What did you learn today? How can you apply it?"
}

if not os.path.exists(PPTX_FOLDER):
    os.makedirs(PPTX_FOLDER)

def get_journal_entries():
    """Get journal entries from DynamoDB or local file"""
    if dynamodb_store:
        return dynamodb_store.get_all_entries()
    
    if not os.path.exists(JOURNAL_FILE):
        # Try to restore from S3 backup if available
        if aws_backup:
            entries = aws_backup.restore_from_backup()
            if entries:
                logger.info("Restored entries from S3 backup")
                with open(JOURNAL_FILE, 'w') as f:
                    json.dump(entries, f, indent=4)
                return entries
        return []
    
    try:
        with open(JOURNAL_FILE, 'r') as f:
            entries = json.load(f)
        return entries
    except json.JSONDecodeError:
        return []

def save_journal_entries(entries):
    """Save journal entries to local file and backup to S3"""
    # Save to local file
    with open(JOURNAL_FILE, 'w') as f:
        json.dump(entries, f, indent=4)
    
    # Backup to S3 if available
    if aws_backup:
        aws_backup.backup_entries(entries)

def add_journal_entry(entry_data):
    entries = get_journal_entries()
    entry = {
        "id": len(entries) + 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": datetime.now().strftime("%B %d, %Y"),
        "time": datetime.now().strftime("%I:%M %p"),
        "focus": entry_data.get("focus"),
        "content": entry_data.get("content"),
        "mood": entry_data.get("mood"),
        "energy": entry_data.get("energy"),
        "gratitude": entry_data.get("gratitude", []),
        "action_item": entry_data.get("action_item"),
        "version": "2.0"
    }
    
    if dynamodb_store:
        # Add to DynamoDB
        dynamodb_store.add_entry(entry)
    else:
        # Add to local list and save
        entries.append(entry)
        save_journal_entries(entries)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login/<ppt_id>', methods=['GET', 'POST'])
def login(ppt_id):
    if ppt_id not in ['ppt1', 'ppt2']:
        flash("Invalid presentation ID.", "error")
        return redirect(url_for('home'))

    if request.method == 'POST':
        password = request.form.get('password')
        if password == PASSWORD:
            session[f'authenticated_{ppt_id}'] = True
            return redirect(url_for('powerpoint_page', ppt_id=ppt_id))
        else:
            flash("Incorrect password. Please try again.", "error")
    return render_template('login.html', ppt_id=ppt_id)

@app.route('/download_ppt/<ppt_id>')
def download_ppt(ppt_id):
    if ppt_id not in PPTX_FILES:
        flash("Invalid presentation ID.", "error")
        return redirect(url_for('home'))

    if not session.get(f'authenticated_{ppt_id}'):
        flash("You need to enter the password to download this file.", "warning")
        return redirect(url_for('login', ppt_id=ppt_id))
    
    try:
        return send_from_directory(PPTX_FOLDER, PPTX_FILES[ppt_id], as_attachment=True)
    except FileNotFoundError:
        flash("File not found on server. Please place the file in the 'secure_powerpoints' folder.", "error")
        return redirect(url_for('powerpoint_page', ppt_id=ppt_id))

@app.route('/powerpoint/<ppt_id>')
def powerpoint_page(ppt_id):
    if not session.get(f'authenticated_{ppt_id}'):
        flash("You need to enter the password to view this page.", "warning")
        return redirect(url_for('login', ppt_id=ppt_id))
    
    return render_template(f'{ppt_id}.html', ppt_id=ppt_id, ppt_file_name=PPTX_FILES.get(ppt_id))

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if request.method == 'POST':
        # Collect all the form data
        focus = request.form.get('focus')
        content = request.form.get('content')
        mood = request.form.get('mood')
        energy = request.form.get('energy')
        action_item = request.form.get('action_item')
        
        # Handle gratitude items (up to 3)
        gratitude = []
        for i in range(1, 4):
            item = request.form.get(f'gratitude_{i}')
            if item and item.strip():
                gratitude.append(item.strip())
        
        # Validate required fields
        if focus and content and mood and energy:
            entry_data = {
                "focus": focus,
                "content": content,
                "mood": mood,
                "energy": energy,
                "gratitude": gratitude,
                "action_item": action_item
            }
            add_journal_entry(entry_data)
            flash("Journal entry added successfully!", "success")
        else:
            flash("Please fill in all required fields.", "error")
        return redirect(url_for('journal'))
    
    entries = get_journal_entries()
    return render_template('journal.html', 
                         entries=entries, 
                         focuses=JOURNAL_FOCUSES,
                         mood_options=MOOD_OPTIONS,
                         energy_levels=ENERGY_LEVELS,
                         focus_prompts=FOCUS_PROMPTS,
                         aws_enabled=bool(aws_backup or dynamodb_store))

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "aws_backup": bool(aws_backup), "dynamodb": bool(dynamodb_store)}, 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5002))
    app.run(debug=os.environ.get('FLASK_ENV') != 'production', port=port) 