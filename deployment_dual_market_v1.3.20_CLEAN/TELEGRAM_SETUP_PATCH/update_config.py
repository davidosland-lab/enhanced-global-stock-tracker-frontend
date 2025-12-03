"""
Update screening_config.json and intraday_rescan_config.json with Telegram credentials
"""
import json
import sys
from pathlib import Path


def update_config_file(config_path: Path, bot_token: str, chat_id: str):
    """Update a config file with Telegram settings"""
    try:
        # Read existing config
        with config_path.open('r') as f:
            config = json.load(f)
        
        # Backup original
        backup_path = config_path.with_suffix('.json.backup')
        with backup_path.open('w') as f:
            json.dump(config, f, indent=2)
        print(f"✓ Backup created: {backup_path}")
        
        # Check which config type this is
        if 'intraday_rescan' in config:
            # This is intraday_rescan_config.json
            if 'alerts' in config and 'telegram' in config['alerts']:
                config['alerts']['telegram']['enabled'] = True
                config['alerts']['telegram']['bot_token'] = bot_token
                config['alerts']['telegram']['chat_id'] = chat_id
                print(f"✓ Updated: {config_path.name} (intraday config)")
        else:
            # This is screening_config.json
            # Add telegram_notifications section
            telegram_config = {
                "enabled": True,
                "bot_token": bot_token,
                "chat_id": chat_id,
                "parse_mode": "Markdown",
                "morning_report": {
                    "send_report": True,
                    "send_as_document": True,
                    "include_summary": True
                },
                "alerts": {
                    "enabled": True,
                    "min_alert_strength": 70.0,
                    "max_alerts_per_hour": 20,
                    "alert_types": ["breakout", "high_score", "news_sentiment"],
                    "quiet_hours": {
                        "enabled": False,
                        "start": "23:00",
                        "end": "07:00"
                    }
                },
                "notifications": {
                    "pipeline_start": True,
                    "pipeline_complete": True,
                    "pipeline_errors": True,
                    "model_training_complete": False,
                    "high_opportunity_detected": True
                }
            }
            config['telegram_notifications'] = telegram_config
            print(f"✓ Updated: {config_path.name} (screening config)")
        
        # Write updated config
        with config_path.open('w') as f:
            json.dump(config, f, indent=2)
        
        return True
        
    except Exception as e:
        print(f"✗ Error updating {config_path}: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("Usage: python update_config.py <bot_token> <chat_id>")
        sys.exit(1)
    
    bot_token = sys.argv[1]
    chat_id = sys.argv[2]
    
    print("\n" + "="*70)
    print("UPDATING CONFIGURATION FILES")
    print("="*70 + "\n")
    
    # Update screening_config.json
    screening_config = Path("models/config/screening_config.json")
    if screening_config.exists():
        update_config_file(screening_config, bot_token, chat_id)
    else:
        print(f"✗ Not found: {screening_config}")
    
    # Update intraday_rescan_config.json
    intraday_config = Path("config/intraday_rescan_config.json")
    if intraday_config.exists():
        update_config_file(intraday_config, bot_token, chat_id)
    else:
        print(f"⚠ Not found: {intraday_config} (optional)")
    
    print("\n" + "="*70)
    print("CONFIGURATION UPDATE COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
