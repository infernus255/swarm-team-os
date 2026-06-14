#!/usr/bin/env python3
import os
import sys
import socket
import argparse
import subprocess
import urllib.request
import json
from pathlib import Path

# Base Paths
INFRA_DIR = Path(__file__).resolve().parent
REPO_ROOT = INFRA_DIR.parent
KEY_PATH = REPO_ROOT / "docs" / "oracle-cloud" / "ssh-key-2026-06-10.key"

def load_oracle_ip() -> str:
    """Attempts to find the Oracle Cloud IP from environment or env files."""
    # Check env var first
    ip = os.getenv("ORACLE_IP")
    if ip:
        return ip
        
    # Check .env file
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("ORACLE_IP="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
                
    # Check config files
    hermes_env = REPO_ROOT / "config" / "hermes.env.example"
    if hermes_env.exists():
        for line in hermes_env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("ORACLE_IP="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
                
    return ""

def get_local_ip() -> str:
    """Discovers the primary local IP address of this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def check_sga_connection(url: str) -> bool:
    """Verifies that the SGA endpoint is up and responding to HTTP GET."""
    # Ensure URL protocol
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    
    print(f"🔍 [SGA Connection Test]: Checking connectivity to {url} ...")
    try:
        req = urllib.request.Request(f"{url}/", method="GET")
        with urllib.request.urlopen(req, timeout=3) as response:
            if response.status == 200:
                print("✅ [SGA Connection Test]: Connected successfully!")
                return True
    except Exception as e:
        print(f"❌ [SGA Connection Test]: Failed to connect: {e}")
    return False

def start_reverse_tunnel(oracle_ip: str):
    """Launches the SSH reverse port forwarding tunnel in the background."""
    if not oracle_ip:
        print("❌ Error: Oracle Cloud IP is not configured. Please set ORACLE_IP in your environment or .env file.")
        sys.exit(1)
        
    if not KEY_PATH.exists():
        print(f"❌ Error: SSH Private Key not found at {KEY_PATH}")
        sys.exit(1)

    # Set key permissions on Unix-like systems
    if os.name != 'nt':
        try:
            os.chmod(str(KEY_PATH), 0o600)
            print(f"🔒 Set private key permissions to 600 at {KEY_PATH.name}")
        except Exception as e:
            print(f"⚠️ Warning: Could not chmod private key: {e}")

    # Command: Forward Oracle port 8000 to local port 8000
    ssh_cmd = [
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-N",
        "-R", "8000:localhost:8000",
        "-i", str(KEY_PATH),
        f"ubuntu@{oracle_ip}"
    ]
    
    print(f"🚀 [Tunnel]: Starting reverse tunnel from Pentium (Local SGA) to Oracle Cloud ({oracle_ip})...")
    print(f"🏃 [Tunnel]: Running command: {' '.join(ssh_cmd)}")
    
    try:
        # Spawn as a background process
        process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("✨ [Tunnel]: Background SSH tunnel process spawned.")
        print("📌 To stop the tunnel, kill the SSH process or stop this execution.")
        
        # Verify it doesn't immediately exit
        try:
            outs, errs = process.communicate(timeout=2)
            print(f"⚠️ [Tunnel]: Tunnel exited early. STDOUT: {outs} | STDERR: {errs}")
        except subprocess.TimeoutExpired:
            print("✅ [Tunnel]: Tunnel established and running in background.")
            
    except Exception as e:
        print(f"❌ [Tunnel]: Failed to start SSH subprocess: {e}")

def export_lan_config():
    """Outputs/configures local environment parameters for other LAN nodes."""
    local_ip = get_local_ip()
    sga_url = f"http://{local_ip}:8000"
    
    print("\n🖥️ [LAN Sync Configurator]:")
    print("----------------------------------------")
    print(f"Local Pentium Host IP discovered: {local_ip}")
    print(f"Recommended SGA URL for Ryzen / Other Nodes: {sga_url}")
    print("----------------------------------------\n")
    
    print("👉 [Bash/Linux Shell]:")
    print(f"export SGA_URL={sga_url}")
    print("\n👉 [Windows PowerShell]:")
    print(f"$env:SGA_URL='{sga_url}'")
    print("\n👉 [CMD / Batch]:")
    print(f"set SGA_URL={sga_url}")
    
    # Proactively write/update .env file
    env_file = REPO_ROOT / ".env"
    lines = []
    found = False
    
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("SGA_URL="):
                lines.append(f"SGA_URL={sga_url}")
                found = True
            else:
                lines.append(line)
                
    if not found:
        lines.append(f"SGA_URL={sga_url}")
        
    try:
        env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n✨ Successfully updated/wrote SGA_URL to {env_file}")
    except Exception as e:
        print(f"\n⚠️ Could not write to .env file: {e}")

def main():
    parser = argparse.ArgumentParser(description="SwarmTeam OS Secure LAN Tunnel & Sync Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start Tunnel command
    parser_tunnel = subparsers.add_parser("start-tunnel", help="Start reverse SSH tunnel from Pentium to Oracle Cloud")
    parser_tunnel.add_argument("--oracle-ip", help="IP address of the Oracle Cloud gateway")
    
    # Check SGA connection
    parser_check = subparsers.add_parser("check-sga", help="Verify connection to SGA API")
    parser_check.add_argument("--url", default="http://localhost:8000", help="SGA target URL")
    
    # Export LAN config
    subparsers.add_parser("export-lan", help="Discover host IP and print connection parameters for Ryzen/other nodes")
    
    args = parser.parse_args()
    
    if args.command == "start-tunnel":
        oracle_ip = args.oracle_ip or load_oracle_ip()
        start_reverse_tunnel(oracle_ip)
    elif args.command == "check-sga":
        check_sga_connection(args.url)
    elif args.command == "export-lan":
        export_lan_config()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
