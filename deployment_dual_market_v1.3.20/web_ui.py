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
REPORTS_PATH = BASE_PATH / 'reports'
TIMEZONE = pytz.timezone('Australia/Sydney')

# Market configurations
MARKETS = {
    'asx': {
        'name': 'ASX (Australian)',
        'timezone': 'Australia/Sydney',
        'reports_path': REPORTS_PATH,
        'logs_path': BASE_PATH / 'logs' / 'screening'
    },
    'us': {
        'name': 'US (S&P 500)',
        'timezone': 'America/New_York',
        'reports_path': REPORTS_PATH / 'us',
        'logs_path': BASE_PATH / 'logs' / 'screening' / 'us'
    }
}

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
    
    # Get latest reports for both markets
    latest_report_asx = get_latest_report('asx')
    latest_report_us = get_latest_report('us')
    
    # Get pipeline states for both markets
    latest_state_asx = get_latest_pipeline_state('asx')
    latest_state_us = get_latest_pipeline_state('us')
    
    status = {
        'system_active': True,
        'scanner_available': SCANNER_AVAILABLE,
        'email_enabled': config.get('email_notifications', {}).get('enabled', False),
        'lstm_training_enabled': config.get('lstm_training', {}).get('enabled', False),
        'spi_monitoring_enabled': config.get('spi_monitoring', {}).get('enabled', False),
        'markets': {
            'asx': {
                'latest_report': latest_report_asx,
                'latest_state': latest_state_asx
            },
            'us': {
                'latest_report': latest_report_us,
                'latest_state': latest_state_us
            }
        },
        'current_time': datetime.now(TIMEZONE).isoformat(),
        'timezone': str(TIMEZONE)
    }
    
    return jsonify(status)

def get_latest_pipeline_state(market='asx'):
    """Get latest pipeline state for a specific market"""
    market_info = MARKETS.get(market, MARKETS['asx'])
    
    state_locations = [
        market_info['reports_path'] / 'pipeline_state',
        BASE_PATH / 'reports' / 'pipeline_state',
    ]
    
    if market == 'us':
        state_locations.append(BASE_PATH / 'reports' / 'pipeline_state' / 'us')
    
    for state_dir in state_locations:
        if state_dir.exists():
            state_files = sorted(state_dir.glob('*.json'), reverse=True)
            if state_files:
                try:
                    with open(state_files[0], 'r') as f:
                        return json.load(f)
                except:
                    pass
    return None

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
    """Get list of available reports for both markets"""
    market = request.args.get('market', 'all')  # 'asx', 'us', or 'all'
    
    reports = {
        'asx': [],
        'us': []
    }
    
    # Get ASX reports if requested
    if market in ['asx', 'all']:
        reports['asx'] = get_market_reports('asx')
    
    # Get US reports if requested
    if market in ['us', 'all']:
        reports['us'] = get_market_reports('us')
    
    if market == 'all':
        return jsonify(reports)
    else:
        return jsonify(reports.get(market, []))

def get_market_reports(market='asx'):
    """Get reports for a specific market"""
    reports = []
    market_info = MARKETS.get(market, MARKETS['asx'])
    
    report_locations = [
        market_info['reports_path'] / 'html',
        market_info['reports_path'] / 'morning_reports',
        BASE_PATH / 'reports' / 'html' / (market if market == 'us' else ''),
    ]
    
    for html_dir in report_locations:
        if html_dir.exists():
            for report_file in sorted(html_dir.glob('*.html'), reverse=True):
                if not any(r['filename'] == report_file.name for r in reports):
                    tz = pytz.timezone(market_info['timezone'])
                    reports.append({
                        'filename': report_file.name,
                        'market': market.upper(),
                        'date': report_file.stem.split('_')[0] if '_' in report_file.stem else report_file.stem,
                        'size': report_file.stat().st_size,
                        'modified': datetime.fromtimestamp(report_file.stat().st_mtime, tz=tz).isoformat()
                    })
    
    return reports[:50]  # Limit to 50 most recent

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

def get_latest_report(market='asx'):
    """Get latest report information for a specific market"""
    market_info = MARKETS.get(market, MARKETS['asx'])
    tz = pytz.timezone(market_info['timezone'])
    
    report_locations = [
        market_info['reports_path'] / 'html',
        market_info['reports_path'] / 'morning_reports',
        BASE_PATH / 'reports' / 'html' / (market if market == 'us' else ''),
    ]
    
    all_reports = []
    for html_dir in report_locations:
        if html_dir.exists():
            all_reports.extend(html_dir.glob('*.html'))
    
    if all_reports:
        latest = max(all_reports, key=lambda p: p.stat().st_mtime)
        return {
            'filename': latest.name,
            'market': market.upper(),
            'date': latest.stem.split('_')[0] if '_' in latest.stem else latest.stem,
            'size': latest.stat().st_size,
            'modified': datetime.fromtimestamp(latest.stat().st_mtime, tz=tz).isoformat()
        }
    return None

@app.route('/api/markets')
def get_markets():
    """Get available markets configuration"""
    markets_info = {}
    for market_id, market_data in MARKETS.items():
        markets_info[market_id] = {
            'name': market_data['name'],
            'timezone': market_data['timezone']
        }
    return jsonify(markets_info)

@app.route('/api/sectors')
def get_sectors():
    """Get sectors configuration for both markets"""
    market = request.args.get('market', 'all')  # 'asx', 'us', or 'all'
    
    try:
        sectors_data = {}
        
        if market in ['asx', 'all']:
            asx_path = BASE_PATH / 'models' / 'config' / 'asx_sectors.json'
            if asx_path.exists():
                with open(asx_path, 'r') as f:
                    sectors_data['asx'] = json.load(f)
        
        if market in ['us', 'all']:
            us_path = BASE_PATH / 'models' / 'config' / 'us_sectors.json'
            if us_path.exists():
                with open(us_path, 'r') as f:
                    sectors_data['us'] = json.load(f)
        
        if market == 'all':
            return jsonify(sectors_data)
        else:
            return jsonify(sectors_data.get(market, {}))
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
    """Get recent log entries for both markets"""
    market = request.args.get('market', 'all')  # 'asx', 'us', or 'all'
    
    try:
        logs_data = {}
        
        if market in ['asx', 'all']:
            logs_data['asx'] = get_market_logs('asx')
        
        if market in ['us', 'all']:
            logs_data['us'] = get_market_logs('us')
        
        if market == 'all':
            return jsonify(logs_data)
        else:
            return jsonify(logs_data.get(market, {'logs': [], 'total_lines': 0}))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_market_logs(market='asx'):
    """Get logs for a specific market"""
    market_info = MARKETS.get(market, MARKETS['asx'])
    
    log_file_names = [
        'overnight_pipeline.log',
        f'{market}_overnight_pipeline.log',
        'us_overnight_pipeline.log' if market == 'us' else 'overnight_pipeline.log'
    ]
    
    log_paths = [market_info['logs_path'] / fname for fname in log_file_names]
    log_paths.append(BASE_PATH / 'overnight_pipeline.log')
    
    all_lines = []
    for log_file in log_paths:
        if log_file.exists() and log_file.stat().st_size > 0:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    all_lines.extend(lines)
            except:
                pass
    
    if all_lines:
        return {
            'logs': all_lines[-200:],
            'total_lines': len(all_lines),
            'market': market.upper()
        }
    else:
        return {
            'logs': [f'No log files found for {market.upper()} market. Run the pipeline to generate logs.\n'],
            'total_lines': 0,
            'market': market.upper()
        }

@app.route('/api/regime')
def get_regime():
    """Get market regime data from latest pipeline state or JSON data"""
    try:
        # Try to get regime data from latest JSON report data
        report_locations = [
            REPORTS_PATH / 'morning_reports',
            REPORTS_PATH / 'html',
            BASE_PATH / 'reports' / 'html',
            BASE_PATH / 'reports'
        ]
        
        # Find the latest JSON data file
        all_json_files = []
        for report_dir in report_locations:
            if report_dir.exists():
                all_json_files.extend(report_dir.glob('*_data.json'))
        
        if all_json_files:
            # Get the most recent JSON file
            latest_json = max(all_json_files, key=lambda p: p.stat().st_mtime)
            try:
                with open(latest_json, 'r') as f:
                    data = json.load(f)
                    event_risk_data = data.get('event_risk_data', {})
                    if event_risk_data and 'market_regime' in event_risk_data:
                        regime = event_risk_data['market_regime']
                        return jsonify({
                            'available': True,
                            'regime': regime,
                            'source': 'report_data',
                            'timestamp': data.get('generated_at', 'unknown')
                        })
            except:
                pass
        
        # If not found in JSON, try pipeline state files
        state_locations = [
            REPORTS_PATH / 'pipeline_state',
            BASE_PATH / 'reports' / 'pipeline_state',
            BASE_PATH / 'models' / 'screening' / 'reports' / 'pipeline_state'
        ]
        
        for state_dir in state_locations:
            if state_dir.exists():
                state_files = sorted(state_dir.glob('*.json'), reverse=True)
                if state_files:
                    try:
                        with open(state_files[0], 'r') as f:
                            state = json.load(f)
                            event_risk_data = state.get('event_risk_data', {})
                            if event_risk_data and 'market_regime' in event_risk_data:
                                regime = event_risk_data['market_regime']
                                return jsonify({
                                    'available': True,
                                    'regime': regime,
                                    'source': 'pipeline_state',
                                    'timestamp': state.get('timestamp', 'unknown')
                                })
                    except:
                        pass
        
        # No regime data found
        return jsonify({
            'available': False,
            'message': 'No market regime data available. Run the pipeline to generate regime analysis.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("Event Risk Guard - Dual Market Web UI")
    print("=" * 80)
    print(f"Markets: ASX (Australian) + US (S&P 500)")
    print(f"Starting web server...")
    print(f"Access dashboard at: http://localhost:5000")
    print("=" * 80)
    
    # Disable .env file loading to avoid encoding issues
    os.environ['FLASK_SKIP_DOTENV'] = '1'
    app.run(host='0.0.0.0', port=5000, debug=True)
