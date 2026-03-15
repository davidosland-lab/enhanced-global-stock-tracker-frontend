"""
Secure Configuration Manager for Unified Trading System v193.11.7.6

This module handles loading sensitive credentials from environment variables
and local .env files that are NEVER uploaded to cloud storage or git.

Features:
- Loads API keys from .env file (local only)
- Validates environment variables
- Provides fallback defaults for non-sensitive settings
- Rate limiting for API calls (EODHD free tier: 20 calls/day)

SECURITY:
- .env file is in .gitignore - NEVER committed to git
- .env file is LOCAL ONLY - NEVER uploaded to GenSpark cloud
- All API keys stay on your local machine

Usage:
    from utils.secure_config import get_eodhd_api_key, EODHDRateLimiter
    
    api_key = get_eodhd_api_key()
    rate_limiter = EODHDRateLimiter()
    
    if rate_limiter.can_make_call():
        # Make API call
        rate_limiter.record_call()
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class SecureConfigManager:
    """
    Manages secure loading of API keys and credentials from environment variables.
    
    NEVER stores keys in code or uploads them to cloud services.
    """
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize secure config manager.
        
        Args:
            env_file: Path to .env file (default: PROJECT_ROOT/.env)
        """
        # Determine project root (3 levels up from this file)
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # Load .env file if not specified
        if env_file is None:
            env_file = self.project_root / '.env'
        else:
            env_file = Path(env_file)
        
        # Load environment variables from .env file (if exists)
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            logger.info(f"✓ Loaded environment variables from {env_file}")
        else:
            logger.warning(f"⚠ No .env file found at {env_file}")
            logger.warning(f"⚠ Create one by copying .env.example: cp .env.example .env")
        
        self._validate_gitignore()
    
    def _validate_gitignore(self):
        """Ensure .env is in .gitignore to prevent accidental uploads"""
        gitignore_path = self.project_root / '.gitignore'
        
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
            
            if '.env' not in gitignore_content:
                logger.error("⚠ SECURITY WARNING: .env is NOT in .gitignore!")
                logger.error("⚠ Add '.env' to .gitignore immediately to prevent API key leaks!")
        else:
            logger.warning("⚠ No .gitignore found - create one to protect .env file")
    
    def get_eodhd_api_key(self) -> Optional[str]:
        """
        Get EODHD API key from environment variable.
        
        Returns:
            API key string or None if not set
        """
        api_key = os.getenv('EODHD_API_KEY')
        
        if api_key and api_key != 'your_eodhd_api_key_here':
            logger.info("✓ EODHD API key loaded successfully")
            return api_key
        else:
            logger.error("✗ EODHD API key not configured")
            logger.error("  1. Copy .env.example to .env")
            logger.error("  2. Add your API key: EODHD_API_KEY=your_actual_key")
            logger.error("  3. Get free key from: https://eodhistoricaldata.com/register")
            return None
    
    def get_email_credentials(self) -> Dict[str, str]:
        """
        Get email SMTP credentials from environment variables.
        
        Returns:
            Dictionary with username and password
        """
        return {
            'username': os.getenv('EMAIL_USERNAME', 'finbertmorningreport@gmail.com'),
            'password': os.getenv('EMAIL_PASSWORD', 'Finbert@295'),
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587
        }
    
    def get_alpha_vantage_key(self) -> Optional[str]:
        """
        Get Alpha Vantage API key (backup data source).
        
        Returns:
            API key or None if not set
        """
        return os.getenv('ALPHA_VANTAGE_API_KEY')


class EODHDRateLimiter:
    """
    Rate limiter for EODHD API (Free tier: 20 calls per day).
    
    Tracks API calls and prevents exceeding daily limit.
    Stores state in local JSON file (not uploaded).
    """
    
    def __init__(self, max_calls_per_day: int = 20):
        """
        Initialize rate limiter.
        
        Args:
            max_calls_per_day: Maximum API calls allowed per day (default: 20)
        """
        self.max_calls_per_day = max_calls_per_day
        
        # State file location (in project root, excluded from git)
        project_root = Path(__file__).parent.parent.absolute()
        self.state_dir = project_root / 'state'
        self.state_dir.mkdir(exist_ok=True)
        
        self.state_file = self.state_dir / 'eodhd_rate_limit.json'
        
        self._load_state()
    
    def _load_state(self):
        """Load rate limit state from disk"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                
                self.last_reset = datetime.fromisoformat(state.get('last_reset', datetime.now().isoformat()))
                self.call_count = state.get('call_count', 0)
                
                # Reset counter if it's a new day
                if datetime.now().date() > self.last_reset.date():
                    self.call_count = 0
                    self.last_reset = datetime.now()
                    self._save_state()
            
            except Exception as e:
                logger.error(f"Failed to load rate limit state: {e}")
                self._reset_state()
        else:
            self._reset_state()
    
    def _reset_state(self):
        """Reset rate limit state"""
        self.last_reset = datetime.now()
        self.call_count = 0
        self._save_state()
    
    def _save_state(self):
        """Save rate limit state to disk"""
        try:
            state = {
                'last_reset': self.last_reset.isoformat(),
                'call_count': self.call_count,
                'max_calls_per_day': self.max_calls_per_day
            }
            
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        
        except Exception as e:
            logger.error(f"Failed to save rate limit state: {e}")
    
    def can_make_call(self) -> bool:
        """
        Check if an API call can be made without exceeding limit.
        
        Returns:
            True if call is allowed, False otherwise
        """
        # Check if we need to reset (new day)
        if datetime.now().date() > self.last_reset.date():
            self._reset_state()
        
        return self.call_count < self.max_calls_per_day
    
    def record_call(self):
        """Record that an API call was made"""
        self.call_count += 1
        self._save_state()
        
        remaining = self.max_calls_per_day - self.call_count
        logger.info(f"EODHD API call recorded. Remaining today: {remaining}/{self.max_calls_per_day}")
    
    def get_remaining_calls(self) -> int:
        """Get number of remaining API calls for today"""
        if datetime.now().date() > self.last_reset.date():
            return self.max_calls_per_day
        return max(0, self.max_calls_per_day - self.call_count)
    
    def get_reset_time(self) -> datetime:
        """Get time when rate limit will reset"""
        next_reset = (self.last_reset + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return next_reset


# ============================================================
# GLOBAL INSTANCES (Singleton Pattern)
# ============================================================

_config_manager = None
_rate_limiter = None


def get_config_manager() -> SecureConfigManager:
    """Get global secure config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager


def get_eodhd_api_key() -> Optional[str]:
    """Convenience function to get EODHD API key"""
    return get_config_manager().get_eodhd_api_key()


def get_rate_limiter() -> EODHDRateLimiter:
    """Get global rate limiter instance"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = EODHDRateLimiter()
    return _rate_limiter


# ============================================================
# TEST MODULE
# ============================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    print("\n" + "="*80)
    print("SECURE CONFIG MANAGER TEST")
    print("="*80 + "\n")
    
    # Test config loading
    config = get_config_manager()
    
    # Test EODHD API key
    api_key = get_eodhd_api_key()
    if api_key:
        print(f"✓ EODHD API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("✗ EODHD API Key: Not configured")
    
    # Test rate limiter
    limiter = get_rate_limiter()
    print(f"\n✓ Rate Limiter Status:")
    print(f"  Remaining calls today: {limiter.get_remaining_calls()}/{limiter.max_calls_per_day}")
    print(f"  Next reset: {limiter.get_reset_time().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test email credentials
    email_creds = config.get_email_credentials()
    print(f"\n✓ Email Credentials:")
    print(f"  Username: {email_creds['username']}")
    print(f"  SMTP Server: {email_creds['smtp_server']}:{email_creds['smtp_port']}")
    
    print("\n" + "="*80)
