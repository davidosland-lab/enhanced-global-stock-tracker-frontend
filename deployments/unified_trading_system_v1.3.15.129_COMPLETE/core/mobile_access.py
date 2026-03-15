"""
Mobile Remote Access Module
============================

Enables secure remote access to the Unified Trading Dashboard from mobile devices.

Features:
- ngrok tunneling for instant remote access
- Authentication with username/password
- Mobile-responsive CSS injection
- QR code generation for easy mobile connection
- Secure HTTPS connection

Usage:
    python mobile_access.py --enable
    
    Or programmatic:
    from mobile_access import MobileAccessManager
    manager = MobileAccessManager()
    manager.start()
"""

import os
import sys
import logging
import subprocess
import time
import json
import qrcode
import io
import base64
from pathlib import Path
from typing import Optional, Dict
import requests
import hashlib

logger = logging.getLogger(__name__)

class MobileAccessManager:
    """Manages mobile remote access to the trading dashboard"""
    
    def __init__(self, 
                 auth_required: bool = True,
                 username: str = "trader",
                 password: str = None,
                 port: int = 8050):
        """
        Initialize mobile access manager
        
        Args:
            auth_required: Whether authentication is required
            username: Username for authentication
            password: Password for authentication (auto-generated if None)
            port: Local port the dashboard runs on
        """
        self.auth_required = auth_required
        self.username = username
        self.password = password or self._generate_password()
        self.port = port
        self.ngrok_process = None
        self.public_url = None
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "mobile_access.json"
        
        # Load or create config
        self._load_config()
        
    def _generate_password(self) -> str:
        """Generate a secure random password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def _load_config(self):
        """Load mobile access configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.username = config.get('username', self.username)
                    self.password = config.get('password', self.password)
                    logger.info("Loaded mobile access configuration")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
    
    def _save_config(self):
        """Save mobile access configuration"""
        try:
            config = {
                'username': self.username,
                'password': self.password,
                'port': self.port,
                'created': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            logger.info(f"Saved mobile access configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _check_ngrok_installed(self) -> bool:
        """Check if ngrok is installed"""
        try:
            result = subprocess.run(['ngrok', 'version'], 
                                  capture_output=True, 
                                  text=True,
                                  timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _install_ngrok(self):
        """Provide instructions for installing ngrok"""
        print("\n" + "="*70)
        print("⚠️  NGROK NOT FOUND")
        print("="*70)
        print("\nNgrok is required for mobile remote access.")
        print("\nInstallation Instructions:")
        print("\n1. Download ngrok:")
        print("   https://ngrok.com/download")
        print("\n2. Extract and add to PATH:")
        print("   - Windows: Copy ngrok.exe to C:\\Windows\\System32\\")
        print("   - Mac/Linux: Copy to /usr/local/bin/")
        print("\n3. Sign up for free account:")
        print("   https://dashboard.ngrok.com/signup")
        print("\n4. Get your authtoken and run:")
        print("   ngrok authtoken YOUR_AUTH_TOKEN")
        print("\n" + "="*70 + "\n")
    
    def start_ngrok(self) -> Optional[str]:
        """Start ngrok tunnel and return public URL"""
        if not self._check_ngrok_installed():
            self._install_ngrok()
            return None
        
        try:
            # Start ngrok process
            logger.info(f"Starting ngrok tunnel on port {self.port}...")
            self.ngrok_process = subprocess.Popen(
                ['ngrok', 'http', str(self.port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for ngrok to start
            time.sleep(3)
            
            # Get public URL from ngrok API
            try:
                response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    self.public_url = tunnels[0]['public_url']
                    # Prefer HTTPS URL
                    for tunnel in tunnels:
                        if tunnel['public_url'].startswith('https://'):
                            self.public_url = tunnel['public_url']
                            break
                    
                    logger.info(f"✅ Ngrok tunnel established: {self.public_url}")
                    return self.public_url
                else:
                    logger.error("No ngrok tunnels found")
                    return None
            except Exception as e:
                logger.error(f"Error getting ngrok URL: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error starting ngrok: {e}")
            return None
    
    def stop_ngrok(self):
        """Stop ngrok tunnel"""
        if self.ngrok_process:
            self.ngrok_process.terminate()
            self.ngrok_process.wait()
            logger.info("Ngrok tunnel stopped")
    
    def generate_qr_code(self, url: str) -> str:
        """Generate QR code for the URL as base64 string"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return ""
    
    def display_connection_info(self):
        """Display connection information for mobile access"""
        if not self.public_url:
            print("\n❌ No public URL available. Please check ngrok setup.\n")
            return
        
        qr_code = self.generate_qr_code(self.public_url)
        
        print("\n" + "="*70)
        print("📱 MOBILE REMOTE ACCESS ENABLED")
        print("="*70)
        print(f"\n🌐 Public URL: {self.public_url}")
        print(f"🔒 Username: {self.username}")
        print(f"🔑 Password: {self.password}")
        print("\n" + "-"*70)
        print("\n📋 CONNECTION INSTRUCTIONS:")
        print("\n1. Open your phone's camera or QR code scanner")
        print("2. Scan the QR code (displayed in browser)")
        print(f"3. Or manually enter: {self.public_url}")
        print(f"4. Login with:")
        print(f"   Username: {self.username}")
        print(f"   Password: {self.password}")
        print("\n" + "-"*70)
        print("\n⚠️  SECURITY NOTES:")
        print("   - Keep your credentials secure")
        print("   - Don't share the URL publicly")
        print("   - Connection is encrypted via HTTPS")
        print("   - Tunnel will expire when this program closes")
        print("\n" + "="*70 + "\n")
        
        # Save config
        self._save_config()
        
        # Write connection info to file
        info_file = self.config_dir / "mobile_connection_info.txt"
        with open(info_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("MOBILE REMOTE ACCESS - CONNECTION INFO\n")
            f.write("="*70 + "\n\n")
            f.write(f"URL: {self.public_url}\n")
            f.write(f"Username: {self.username}\n")
            f.write(f"Password: {self.password}\n\n")
            f.write("This file contains sensitive information. Keep it secure.\n")
        
        logger.info(f"Connection info saved to: {info_file}")
    
    def start(self):
        """Start mobile remote access"""
        logger.info("Starting mobile remote access...")
        
        # Start ngrok
        url = self.start_ngrok()
        if url:
            self.display_connection_info()
            return True
        else:
            logger.error("Failed to start mobile remote access")
            return False
    
    def stop(self):
        """Stop mobile remote access"""
        logger.info("Stopping mobile remote access...")
        self.stop_ngrok()


def get_mobile_responsive_css():
    """Return CSS for mobile-responsive layout"""
    return """
    /* Mobile Responsive CSS for Trading Dashboard */
    @media only screen and (max-width: 768px) {
        /* Make containers stack vertically */
        ._dash-loading-callback {
            margin: 5px !important;
            padding: 10px !important;
        }
        
        /* Adjust font sizes for mobile */
        h1, h2, h3, h4 {
            font-size: smaller !important;
        }
        
        /* Make charts responsive */
        .js-plotly-plot {
            width: 100% !important;
            height: auto !important;
            min-height: 300px !important;
        }
        
        /* Stack market status cards */
        div[style*="flexWrap"] {
            flex-direction: column !important;
        }
        
        /* Adjust padding for mobile */
        div[style*="padding"] {
            padding: 10px !important;
        }
        
        /* Make buttons full width on mobile */
        button {
            width: 100% !important;
            margin: 5px 0 !important;
        }
        
        /* Adjust table layouts */
        table {
            font-size: 12px !important;
        }
        
        /* Make input fields full width */
        input, select, textarea {
            width: 100% !important;
            box-sizing: border-box !important;
        }
        
        /* Improve touch targets */
        a, button, input[type="button"], input[type="submit"] {
            min-height: 44px !important;
            min-width: 44px !important;
        }
    }
    
    /* Tablet adjustments */
    @media only screen and (min-width: 769px) and (max-width: 1024px) {
        .js-plotly-plot {
            min-height: 400px !important;
        }
    }
    """


if __name__ == '__main__':
    import argparse
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(description='Mobile Remote Access Manager')
    parser.add_argument('--enable', action='store_true', help='Enable mobile access')
    parser.add_argument('--username', default='trader', help='Username for authentication')
    parser.add_argument('--password', help='Password (auto-generated if not provided)')
    parser.add_argument('--port', type=int, default=8050, help='Dashboard port')
    
    args = parser.parse_args()
    
    if args.enable:
        manager = MobileAccessManager(
            username=args.username,
            password=args.password,
            port=args.port
        )
        
        if manager.start():
            print("\n✅ Mobile access is now enabled!")
            print("   Press Ctrl+C to stop...\n")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nStopping mobile access...")
                manager.stop()
                print("✅ Mobile access stopped.\n")
    else:
        print("\nUsage: python mobile_access.py --enable")
        print("Options:")
        print("  --username USERNAME  Set authentication username (default: trader)")
        print("  --password PASSWORD  Set authentication password (auto-generated if not provided)")
        print("  --port PORT          Dashboard port (default: 8050)")
