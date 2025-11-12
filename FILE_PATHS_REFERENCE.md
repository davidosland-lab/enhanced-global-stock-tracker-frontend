# File Paths Reference - FinBERT Integration

**System Root**: `/home/user/webapp`  
**Date**: 2025-11-07  
**Branch**: `finbert-v4.0-development`

---

## 📦 **Deployment Package Paths**

### **Complete Paths with Sizes**

```
/home/user/webapp/OvernightScreener_WITH_FinBERT_v4.4.4_Win11_20251107_050703.zip
Size: 328K
Description: Complete system (RECOMMENDED)
```

```
/home/user/webapp/OvernightScreener_FinBERT_Integrated_Win11_20251107_050703.zip
Size: 104K
Description: Screener only (for updates)
```

```
/home/user/webapp/FinBERT_v4.4.4_INTEGRATED_WITH_SCREENER_20251107_050703.zip
Size: 245K
Description: FinBERT only (standalone)
```

---

## 📖 **Documentation Paths**

### **Integration Documentation**

```
/home/user/webapp/INTEGRATION_PLAN_FINBERT_TO_SCREENER.md
Description: Complete integration architecture and plan (800+ lines)
Contents: Architecture, components, code examples, validation
```

```
/home/user/webapp/FINBERT_INTEGRATION_COMPLETE.md
Description: Integration completion summary (547 lines)
Contents: What was built, technical details, test results, next steps
```

```
/home/user/webapp/DEPLOYMENT_COMPLETE_SUMMARY.md
Description: Final deployment summary (373 lines)
Contents: Achievements, packages, before/after comparison, metrics
```

### **Deployment Documentation**

```
/home/user/webapp/DEPLOYMENT_PACKAGES_README.md
Description: Installation guide for all packages (350+ lines)
Contents: Installation steps, configuration, testing, troubleshooting
```

### **Rollback Documentation**

```
/home/user/webapp/FINBERT_V4.4.4_ROLLBACK_GUIDE.md
Description: Complete rollback procedures (300+ lines)
Contents: 3 rollback methods, verification, troubleshooting
```

```
/home/user/webapp/ROLLBACK_TO_FINBERT_V4.4.4.bat
Description: Automated Windows rollback script
```

### **Phase 3 Documentation**

```
/home/user/webapp/PHASE_3_COMPLETE_SUMMARY.md
Description: Phase 3 features summary
Contents: Email notifications, LSTM training, deployment
```

---

## 💻 **Integration Source Code Paths**

### **Bridge Module (NEW)**

```
/home/user/webapp/models/screening/finbert_bridge.py
Size: 545 lines
Description: Adapter connecting screener to FinBERT v4.4.4
Key Classes: FinBERTBridge
Key Functions: get_lstm_prediction(), get_sentiment_analysis()
```

### **Updated Batch Predictor**

```
/home/user/webapp/models/screening/batch_predictor.py
Size: 558 lines (modified)
Description: Batch prediction engine with FinBERT integration
Key Changes: _lstm_prediction(), _sentiment_prediction()
```

### **Updated Configuration**

```
/home/user/webapp/models/config/screening_config.json
Description: Screening configuration with finbert_integration section
Key Sections: finbert_integration, email_notifications, lstm_training
```

### **Integration Test Suite (NEW)**

```
/home/user/webapp/scripts/screening/test_finbert_integration.py
Size: 410 lines
Description: Comprehensive integration tests
Tests: Bridge availability, LSTM, sentiment, batch predictor, validation
```

---

## 🤖 **FinBERT v4.4.4 Paths**

### **FinBERT Root Directory**

```
/home/user/webapp/finbert_v4.4.4/
Size: 1.2M
Description: Complete FinBERT v4.4.4 application (UNCHANGED)
Status: Read-only access via bridge
```

### **Key FinBERT Files**

```
/home/user/webapp/finbert_v4.4.4/app_finbert_v4_dev.py
Description: FinBERT main application (Streamlit UI)
```

```
/home/user/webapp/finbert_v4.4.4/models/lstm_predictor.py
Size: 22.5 KB
Description: Real LSTM neural network predictor
Architecture: 3-layer LSTM (128→64→32 neurons)
```

```
/home/user/webapp/finbert_v4.4.4/models/finbert_sentiment.py
Size: 11.5 KB
Description: FinBERT transformer sentiment analyzer
Model: ProsusAI/finbert
```

```
/home/user/webapp/finbert_v4.4.4/models/news_sentiment_real.py
Size: 29.2 KB
Description: Real news scraping from Yahoo Finance + Finviz
```

```
/home/user/webapp/finbert_v4.4.4/models/prediction_manager.py
Size: 17.8 KB
Description: FinBERT prediction management
```

### **FinBERT Model Storage**

```
/home/user/webapp/finbert_v4.4.4/models/trained/
Description: Directory for trained LSTM .h5 or .keras model files
Note: Models need to be trained after installation
```

---

## 📂 **Screening System Paths**

### **Screening Modules**

```
/home/user/webapp/models/screening/overnight_pipeline.py
Description: Main overnight screening orchestrator
Phases: 7 phases including email notifications
```

```
/home/user/webapp/models/screening/spi_monitor.py
Description: SPI 200 futures monitoring
```

```
/home/user/webapp/models/screening/stock_scanner.py
Description: ASX stock scanner and validator
```

```
/home/user/webapp/models/screening/send_notification.py
Description: Email notification system (Phase 3 Part 3)
```

```
/home/user/webapp/models/screening/lstm_trainer.py
Description: LSTM training automation (Phase 3 Part 4)
```

### **Windows Batch Scripts**

```
/home/user/webapp/RUN_OVERNIGHT_SCREENING.bat
Description: Run overnight screening pipeline
```

```
/home/user/webapp/RUN_LSTM_TRAINING.bat
Description: Run LSTM training for priority stocks
```

```
/home/user/webapp/CHECK_MODEL_STATUS.bat
Description: Check LSTM model staleness
```

### **Test Scripts**

```
/home/user/webapp/scripts/screening/test_finbert_integration.py
Description: Integration test suite (NEW)
```

```
/home/user/webapp/scripts/screening/test_email_notifications.py
Description: Email notification tests
```

```
/home/user/webapp/scripts/screening/test_lstm_trainer.py
Description: LSTM trainer tests
```

```
/home/user/webapp/scripts/screening/test_full_pipeline.py
Description: Full pipeline tests
```

---

## 🔧 **Configuration File Paths**

### **Main Configuration**

```
/home/user/webapp/models/config/screening_config.json
Description: Main screening configuration
Key Sections:
  - schedule: Overnight timing
  - screening: Stock selection and weights
  - lstm_training: Training automation
  - spi_monitoring: SPI futures tracking
  - finbert_integration: FinBERT integration (NEW)
  - email_notifications: Email settings
  - performance: Parallel processing
```

---

## 📊 **Reports and Logs**

### **Report Directories**

```
/home/user/webapp/reports/screening_results/
Description: Overnight screening reports (HTML)
```

```
/home/user/webapp/models/screening/reports/
Description: Alternative report location
```

### **Log Directories**

```
/home/user/webapp/logs/screening/
Description: Screening system logs
```

```
/home/user/webapp/finbert_v4.4.4/logs/
Description: FinBERT system logs
```

---

## 🗄️ **Data and Cache**

### **Cache Files**

```
/home/user/webapp/news_sentiment_cache.db
Description: SQLite cache for sentiment analysis
Cache Duration: 15 minutes
```

### **Model Training Logs**

```
/home/user/webapp/models/screening/training_logs/
Description: LSTM training logs (JSONL format)
```

---

## 🔐 **Backup and Rollback**

### **Backup Directory**

```
/home/user/webapp/backup/finbert_v4.4.4/
Description: Local backup of FinBERT v4.4.4 ZIP
File: FinBERT_v4.4.4_MARKERS_VISIBLE_20251106_204028.zip
```

### **Git References**

```
Git Tag: finbert-v4.4.4-rollback-point
Branch: finbert-v4.4.4-stable-backup
Current Branch: finbert-v4.0-development
```

---

## 📝 **Requirements Files**

```
/home/user/webapp/requirements_screening.txt
Description: Python dependencies for screening system
```

```
/home/user/webapp/finbert_v4.4.4/requirements.txt
Description: Python dependencies for FinBERT v4.4.4
```

---

## 🔍 **Quick Access Commands**

### **Navigate to Root**

```bash
cd /home/user/webapp
```

### **List Deployment Packages**

```bash
cd /home/user/webapp
ls -lh *20251107_050703.zip
```

### **View Documentation**

```bash
cd /home/user/webapp
cat DEPLOYMENT_PACKAGES_README.md
cat FINBERT_INTEGRATION_COMPLETE.md
```

### **Access Integration Code**

```bash
cd /home/user/webapp
code models/screening/finbert_bridge.py  # VS Code
cat models/screening/finbert_bridge.py   # Terminal
```

### **Access FinBERT**

```bash
cd /home/user/webapp/finbert_v4.4.4
python app_finbert_v4_dev.py
```

### **Run Tests**

```bash
cd /home/user/webapp
python scripts/screening/test_finbert_integration.py
```

---

## 🌐 **GitHub Paths**

### **Repository**

```
Repository: davidosland-lab/enhanced-global-stock-tracker-frontend
Branch: finbert-v4.0-development
Pull Request: #7
```

### **GitHub URLs**

```
Repository: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend
Pull Request: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/pull/7
Raw Files: https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/tree/finbert-v4.0-development
```

---

## 📥 **Download Commands**

### **Clone Repository**

```bash
git clone https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend.git
cd enhanced-global-stock-tracker-frontend
git checkout finbert-v4.0-development
```

### **Download Specific Package**

```bash
# After cloning
cd enhanced-global-stock-tracker-frontend
cp OvernightScreener_WITH_FinBERT_v4.4.4_Win11_20251107_050703.zip ~/Downloads/
```

---

## 📋 **Path Summary Table**

| Category | Path | Size/Lines |
|----------|------|------------|
| **Deployment Packages** | | |
| Complete System | `/home/user/webapp/OvernightScreener_WITH_FinBERT_v4.4.4_Win11_20251107_050703.zip` | 328 KB |
| Screener Only | `/home/user/webapp/OvernightScreener_FinBERT_Integrated_Win11_20251107_050703.zip` | 104 KB |
| FinBERT Only | `/home/user/webapp/FinBERT_v4.4.4_INTEGRATED_WITH_SCREENER_20251107_050703.zip` | 245 KB |
| **Integration Code** | | |
| Bridge Module | `/home/user/webapp/models/screening/finbert_bridge.py` | 545 lines |
| Batch Predictor | `/home/user/webapp/models/screening/batch_predictor.py` | 558 lines |
| Test Suite | `/home/user/webapp/scripts/screening/test_finbert_integration.py` | 410 lines |
| Configuration | `/home/user/webapp/models/config/screening_config.json` | JSON |
| **FinBERT v4.4.4** | | |
| Root Directory | `/home/user/webapp/finbert_v4.4.4/` | 1.2 MB |
| LSTM Predictor | `/home/user/webapp/finbert_v4.4.4/models/lstm_predictor.py` | 22.5 KB |
| Sentiment Analyzer | `/home/user/webapp/finbert_v4.4.4/models/finbert_sentiment.py` | 11.5 KB |
| News Scraper | `/home/user/webapp/finbert_v4.4.4/models/news_sentiment_real.py` | 29.2 KB |
| **Documentation** | | |
| Integration Plan | `/home/user/webapp/INTEGRATION_PLAN_FINBERT_TO_SCREENER.md` | 800+ lines |
| Integration Complete | `/home/user/webapp/FINBERT_INTEGRATION_COMPLETE.md` | 547 lines |
| Deployment Guide | `/home/user/webapp/DEPLOYMENT_PACKAGES_README.md` | 350+ lines |
| Deployment Summary | `/home/user/webapp/DEPLOYMENT_COMPLETE_SUMMARY.md` | 373 lines |
| Rollback Guide | `/home/user/webapp/FINBERT_V4.4.4_ROLLBACK_GUIDE.md` | 300+ lines |

---

## ✅ **Verification**

### **Check All Paths Exist**

```bash
cd /home/user/webapp

# Check deployment packages
ls -lh *20251107_050703.zip

# Check integration code
ls -lh models/screening/finbert_bridge.py
ls -lh models/screening/batch_predictor.py

# Check FinBERT directory
ls -lh finbert_v4.4.4/

# Check documentation
ls -lh INTEGRATION_PLAN_FINBERT_TO_SCREENER.md
ls -lh FINBERT_INTEGRATION_COMPLETE.md
ls -lh DEPLOYMENT_PACKAGES_README.md
```

### **Verify File Contents**

```bash
# Check file sizes
du -h *20251107_050703.zip

# Count lines in key files
wc -l models/screening/finbert_bridge.py
wc -l scripts/screening/test_finbert_integration.py
wc -l FINBERT_INTEGRATION_COMPLETE.md
```

---

**System Root**: `/home/user/webapp`  
**Total Files**: 3 deployment packages + 6 documentation files + 4 integration files  
**Total Size**: 680 KB (packages) + 1.2 MB (FinBERT) + 2,500+ lines (code/docs)  
**Status**: ✅ All files present and accessible
