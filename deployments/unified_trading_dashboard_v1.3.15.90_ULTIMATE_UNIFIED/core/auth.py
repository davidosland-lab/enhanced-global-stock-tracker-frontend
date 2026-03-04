"""
Authentication Module for Trading Dashboard
===========================================

Provides authentication and security for remote access.

Features:
- Username/password authentication
- Session management
- Secure password hashing
- Login rate limiting
- Session timeout

Usage:
    from auth import DashAuth
    auth = DashAuth(app, username='trader', password='secret')
"""

import hashlib
import secrets
import time
import json
from pathlib import Path
from typing import Optional, Dict
from functools import wraps
import dash
from dash import html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
import logging

logger = logging.getLogger(__name__)


class DashAuth:
    """Authentication manager for Dash applications"""
    
    def __init__(self, app: dash.Dash, 
                 username: str = 'trader',
                 password: str = None,
                 session_timeout: int = 3600,
                 max_attempts: int = 5):
        """
        Initialize authentication
        
        Args:
            app: Dash application instance
            username: Authentication username
            password: Authentication password
            session_timeout: Session timeout in seconds (default 1 hour)
            max_attempts: Maximum login attempts before lockout
        """
        self.app = app
        self.username = username
        self.password_hash = self._hash_password(password) if password else None
        self.session_timeout = session_timeout
        self.max_attempts = max_attempts
        
        # Session storage
        self.sessions: Dict[str, Dict] = {}
        
        # Login attempts tracking (IP -> count, timestamp)
        self.login_attempts: Dict[str, tuple] = {}
        
        # Config storage
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        self.auth_config_file = self.config_dir / "auth_config.json"
        
        # Load or create credentials
        if not self.password_hash:
            self._load_or_create_credentials()
        
        logger.info("✅ Authentication module initialized")
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _generate_session_token(self) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    def _load_or_create_credentials(self):
        """Load existing credentials or create new ones"""
        if self.auth_config_file.exists():
            try:
                with open(self.auth_config_file, 'r') as f:
                    config = json.load(f)
                    self.username = config.get('username', self.username)
                    self.password_hash = config.get('password_hash')
                    logger.info("✅ Loaded authentication credentials")
                    return
            except Exception as e:
                logger.error(f"Error loading credentials: {e}")
        
        # Generate new password
        password = secrets.token_urlsafe(12)
        self.password_hash = self._hash_password(password)
        
        # Save credentials
        try:
            config = {
                'username': self.username,
                'password_hash': self.password_hash,
                'password_plaintext': password,  # Store for first-time setup
                'created': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.auth_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            logger.info(f"✅ Created new authentication credentials")
            logger.info(f"   Username: {self.username}")
            logger.info(f"   Password: {password}")
            logger.info(f"   Saved to: {self.auth_config_file}")
            
        except Exception as e:
            logger.error(f"Error saving credentials: {e}")
    
    def _check_rate_limit(self, ip: str) -> bool:
        """Check if IP is rate limited"""
        if ip in self.login_attempts:
            attempts, timestamp = self.login_attempts[ip]
            
            # Reset after 15 minutes
            if time.time() - timestamp > 900:
                del self.login_attempts[ip]
                return True
            
            # Check if max attempts exceeded
            if attempts >= self.max_attempts:
                return False
        
        return True
    
    def _record_login_attempt(self, ip: str, success: bool):
        """Record login attempt"""
        if success:
            # Clear attempts on success
            if ip in self.login_attempts:
                del self.login_attempts[ip]
        else:
            # Increment failed attempts
            if ip in self.login_attempts:
                attempts, _ = self.login_attempts[ip]
                self.login_attempts[ip] = (attempts + 1, time.time())
            else:
                self.login_attempts[ip] = (1, time.time())
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify username and password"""
        if username != self.username:
            return False
        
        password_hash = self._hash_password(password)
        return password_hash == self.password_hash
    
    def create_session(self, username: str) -> str:
        """Create new session and return token"""
        token = self._generate_session_token()
        self.sessions[token] = {
            'username': username,
            'created': time.time(),
            'last_access': time.time()
        }
        return token
    
    def validate_session(self, token: str) -> bool:
        """Validate session token"""
        if not token or token not in self.sessions:
            return False
        
        session = self.sessions[token]
        
        # Check timeout
        if time.time() - session['last_access'] > self.session_timeout:
            del self.sessions[token]
            return False
        
        # Update last access
        session['last_access'] = time.time()
        return True
    
    def logout(self, token: str):
        """Logout and invalidate session"""
        if token in self.sessions:
            del self.sessions[token]
    
    def get_login_layout(self):
        """Get login page layout"""
        return html.Div([
            html.Div([
                html.Div([
                    html.H1('🔐 Unified Trading Dashboard', 
                           style={'color': '#2196F3', 'marginBottom': '10px'}),
                    html.P('Secure Login Required', 
                          style={'color': '#888', 'marginBottom': '30px'}),
                    
                    html.Div([
                        html.Label('Username', 
                                  style={'color': '#fff', 'display': 'block', 'marginBottom': '5px'}),
                        dcc.Input(
                            id='login-username',
                            type='text',
                            placeholder='Enter username',
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'backgroundColor': '#2a2a2a',
                                'border': '1px solid #444',
                                'borderRadius': '4px',
                                'color': '#fff',
                                'fontSize': '14px',
                                'marginBottom': '15px'
                            }
                        ),
                    ]),
                    
                    html.Div([
                        html.Label('Password', 
                                  style={'color': '#fff', 'display': 'block', 'marginBottom': '5px'}),
                        dcc.Input(
                            id='login-password',
                            type='password',
                            placeholder='Enter password',
                            style={
                                'width': '100%',
                                'padding': '12px',
                                'backgroundColor': '#2a2a2a',
                                'border': '1px solid #444',
                                'borderRadius': '4px',
                                'color': '#fff',
                                'fontSize': '14px',
                                'marginBottom': '20px'
                            }
                        ),
                    ]),
                    
                    html.Button(
                        'Login',
                        id='login-button',
                        n_clicks=0,
                        style={
                            'width': '100%',
                            'padding': '12px',
                            'backgroundColor': '#2196F3',
                            'border': 'none',
                            'borderRadius': '4px',
                            'color': '#fff',
                            'fontSize': '16px',
                            'fontWeight': 'bold',
                            'cursor': 'pointer',
                            'marginBottom': '15px'
                        }
                    ),
                    
                    html.Div(id='login-error', style={'color': '#F44336', 'marginTop': '10px'}),
                    
                    html.Div([
                        html.P('📱 For mobile access, scan the QR code provided during setup', 
                              style={'color': '#888', 'fontSize': '12px', 'marginTop': '20px'})
                    ])
                    
                ], style={
                    'backgroundColor': '#1e1e1e',
                    'padding': '40px',
                    'borderRadius': '10px',
                    'boxShadow': '0 4px 6px rgba(0,0,0,0.3)',
                    'maxWidth': '400px',
                    'width': '100%'
                })
            ], style={
                'display': 'flex',
                'justifyContent': 'center',
                'alignItems': 'center',
                'minHeight': '100vh',
                'backgroundColor': '#121212'
            }),
            
            # Session storage
            dcc.Store(id='session-token', storage_type='session'),
            dcc.Location(id='url', refresh=False)
        ])


def require_auth(auth_manager: DashAuth):
    """Decorator to require authentication for callbacks"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get session token from dash callback context
            # This is a placeholder - actual implementation would check session
            return func(*args, **kwargs)
        return wrapper
    return decorator
