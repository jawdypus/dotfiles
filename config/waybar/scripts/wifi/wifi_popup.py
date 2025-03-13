#!/usr/bin/env python3
import subprocess
import curses
import re
import os
import time
import pty
import select
import sys
import termios
import tty

class WifiNetwork:
    def __init__(self, ssid, signal, security, in_use=False, autoconnect=False):
        self.ssid = ssid
        self.signal = signal  # 0-100
        self.security = security  # True if password protected
        self.in_use = in_use  # True if currently connected
        self.autoconnect = autoconnect

class WifiManager:
    def __init__(self):
        self.networks = []
        self.known_networks = self.load_known_networks()
        
    def load_known_networks(self):
        """Load previously connected networks from a file."""
        known = {}
        try:
            with open(os.path.expanduser("~/.wifi_tui_known_networks"), "r") as f:
                for line in f:
                    parts = line.strip().split("|")
                    if len(parts) >= 2:
                        ssid = parts[0]
                        autoconnect = parts[1].lower() == "true"
                        known[ssid] = autoconnect
        except FileNotFoundError:
            pass
        return known
    
    def save_known_networks(self):
        """Save connected networks to a file."""
        with open(os.path.expanduser("~/.wifi_tui_known_networks"), "w") as f:
            for ssid, autoconnect in self.known_networks.items():
                f.write(f"{ssid}|{autoconnect}\n")
    
    def is_wifi_enabled(self):
        """Check if WiFi is enabled."""
        try:
            result = subprocess.run(["nmcli", "radio", "wifi"], 
                                  capture_output=True, text=True, check=True)
            return "enabled" in result.stdout.lower()
        except Exception:
            return False
    
    def toggle_wifi(self):
        """Toggle WiFi on/off."""
        is_enabled = self.is_wifi_enabled()
        state = "off" if is_enabled else "on"
        subprocess.run(["nmcli", "radio", "wifi", state], check=True)
        return not is_enabled
    
    def scan_networks(self):
        """Scan for available WiFi networks."""
        self.networks = []
        try:
            result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,IN-USE", 
                                    "device", "wifi", "list", "--rescan", "yes"],
                                  capture_output=True, text=True, check=True)
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split(':')
                if len(parts) >= 4:
                    ssid = parts[0]
                    if not ssid:  # Skip networks with empty SSIDs
                        continue
                        
                    try:
                        signal = int(parts[1])
                    except ValueError:
                        signal = 0
                        
                    security = parts[2] != ""
                    in_use = parts[3] == "*"
                    
                    autoconnect = self.known_networks.get(ssid, False)
                    self.networks.append(WifiNetwork(ssid, signal, security, in_use, autoconnect))
            
            # Sort networks by signal strength (highest first)
            self.networks.sort(key=lambda x: (not x.in_use, -x.signal))
            
        except Exception as e:
            print(f"Error scanning networks: {e}")
    
    def connect_to_network(self, network):
        """Connect to the selected network."""
        if network.ssid in self.known_networks:
            # Use -a for known networks
            return self.execute_connect_command(["nmcli", "device", "wifi", "connect", network.ssid, "-a"])
        elif network.security:
            # For secured networks, use direct nmcli command for password prompt
            return self.execute_interactive_connect(network.ssid)
        else:
            # For open networks
            return self.execute_connect_command(["nmcli", "device", "wifi", "connect", network.ssid])
    
    def execute_interactive_connect(self, ssid):
        """Execute interactive connection with proper password prompt."""
        os.system('clear')
        print(f"Connecting to {ssid}...\n")
        
        # Save terminal settings
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            # Create a pseudo-terminal
            master, slave = pty.openpty()
            
            # Start the nmcli process
            cmd = ["nmcli", "device", "wifi", "connect", ssid, "-a"]
            process = subprocess.Popen(
                cmd,
                stdin=slave,
                stdout=slave,
                stderr=slave,
                universal_newlines=True
            )
            
            # Close the slave file descriptor
            os.close(slave)
            
            # Set terminal to raw mode
            tty.setraw(fd)
            
            output_buffer = ""
            connection_success = False
            
            while process.poll() is None:
                # Use select to check if there's data to read or if we can write
                r, w, e = select.select([master, fd], [], [], 0.1)
                
                # Read from the process's output
                if master in r:
                    try:
                        data = os.read(master, 1024).decode()
                        sys.stdout.write(data)
                        sys.stdout.flush()
                        output_buffer += data
                        
                        # Check if connection was successful
                        if "successfully activated" in output_buffer:
                            connection_success = True
                    except OSError:
                        break
                
                # Forward user input to the process
                if fd in r:
                    try:
                        char = os.read(fd, 1)
                        os.write(master, char)
                    except OSError:
                        break
            
            # Get final exit code
            exit_code = process.poll()
            
            # If process has ended, read any remaining output
            try:
                data = os.read(master, 1024).decode()
                sys.stdout.write(data)
                sys.stdout.flush()
                output_buffer += data
            except OSError:
                pass
            
            # Check if we've successfully connected
            if exit_code == 0 or connection_success or "successfully activated" in output_buffer:
                self.known_networks[ssid] = True
                self.save_known_networks()
                print("\nSuccessfully connected to network!")
                connection_success = True
            
        except Exception as e:
            print(f"\nError connecting to network: {e}")
            connection_success = False
            
        finally:
            # Restore terminal settings
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            # Close master file descriptor
            os.close(master)
            
            print("\nPress Enter to return to the WiFi manager...")
            input()
            return connection_success
    
    def execute_connect_command(self, command):
        """Execute the connection command and display its output."""
        try:
            # Clear the screen and reset terminal
            os.system('clear')
            print(f"Connecting to {command[4]}...\n")
            
            # Execute the command and wait for it to complete
            process = subprocess.Popen(command, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.STDOUT,
                                    stdin=subprocess.PIPE,
                                    universal_newlines=True)
            
            # Process output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
                    
            # Get the return code
            return_code = process.poll()
            
            # If connection was successful, add to known networks
            if return_code == 0:
                self.known_networks[command[4]] = True
                self.save_known_networks()
                
            print("\nPress Enter to return to the WiFi manager...")
            input()
            return return_code == 0
            
        except Exception as e:
            print(f"Error connecting to network: {e}")
            print("\nPress Enter to return to the WiFi manager...")
            input()
            return False
    
    def toggle_autoconnect(self, network):
        """Toggle autoconnect for a network."""
        if network.ssid in self.known_networks:
            current = self.known_networks[network.ssid]
            # Execute nmcli command to set autoconnect
            try:
                conn_name = self.get_connection_name(network.ssid)
                if conn_name:
                    autoconnect = "no" if current else "yes"
                    subprocess.run(["nmcli", "connection", "modify", conn_name, 
                                  "connection.autoconnect", autoconnect], check=True)
                    self.known_networks[network.ssid] = not current
                    self.save_known_networks()
                    
                    # Update the network object
                    for net in self.networks:
                        if net.ssid == network.ssid:
                            net.autoconnect = not current
                            break
                    
                    return True
            except Exception as e:
                print(f"Error toggling autoconnect: {e}")
                time.sleep(2)
        return False
    
    def get_connection_name(self, ssid):
        """Get the connection name for an SSID."""
        try:
            result = subprocess.run(["nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show"],
                                  capture_output=True, text=True, check=True)
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split(':')
                if len(parts) >= 2 and parts[0] == ssid:
                    return parts[0]
                    
        except Exception:
            pass
        return None

def draw_signal_bars(signal, width=5):
    """Draw signal strength indicator using Jetbrains Mono font characters."""
    if signal >= 80:
        return "▰▰▰▰▰"
    elif signal >= 60:
        return "▰▰▰▰▱"
    elif signal >= 40:
        return "▰▰▰▱▱"
    elif signal >= 20:
        return "▰▰▱▱▱"
    else:
        return "▰▱▱▱▱"

def draw_main_screen(stdscr, wifi_manager, selected_idx):
    """Draw the main TUI screen."""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    # Check terminal size
    if height < 10 or width < 40:
        stdscr.addstr(0, 0, "Terminal too small")
        stdscr.refresh()
        return
    
    # Title
    title = "WiFi Manager"
    stdscr.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)
    
    # WiFi toggle option (always first)
    wifi_status = "ON" if wifi_manager.is_wifi_enabled() else "OFF"
    toggle_text = f"[Toggle WiFi: {wifi_status}]"
    
    if selected_idx == 0:
        stdscr.addstr(3, 2, toggle_text, curses.A_REVERSE)
    else:
        stdscr.addstr(3, 2, toggle_text)
    
    # Header
    stdscr.addstr(5, 2, "SSID", curses.A_BOLD)
    stdscr.addstr(5, width - 25, "Signal", curses.A_BOLD)
    stdscr.addstr(5, width - 15, "Security", curses.A_BOLD)
    stdscr.addstr(5, width - 5, "Auto", curses.A_BOLD)
    stdscr.addstr(6, 2, "─" * (width - 4))
    
    # Networks list
    start_y = 7
    max_networks = height - start_y - 2
    
    # Calculate indices to display
    total_networks = len(wifi_manager.networks)
    if total_networks == 0:
        stdscr.addstr(start_y, 2, "No networks found")
    else:
        # Adjust selected index if it's the toggle option
        list_idx = selected_idx - 1 if selected_idx > 0 else 0
        
        # Calculate start and end indices for scrolling
        start_idx = max(0, list_idx - max_networks // 2)
        end_idx = min(total_networks, start_idx + max_networks)
        
        for i, idx in enumerate(range(start_idx, end_idx)):
            network = wifi_manager.networks[idx]
            y = start_y + i
            
            # Network name (truncate if too long)
            max_ssid_len = width - 30
            ssid = network.ssid[:max_ssid_len] + ('...' if len(network.ssid) > max_ssid_len else '')
            
            # Format row
            text = f"{ssid}"
            
            # Set attributes based on selection and connection status
            attrs = curses.A_NORMAL
            if idx + 1 == selected_idx:
                attrs |= curses.A_REVERSE
            if network.in_use:
                attrs |= curses.A_BOLD
            
            stdscr.addstr(y, 2, text, attrs)
            
            # Signal strength
            signal_bars = draw_signal_bars(network.signal)
            stdscr.addstr(y, width - 25, signal_bars)
            
            # Security
            if network.security:
                stdscr.addstr(y, width - 15, "🔒")
            else:
                stdscr.addstr(y, width - 15, "  ")
            
            # Autoconnect
            if network.autoconnect:
                stdscr.addstr(y, width - 5, "✓")
    
    # Footer
    footer_y = height - 2
    stdscr.addstr(footer_y, 2, "─" * (width - 4))
    stdscr.addstr(footer_y + 1, 2, "↑/↓: Navigate | Enter: Connect | A: Toggle Autoconnect | R: Refresh | Q: Quit")
    
    stdscr.refresh()

def main(stdscr):
    """Main function for the TUI."""
    # Setup
    curses.curs_set(0)  # Hide cursor
    stdscr.timeout(100)  # Non-blocking input
    
    wifi_manager = WifiManager()
    selected_idx = 0
    
    # Initial scan
    wifi_manager.scan_networks()
    
    # Main loop
    while True:
        draw_main_screen(stdscr, wifi_manager, selected_idx)
        
        try:
            key = stdscr.getch()
        except:
            key = -1
            
        # Handle key presses
        if key == ord('q') or key == ord('Q'):
            break
        elif key == curses.KEY_UP:
            selected_idx = max(0, selected_idx - 1)
        elif key == curses.KEY_DOWN:
            max_idx = len(wifi_manager.networks) + 1  # +1 for toggle option
            selected_idx = min(max_idx - 1, selected_idx + 1)
        elif key == ord('r') or key == ord('R'):
            wifi_manager.scan_networks()
            selected_idx = 0
        elif key == ord('a') or key == ord('A'):
            # Toggle autoconnect for selected network
            if selected_idx > 0 and selected_idx <= len(wifi_manager.networks):
                network = wifi_manager.networks[selected_idx - 1]
                wifi_manager.toggle_autoconnect(network)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            if selected_idx == 0:
                # Toggle WiFi
                wifi_manager.toggle_wifi()
                wifi_manager.scan_networks()
            elif selected_idx <= len(wifi_manager.networks):
                # Connect to network
                network = wifi_manager.networks[selected_idx - 1]
                curses.endwin()  # Temporarily exit curses mode
                wifi_manager.connect_to_network(network)
                wifi_manager.scan_networks()
                curses.curs_set(0)  # Hide cursor again after returning
                
        # Refresh every 30 seconds
        if time.time() % 30 < 0.1:
            wifi_manager.scan_networks()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
