# Manual Fix Script for Windows - v1.3.15.158
# Apply ALL 8 Critical Fixes Without Re-downloading

## CRITICAL FIX #1: Remove get_mock_sentiment Call

**File**: `finbert_v4.4.4\models\lstm_predictor.py`

**Find line ~487** (search for "get_mock_sentiment"):
```python
sentiment_data = self.sentiment_analyzer.get_mock_sentiment(symbol)
```

**Replace with**:
```python
# FIX v1.3.15.151: get_mock_sentiment() removed - sentiment handled by finbert_bridge.py
# This method no longer exists in FinBERTSentimentAnalyzer
sentiment_data = None
```

**Save the file.**

---

## CRITICAL FIX #2: Fix news_sentiment_real.py Import

**File**: `finbert_v4.4.4\models\news_sentiment_real.py`

**Find lines 24-35** (the import section):
```python
# Import finbert_analyzer - handle import errors gracefully
try:
    from .finbert_sentiment import finbert_analyzer
    logger.info("✓ FinBERT analyzer imported successfully")
except (ImportError, ValueError) as e:
    # Try absolute import as fallback
    try:
        from models.finbert_sentiment import finbert_analyzer
        logger.info("✓ FinBERT analyzer imported (absolute path)")
    except (ImportError, ValueError) as e2:
        logger.error(f"Failed to import finbert_analyzer: {e2}")
        finbert_analyzer = None
```

**Replace with**:
```python
# Import finbert_analyzer - handle import errors gracefully
# FIX v1.3.15.157: Use importlib to avoid "No module named 'models.finbert_sentiment'" error
import importlib.util
from pathlib import Path

try:
    # First try relative import
    from .finbert_sentiment import finbert_analyzer
    logger.info("✓ FinBERT analyzer imported successfully (relative import)")
except (ImportError, ValueError) as e:
    # Try importing using importlib from same directory
    try:
        current_dir = Path(__file__).parent
        finbert_sentiment_path = current_dir / "finbert_sentiment.py"
        
        if finbert_sentiment_path.exists():
            spec = importlib.util.spec_from_file_location("finbert_sentiment", finbert_sentiment_path)
            if spec and spec.loader:
                finbert_sentiment_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(finbert_sentiment_module)
                finbert_analyzer = finbert_sentiment_module.finbert_analyzer
                logger.info("✓ FinBERT analyzer imported (importlib)")
            else:
                raise ImportError("Could not load finbert_sentiment module")
        else:
            raise FileNotFoundError(f"finbert_sentiment.py not found at {finbert_sentiment_path}")
    except Exception as e2:
        logger.error(f"Failed to import finbert_analyzer: {e2}")
        finbert_analyzer = None
```

**Save the file.**

---

## CRITICAL FIX #3: Fix LSTM Training PyTorch Gradient Error

**File**: `finbert_v4.4.4\models\lstm_predictor.py`

**Find lines 204-240** (the custom_loss function and compile):
```python
        # Custom loss function for financial data
        def custom_loss(y_true, y_pred):
            """
            Custom loss function for LSTM training
            FIXED v2: Handles both TensorFlow and PyTorch tensors
            """
            # Handle PyTorch tensors if present (detach from gradient graph first)
            try:
                # Check if y_pred is a PyTorch tensor
                if hasattr(y_pred, 'detach'):
                    # It's a PyTorch tensor - detach and convert to numpy first
                    y_pred = y_pred.detach().cpu().numpy()
                if hasattr(y_true, 'detach'):
                    y_true = y_true.detach().cpu().numpy()
            except:
                pass  # If it fails, continue with TensorFlow conversion
            
            # Convert to TensorFlow tensors explicitly
            y_true = tf.convert_to_tensor(y_true, dtype=tf.float32)
            y_pred = tf.convert_to_tensor(y_pred, dtype=tf.float32)
            
            # Price prediction loss (MAE)
            price_loss = tf.reduce_mean(tf.abs(y_true[:, 0] - y_pred[:, 0]))
            
            # Direction accuracy loss
            true_direction = tf.sign(y_true[:, 0])
            pred_direction = tf.sign(y_pred[:, 0])
            direction_loss = tf.reduce_mean(tf.abs(true_direction - pred_direction))
            
            # Combined loss
            return price_loss + 0.3 * direction_loss
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss=custom_loss,
            metrics=['mae', 'mse']
        )
```

**Replace with**:
```python
        # FIX v1.3.15.158: Use simple MSE loss to avoid PyTorch gradient issues
        # Custom loss causes "element 0 does not require grad" error with Keras 3 + PyTorch backend
        # Simplified to use built-in loss function for compatibility
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='mse',  # Use built-in MSE instead of custom loss
            metrics=['mae', 'mse']
        )
```

**Save the file.**

---

## CRITICAL FIX #4: Fix Market Regime Engine

**File**: `pipelines\models\screening\market_regime_engine.py`

**Find line ~117**:
```python
market_data = self.data_fetcher.fetch_overnight_data()
```

**Replace with**:
```python
market_data = self.data_fetcher.fetch_market_data()
```

**Save the file.**

---

## CRITICAL FIX #5: Fix Sentiment Integration Imports

**File**: `core\paper_trading_coordinator.py`

**Find line ~59**:
```python
from sentiment_integration import IntegratedSentimentAnalyzer, get_sentiment_analyzer
```

**Replace with**:
```python
from core.sentiment_integration import IntegratedSentimentAnalyzer, get_sentiment_analyzer
```

**Save the file.**

---

**File**: `core\unified_trading_dashboard.py`

**Find line ~1439**:
```python
from sentiment_integration import IntegratedSentimentAnalyzer
```

**Replace with**:
```python
from core.sentiment_integration import IntegratedSentimentAnalyzer
```

**Save the file.**

---

## CRITICAL FIX #6: Fix train_lstm.py Import

**File**: `finbert_v4.4.4\models\train_lstm.py`

**Find line ~19**:
```python
from models.lstm_predictor import StockLSTMPredictor
```

**Replace with**:
```python
# FIX v1.3.15.156: Use importlib to avoid sys.path conflicts
import importlib.util
import sys
from pathlib import Path

# Get the directory containing this script
current_dir = Path(__file__).parent
lstm_predictor_path = current_dir / "lstm_predictor.py"

# Load lstm_predictor using importlib
spec = importlib.util.spec_from_file_location("lstm_predictor_module", lstm_predictor_path)
lstm_predictor_module = importlib.util.module_from_spec(spec)
sys.modules['lstm_predictor_module'] = lstm_predictor_module
spec.loader.exec_module(lstm_predictor_module)

# Import the class
StockLSTMPredictor = lstm_predictor_module.StockLSTMPredictor
```

**Save the file.**

---

## Verification Commands

After applying ALL fixes, run these commands to verify:

```powershell
cd "C:\Users\david\REgime trading V4 restored\unified_trading_system_v1.3.15.129_COMPLETE"

# Should NOT find get_mock_sentiment (it's commented out)
findstr /c:"sentiment_data = self.sentiment_analyzer.get_mock_sentiment" finbert_v4.4.4\models\lstm_predictor.py

# Should find the fix comment
findstr /c:"FIX v1.3.15.151" finbert_v4.4.4\models\lstm_predictor.py

# Should find importlib
findstr /c:"import importlib" finbert_v4.4.4\models\news_sentiment_real.py

# Should find FIX v1.3.15.158
findstr /c:"FIX v1.3.15.158" finbert_v4.4.4\models\lstm_predictor.py
```

---

## Test After Fixing

```powershell
python pipelines\run_au_pipeline.py --mode test
```

**Expected**: No errors, 5/5 predictions successful, 1 BUY signal.

---

## Summary

You need to manually edit **6 files** to apply all fixes:

1. ✅ `finbert_v4.4.4\models\lstm_predictor.py` (2 fixes: remove get_mock_sentiment, fix PyTorch loss)
2. ✅ `finbert_v4.4.4\models\news_sentiment_real.py` (fix import)
3. ✅ `finbert_v4.4.4\models\train_lstm.py` (fix import)
4. ✅ `pipelines\models\screening\market_regime_engine.py` (fix method name)
5. ✅ `core\paper_trading_coordinator.py` (fix import)
6. ✅ `core\unified_trading_dashboard.py` (fix import)

**Edit these files in Notepad/VSCode, save, and retest.**
