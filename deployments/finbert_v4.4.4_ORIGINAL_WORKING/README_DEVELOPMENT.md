# FinBERT v4.0 - Development Version

## 🚧 Development Branch

This is the active development branch for FinBERT v4.0. All experimental features and improvements should be made here without affecting the stable v3.3 release.

## 📍 Version Information

- **Current Version**: 4.0-DEVELOPMENT
- **Base Version**: 3.3 CLEAN (Stable)
- **Branch**: `finbert-v4.0-development`
- **Status**: Active Development

## 🎯 Development Roadmap

### Phase 1: Core Improvements (Current)
- [ ] Implement real FinBERT model for sentiment analysis
- [ ] Add LSTM model for time series prediction
- [ ] Integrate XGBoost for improved accuracy
- [ ] Add database support (SQLite/PostgreSQL)

### Phase 2: Data Sources
- [ ] Multiple news API integrations
- [ ] Social media sentiment (Twitter/Reddit)
- [ ] Economic indicators API
- [ ] Options flow data

### Phase 3: UI/UX Enhancements
- [ ] Dark mode theme
- [ ] Mobile responsive design
- [ ] Real-time WebSocket updates
- [ ] Interactive dashboard

### Phase 4: Advanced Features
- [ ] Portfolio management system
- [ ] Backtesting framework
- [ ] Custom alert system
- [ ] Report generation (PDF/Excel)

## 🛠️ Development Setup

### Prerequisites
```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Running Development Version
```bash
# Start with hot reload
python app_finbert_v4_dev.py --debug

# Or use the development batch file
START_DEV.bat
```

### Testing
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python test_integration.py
```

## 📁 Project Structure

```
FinBERT_v4.0_Development/
├── app_finbert_v4_dev.py       # Main development backend
├── requirements-dev.txt        # Development dependencies
├── tests/                      # Test suite
│   ├── test_ml_models.py
│   ├── test_api_endpoints.py
│   └── test_sentiment.py
├── models/                     # ML models
│   ├── lstm_predictor.py
│   ├── xgboost_model.py
│   └── finbert_wrapper.py
├── frontend/                   # Enhanced UI
│   ├── index_v4.html
│   ├── dark_theme.css
│   └── websocket_client.js
└── docs/                       # Development docs
    ├── API_v4.md
    ├── CONTRIBUTING.md
    └── CHANGELOG_v4.md
```

## 🔄 Git Workflow

### Feature Development
```bash
# Create feature branch from development
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: description of feature"

# Push to remote
git push origin feature/your-feature-name

# Create PR to finbert-v4.0-development branch
```

### Syncing with Stable
```bash
# If you need features from stable v3.3
git checkout finbert-v4.0-development
git merge finbert-v3.3-backup --no-ff
```

## ⚠️ Important Notes

### DO NOT:
- Merge directly to main branch
- Modify files in FinBERT_v3.3_ENHANCED_FINAL
- Break backward compatibility without discussion
- Deploy to production without thorough testing

### DO:
- Keep v3.3 stable version intact
- Test all changes thoroughly
- Document new features
- Update version numbers appropriately
- Create feature branches for major changes

## 🧪 Testing Guidelines

1. **Unit Tests**: All new functions must have tests
2. **Integration Tests**: Test API endpoints
3. **Performance Tests**: Ensure no degradation
4. **User Acceptance**: Manual testing required

## 📊 Current Development Status

### Completed ✅
- Project structure setup
- Development branch created
- Base v3.3 code cloned

### In Progress 🔄
- Enhanced ML models research
- Database schema design
- WebSocket implementation planning

### Planned 📅
- FinBERT model integration
- News API connections
- Dark mode UI
- Mobile responsive design

## 🤝 Contributing

1. Check existing issues and PRs
2. Create feature branch
3. Write tests for new features
4. Update documentation
5. Submit PR with description

## 📝 Change Log

### v4.0.0-alpha (In Development)
- Initial development setup
- Cloned from v3.3 stable
- Added development documentation

## 🔗 Links

- **Stable Version (v3.3)**: [FinBERT_v3.3_ENHANCED_FINAL](../FinBERT_v3.3_ENHANCED_FINAL)
- **GitHub Repo**: [enhanced-global-stock-tracker-frontend](https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend)
- **Development Branch**: [finbert-v4.0-development](https://github.com/davidosland-lab/enhanced-global-stock-tracker-frontend/tree/finbert-v4.0-development)

## 📧 Development Contact

For development discussions, create an issue with label `v4.0-dev`

---

**Remember**: This is a development version. Use v3.3 for production!