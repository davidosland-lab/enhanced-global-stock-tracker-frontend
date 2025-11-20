"""
Event Risk Guard - Web UI
Flask-based web interface for monitoring and controlling the Event Risk Guard system
"""

import os
import sys
import json
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
import pytz
import logging

# Add models directory to path
BASE_PATH = Path(__file__).parent
sys.path.insert(0, str(BASE_PATH / 'models'))

# Import Event Risk Guard modules
try:
    from models.screening.stock_scanner import StockScanner
    from models.screening.send_notification import EmailNotifier
    SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import scanner modules: {e}")
    SCANNER_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
CONFIG_PATH = BASE_PATH / 'models' / 'config' / 'screening_config.json'
REPORTS_PATH = BASE_PATH / 'models' / 'screening' / 'reports'
TIMEZONE = pytz.timezone('Australia/Sydney')

# Load configuration
def load_config():
    """Load screening configuration"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}

def save_config(config):
    """Save screening configuration"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        return False

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/status')
def get_status():
    """Get system status"""
    config = load_config()
    
    # Get latest report
    latest_report = get_latest_report()
    
    # Get pipeline state - check multiple locations
    state_locations = [
        REPORTS_PATH / 'pipeline_state',
        BASE_PATH / 'reports' / 'pipeline_state',
        BASE_PATH / 'models' / 'screening' / 'reports' / 'pipeline_state'
    ]
    
    latest_state = None
    for state_dir in state_locations:
        if state_dir.exists():
            state_files = sorted(state_dir.glob('*.json'), reverse=True)
            if state_files:
                try:
                    with open(state_files[0], 'r') as f:
                        latest_state = json.load(f)
                        break  # Found it, stop searching
                except:
                    pass
    
    status = {
        'system_active': True,
        'scanner_available': SCANNER_AVAILABLE,
        'email_enabled': config.get('email_notifications', {}).get('enabled', False),
        'lstm_training_enabled': config.get('lstm_training', {}).get('enabled', False),
        'spi_monitoring_enabled': config.get('spi_monitoring', {}).get('enabled', False),
        'latest_report': latest_report,
        'latest_state': latest_state,
        'current_time': datetime.now(TIMEZONE).isoformat(),
        'timezone': str(TIMEZONE)
    }
    
    return jsonify(status)

@app.route('/api/config')
def get_config():
    """Get current configuration"""
    config = load_config()
    # Remove sensitive data
    if 'email_notifications' in config:
        config['email_notifications']['smtp_password'] = '********'
    return jsonify(config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    try:
        new_config = request.json
        current_config = load_config()
        
        # Merge configurations (don't overwrite password if it's masked)
        for key, value in new_config.items():
            if key == 'email_notifications' and 'smtp_password' in value:
                if value['smtp_password'] == '********':
                    # Keep existing password
                    value['smtp_password'] = current_config.get('email_notifications', {}).get('smtp_password', '')
            current_config[key] = value
        
        if save_config(current_config):
            return jsonify({'success': True, 'message': 'Configuration updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save configuration'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/reports')
def get_reports():
    """Get list of available reports"""
    reports = []
    
    # Check multiple possible report locations
    report_locations = [
        REPORTS_PATH / 'morning_reports',
        REPORTS_PATH / 'html',
        BASE_PATH / 'reports' / 'html',
        BASE_PATH / 'reports'
    ]
    
    for html_dir in report_locations:
        if html_dir.exists():
            for report_file in sorted(html_dir.glob('*.html'), reverse=True):
                # Avoid duplicates
                if not any(r['filename'] == report_file.name for r in reports):
                    reports.append({
                        'filename': report_file.name,
                        'date': report_file.stem.split('_')[0] if '_' in report_file.stem else report_file.stem,
                        'size': report_file.stat().st_size,
                        'modified': datetime.fromtimestamp(report_file.stat().st_mtime, tz=TIMEZONE).isoformat()
                    })
    
    return jsonify(reports[:50])  # Limit to 50 most recent

@app.route('/api/reports/<filename>')
def get_report(filename):
    """Get specific report"""
    # Check multiple possible locations
    report_locations = [
        REPORTS_PATH / 'morning_reports' / filename,
        REPORTS_PATH / 'html' / filename,
        BASE_PATH / 'reports' / 'html' / filename,
        BASE_PATH / 'reports' / filename
    ]
    
    for report_path in report_locations:
        if report_path.exists():
            return send_file(report_path, mimetype='text/html')
    
    return jsonify({'error': 'Report not found'}), 404

def get_latest_report():
    """Get latest report information"""
    # Check multiple possible locations
    report_locations = [
        REPORTS_PATH / 'morning_reports',
        REPORTS_PATH / 'html',
        BASE_PATH / 'reports' / 'html',
        BASE_PATH / 'reports'
    ]
    
    all_reports = []
    for html_dir in report_locations:
        if html_dir.exists():
            all_reports.extend(html_dir.glob('*.html'))
    
    if all_reports:
        # Get the most recent report
        latest = max(all_reports, key=lambda p: p.stat().st_mtime)
        return {
            'filename': latest.name,
            'date': latest.stem.split('_')[0] if '_' in latest.stem else latest.stem,
            'size': latest.stat().st_size,
            'modified': datetime.fromtimestamp(latest.stat().st_mtime, tz=TIMEZONE).isoformat()
        }
    return None

@app.route('/api/sectors')
def get_sectors():
    """Get ASX sectors configuration"""
    try:
        sectors_path = BASE_PATH / 'models' / 'config' / 'asx_sectors.json'
        with open(sectors_path, 'r') as f:
            sectors = json.load(f)
        return jsonify(sectors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Send test email"""
    try:
        notifier = EmailNotifier()
        success = notifier.send_notification(
            notification_type='success',
            subject='Test Email - Event Risk Guard Web UI',
            body='This is a test email from the Event Risk Guard web interface.'
        )
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to send test email'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/models')
def get_models():
    """Get list of trained LSTM models"""
    models = []
    
    # Search multiple possible locations for model files
    search_paths = [
        BASE_PATH / 'models' / 'lstm',      # LSTM trainer default location
        BASE_PATH / 'models',                # Direct in models folder
        BASE_PATH / 'models' / 'lstm_models' # Alternative location
    ]
    
    for models_dir in search_paths:
        if models_dir.exists():
            for model_file in sorted(models_dir.glob('*.keras'), reverse=True):
                # Avoid duplicates
                if not any(m['filename'] == model_file.name for m in models):
                    models.append({
                        'symbol': model_file.stem,
                        'filename': model_file.name,
                        'path': str(model_file.relative_to(BASE_PATH)),
                        'size': model_file.stat().st_size,
                        'modified': datetime.fromtimestamp(model_file.stat().st_mtime, tz=TIMEZONE).isoformat()
                    })
            
            # Also check for .h5 files (older Keras format)
            for model_file in sorted(models_dir.glob('*.h5'), reverse=True):
                if not any(m['filename'] == model_file.name for m in models):
                    models.append({
                        'symbol': model_file.stem,
                        'filename': model_file.name,
                        'path': str(model_file.relative_to(BASE_PATH)),
                        'size': model_file.stat().st_size,
                        'modified': datetime.fromtimestamp(model_file.stat().st_mtime, tz=TIMEZONE).isoformat()
                    })
    
    # Sort by modification time (newest first)
    models.sort(key=lambda x: x['modified'], reverse=True)
    
    return jsonify(models)

@app.route('/api/logs')
def get_logs():
    """Get recent log entries"""
    try:
        # Try multiple log file locations
        log_paths = [
            BASE_PATH / 'logs' / 'screening' / 'overnight_pipeline.log',
            BASE_PATH / 'overnight_pipeline.log',
            BASE_PATH / 'logs' / 'overnight_pipeline.log'
        ]
        
        all_lines = []
        for log_file in log_paths:
            if log_file.exists() and log_file.stat().st_size > 0:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    all_lines.extend(lines)
        
        if all_lines:
            # Return last 200 lines (increased from 100)
            return jsonify({
                'logs': all_lines[-200:],
                'total_lines': len(all_lines)
            })
        else:
            # Check if log file exists but is empty
            for log_file in log_paths:
                if log_file.exists():
                    return jsonify({
                        'logs': [f"Log file exists but is empty: {log_file}\n"],
                        'total_lines': 0,
                        'info': 'Run the pipeline to generate logs'
                    })
            
            return jsonify({
                'logs': ['No log files found. Run the pipeline to generate logs.\n'],
                'total_lines': 0
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("Event Risk Guard - Web UI")
    print("=" * 80)
    print(f"Starting web server...")
    print(f"Access dashboard at: http://localhost:5000")
    print("=" * 80)
    
    # Disable .env file loading to avoid encoding issues
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    app.run(host='0.0.0.0', port=5000, debug=True)
