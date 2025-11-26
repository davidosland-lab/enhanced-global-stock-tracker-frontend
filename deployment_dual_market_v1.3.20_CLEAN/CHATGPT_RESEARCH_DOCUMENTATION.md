# ChatGPT Research Integration Documentation

## Overview

The **ChatGPT Research Integration** adds AI-powered deep research analysis to the Dual Market Screening System. This feature uses OpenAI's ChatGPT (GPT-4o Mini) to perform comprehensive fundamental and technical analysis on top stock opportunities, generating professional research reports in markdown format.

**Version:** 1.0  
**Integration Date:** 2025-11-26  
**Markets Supported:** ASX, US  

---

## Features

### 🔬 Deep Research Analysis

ChatGPT performs comprehensive analysis on your top opportunities, covering:

1. **Company Overview**
   - Business model and core operations
   - Competitive position in sector
   - Key products/services and revenue streams

2. **Fundamental Analysis**
   - Recent financial performance
   - Key financial metrics and ratios
   - Management quality and corporate governance
   - Growth drivers and catalysts

3. **Technical Analysis Context**
   - Current price action and trend
   - Support and resistance levels
   - Volume analysis and market interest
   - Integration with pipeline technical indicators

4. **Market Context**
   - Sector trends and outlook
   - Market conditions (ASX/US specific)
   - Competitive landscape
   - Regulatory factors

5. **Risk Assessment**
   - Key risks and challenges
   - Volatility considerations
   - Downside scenarios
   - Risk mitigation strategies

6. **Investment Thesis**
   - Bull case: Why it's a good opportunity
   - Bear case: What could go wrong
   - Expected holding period
   - Price targets (if applicable)

7. **Recommendation Summary**
   - Overall recommendation (Strong Buy/Buy/Hold/Sell/Strong Sell)
   - Rationale for recommendation
   - Entry points and stop-loss suggestions
   - Position sizing considerations

### 📊 Dual Market Support

- **ASX Market:** Tailored research for Australian stocks with RBA, ASX context
- **US Market:** Tailored research for US stocks with Federal Reserve, US market context
- Independent research reports for each market
- Market-specific news sources integration

### 📄 Professional Report Generation

- **Format:** Clean, professional markdown
- **Structure:** Table of contents, individual stock sections
- **Length:** ~2000 words per stock
- **Output:** Saved to `reports/chatgpt_research/`
- **Naming:** `asx_research_YYYYMMDD.md` / `us_research_YYYYMMDD.md`

---

## Configuration

### Step 1: Set OpenAI API Key

The system requires an OpenAI API key to function. **Three easy options:**

#### **Option 1: Config File (RECOMMENDED - Easiest)**

1. Navigate to config folder:
   ```powershell
   cd deployment_dual_market_v1.3.20_CLEAN\config
   ```

2. Copy the example file:
   ```powershell
   copy .env.example api_keys.env
   ```

3. Edit `config\api_keys.env` and add your key:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

4. Save and close. Done! ✅

**The system automatically loads from this file.** No environment variables needed!

See `SETUP_OPENAI_API_KEY.md` for detailed instructions.

#### **Option 2: Environment Variable (Permanent)**

**Windows PowerShell:**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-proj-your-key', 'User')
```

**Linux/Mac:**
```bash
echo 'export OPENAI_API_KEY="sk-proj-your-key"' >> ~/.bashrc
source ~/.bashrc
```

#### **Option 3: Environment Variable (Temporary)**

**Windows PowerShell:**
```powershell
$env:OPENAI_API_KEY="sk-proj-your-api-key-here"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-proj-your-api-key-here"
```

**Note:** For complete setup instructions, see `SETUP_OPENAI_API_KEY.md`

### Step 2: Update `screening_config.json`

The research configuration is already added to `models/config/screening_config.json`:

```json
{
  "research": {
    "enabled": true,
    "model": "gpt-4o-mini",
    "max_stocks": 5,
    "output_format": "markdown",
    "output_path": "reports/chatgpt_research",
    "include_in_report": true,
    "run_after_scoring": true
  }
}
```

**Configuration Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable ChatGPT research |
| `model` | string | `"gpt-4o-mini"` | OpenAI model to use |
| `max_stocks` | integer | `5` | Maximum number of stocks to research |
| `output_format` | string | `"markdown"` | Output format (currently only markdown) |
| `output_path` | string | `"reports/chatgpt_research"` | Directory to save reports |
| `include_in_report` | boolean | `true` | Include research summary in HTML report |
| `run_after_scoring` | boolean | `true` | Run research after opportunity scoring |

---

## Usage

### Running with ChatGPT Research

**ASX Pipeline:**
```bash
cd deployment_dual_market_v1.3.20_CLEAN
python RUN_PIPELINE.bat
```

**US Pipeline:**
```bash
cd deployment_dual_market_v1.3.20_CLEAN
python RUN_US_PIPELINE.bat
```

When enabled, the research runs automatically as **Phase 4.7: ChatGPT Research** after opportunity scoring.

### Disabling ChatGPT Research

To disable research temporarily without removing the API key:

Edit `models/config/screening_config.json`:
```json
"research": {
  "enabled": false,
  ...
}
```

---

## Output Files

### Research Reports

**Location:**
- ASX: `reports/chatgpt_research/asx_research_YYYYMMDD.md`
- US: `reports/chatgpt_research/us_research_YYYYMMDD.md`

**Format:** Professional markdown with:
- Header with metadata
- Table of contents
- Individual stock sections
- Comprehensive analysis (2000 words per stock)
- Disclaimer footer

### HTML Morning Reports

The HTML morning reports now include a **ChatGPT Research Analysis** section that:
- Shows number of stocks researched
- Lists analysis components
- Provides path to full markdown report
- Displays research status and metadata

---

## Testing

### Test Script

A comprehensive test script is provided: `TEST_CHATGPT_RESEARCH.py`

**Run Tests:**
```bash
cd deployment_dual_market_v1.3.20_CLEAN
python TEST_CHATGPT_RESEARCH.py
```

**Tests Performed:**
1. ✅ OpenAI API Connection
2. ✅ Research Generation (ASX & US)
3. ✅ Markdown Export

**Expected Output:**
```
================================================================================
CHATGPT RESEARCH INTEGRATION TEST SUITE
================================================================================

TEST 1: OpenAI API Connection
✓ OPENAI_API_KEY found (51 characters)
✅ Connection test PASSED

TEST 2: Research Generation
📊 Testing ASX Research...
✅ ASX Research PASSED: 2 stocks analyzed
📊 Testing US Research...
✅ US Research PASSED: 1 stocks analyzed

TEST 3: Markdown Export
✅ ASX Markdown saved: test_reports/test_asx_research.md
✅ US Markdown saved: test_reports/test_us_research.md

================================================================================
TEST SUMMARY
================================================================================
✅ PASS: API Connection
✅ PASS: Research Generation
✅ PASS: Markdown Export
================================================================================
Results: 3/3 tests passed

🎉 ALL TESTS PASSED - ChatGPT Research is ready!
```

---

## Architecture

### Module Structure

```
deployment_dual_market_v1.3.20_CLEAN/
├── models/
│   ├── screening/
│   │   ├── chatgpt_research.py          # Core research module
│   │   ├── overnight_pipeline.py        # ASX pipeline (integrated)
│   │   ├── us_overnight_pipeline.py     # US pipeline (integrated)
│   │   └── report_generator.py          # HTML report generator (updated)
│   └── config/
│       └── screening_config.json        # Configuration (updated)
├── reports/
│   └── chatgpt_research/                # Research output directory
│       ├── asx_research_YYYYMMDD.md
│       └── us_research_YYYYMMDD.md
└── TEST_CHATGPT_RESEARCH.py            # Test script
```

### Integration Points

1. **Pipeline Initialization** (`__init__`):
   - Loads research configuration
   - Checks ChatGPT module availability
   - Logs research status

2. **Pipeline Execution** (`run_full_pipeline`):
   - Phase 4.7: Runs `_run_chatgpt_research()`
   - Passes research data to report generator

3. **Report Generation** (`_generate_report`/`_generate_us_report`):
   - Receives research data
   - Passes to `report_generator.generate_morning_report()`

4. **HTML Report** (`report_generator.py`):
   - New section: `_build_research_section()`
   - Displays research summary and markdown path

### Data Flow

```
Pipeline
  ↓
Score Opportunities (Phase 4)
  ↓
Train LSTM Models (Phase 4.5)
  ↓
ChatGPT Research (Phase 4.7) ← NEW
  ├─ Get top N opportunities
  ├─ Call run_chatgpt_research()
  ├─ Generate research for each stock
  ├─ Save markdown report
  └─ Return research_data dict
  ↓
Generate Report (Phase 5)
  ├─ Include research summary in HTML
  └─ Link to full markdown report
```

---

## Cost Considerations

### OpenAI API Pricing (GPT-4o Mini)

**Model:** `gpt-4o-mini`  
**Input:** $0.150 / 1M tokens  
**Output:** $0.600 / 1M tokens  

### Estimated Costs Per Run

**Assumptions:**
- Max stocks: 5
- Average prompt: ~800 tokens/stock
- Average response: ~2500 tokens/stock
- Total per stock: ~3300 tokens

**Cost per stock:** ~$0.0018  
**Cost per run (5 stocks):** ~$0.009  
**Monthly cost (30 runs):** ~$0.27  

**Very affordable!** 🎉

### Cost Optimization Tips

1. **Reduce `max_stocks`**: Lower to 3 stocks for ~$0.005/run
2. **Use selectively**: Enable only for important screening runs
3. **Monitor usage**: Check OpenAI dashboard regularly
4. **Set limits**: Configure OpenAI account spending limits

---

## Troubleshooting

### Issue 1: "OPENAI_API_KEY not found"

**Solution:**
```powershell
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-key-here"

# Or set permanently
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-your-key-here', 'User')
```

### Issue 2: "OpenAI SDK not installed"

**Solution:**
```bash
pip install openai
```

### Issue 3: "Connection test failed"

**Possible causes:**
- Invalid API key
- Network connectivity issues
- OpenAI API service issues

**Solution:**
1. Verify API key at https://platform.openai.com/api-keys
2. Check internet connection
3. Visit https://status.openai.com/ for service status

### Issue 4: Research not appearing in report

**Check:**
1. `research.enabled = true` in config
2. OPENAI_API_KEY is set correctly
3. Check pipeline logs for errors
4. Verify `chatgpt_research.py` module is present

### Issue 5: "Rate limit exceeded"

**Solution:**
- Wait a few minutes before retrying
- Reduce `max_stocks` in configuration
- Check OpenAI account rate limits
- Consider upgrading OpenAI tier if needed

---

## Best Practices

### 1. Strategic Use

- **Enable for major runs**: Use ChatGPT research for important screening sessions
- **Disable for tests**: Turn off during pipeline testing to save costs
- **Review regularly**: Check research quality and adjust prompts if needed

### 2. Prompt Engineering

The prompts in `chatgpt_research.py` can be customized for your needs:

```python
def build_prompt(opportunity: Dict, market: str = "ASX") -> str:
    # Customize prompt here
    prompt = f"""You are a professional stock market analyst...
    
    Add your custom instructions here...
    """
    return prompt
```

### 3. Model Selection

While `gpt-4o-mini` is recommended for cost-effectiveness, you can use other models:

```json
"research": {
  "model": "gpt-4o",          # More capable, higher cost
  "model": "gpt-4o-mini",     # Best balance (recommended)
  "model": "gpt-3.5-turbo"   # Cheaper, less detailed
}
```

### 4. Output Management

- Archive old research reports monthly
- Keep reports for historical analysis
- Cross-reference with actual stock performance
- Use for learning and strategy refinement

---

## Future Enhancements

Planned features for future versions:

1. **PDF Export**: Generate PDF reports alongside markdown
2. **Email Integration**: Send research reports via email
3. **Custom Prompts**: User-defined research focus areas
4. **Multi-language**: Support for non-English research
5. **Voice Synthesis**: Audio summaries of research reports
6. **Backtesting**: Compare research recommendations with actual performance
7. **Sentiment Scoring**: Numeric scores from research text
8. **Portfolio Integration**: Link research to portfolio positions

---

## Support

For issues, questions, or feature requests:

1. Check this documentation
2. Review test script output
3. Check pipeline logs in `logs/screening/`
4. Contact system administrator

---

## Changelog

### Version 1.0 (2025-11-26)

**Initial Release:**
- ✅ ChatGPT research module (`chatgpt_research.py`)
- ✅ Integration with ASX pipeline
- ✅ Integration with US pipeline
- ✅ Markdown report generation
- ✅ HTML report section
- ✅ Configuration support
- ✅ Test script
- ✅ Documentation

**Files Modified:**
- `models/screening/chatgpt_research.py` (NEW)
- `models/screening/overnight_pipeline.py` (UPDATED)
- `models/screening/us_overnight_pipeline.py` (UPDATED)
- `models/screening/report_generator.py` (UPDATED)
- `models/config/screening_config.json` (UPDATED)
- `TEST_CHATGPT_RESEARCH.py` (NEW)

**Benefits:**
- 🎯 Professional-grade stock research
- 📊 Comprehensive fundamental analysis
- 🔍 Risk assessment and recommendations
- 💰 Very low cost (~$0.009 per run)
- 🚀 Easy to enable/disable
- 📈 Enhanced decision-making

---

## Conclusion

The ChatGPT Research Integration provides professional-grade stock analysis at minimal cost, enhancing your overnight screening system with AI-powered insights. With comprehensive research on your top opportunities, you'll make more informed trading decisions backed by detailed fundamental and technical analysis.

**Happy Trading! 🚀📈**
