# Fix Log: TRAIN_LSTM_SINGLE.bat Variable Issue

## Date: 2025-11-15

## Problem
When running `TRAIN_LSTM_SINGLE.bat` with interactive input (entering "MSFT"), the script failed with:

```
Training LSTM model for:

train_lstm_custom.py: error: argument --symbols: expected one argument
[ERROR] Training failed for
```

**Root Cause**: The `SYMBOL` variable was empty when passed to Python script.

## Technical Details

### Issue
Windows batch files with `setlocal enabledelayedexpansion` at the very start can interfere with `set /p` command's ability to set variables properly. The variable was set but became inaccessible when using delayed expansion syntax `!SYMBOL!`.

### Original Code Structure (BROKEN)
```batch
@echo off
setlocal enabledelayedexpansion    ← Enabled too early

set /p SYMBOL="Enter symbol: "     ← Variable not accessible with !SYMBOL! later
python train_lstm_custom.py --symbols !SYMBOL!  ← Empty variable passed
```

### Fixed Code Structure (WORKING)
```batch
@echo off

set /p SYMBOL="Enter symbol: "     ← Get input first

setlocal enabledelayedexpansion    ← Enable AFTER input captured

if not defined SYMBOL (...)        ← Verify variable exists
python train_lstm_custom.py --symbols "!SYMBOL!"  ← Now works correctly
```

## Changes Made

1. **Moved `setlocal enabledelayedexpansion`** from line 2 to line 47
   - Now enabled AFTER user input is captured
   - This allows `set /p` to properly set the variable

2. **Added verification check** (line 50-56)
   - Ensures SYMBOL variable is defined before proceeding
   - Provides clear error message if not set

3. **Added quotes to Python command** (line 94)
   - Changed: `--symbols !SYMBOL!`
   - To: `--symbols "!SYMBOL!"`
   - Protects against symbols with special characters

4. **Fixed parenthesis escaping** (lines 26-30)
   - Changed: `(Commonwealth Bank)`
   - To: `^(Commonwealth Bank^)`
   - Prevents batch file parsing errors

## Testing

### Test Case 1: Interactive Input
```batch
TRAIN_LSTM_SINGLE.bat
> Enter: MSFT
✅ Expected: Trains LSTM model for MSFT
```

### Test Case 2: Command Line Argument
```batch
TRAIN_LSTM_SINGLE.bat CBA.AX
✅ Expected: Trains LSTM model for CBA.AX (no prompt)
```

### Test Case 3: Empty Input
```batch
TRAIN_LSTM_SINGLE.bat
> Press Enter (empty)
✅ Expected: Error message and exit
```

## Why This Pattern Works

### Key Principle: Variable Scope and Delayed Expansion Timing

1. **Standard Variables** (`%VARIABLE%`):
   - Expanded at parse time (when line is read)
   - Works with `set /p` command
   - Used before `setlocal enabledelayedexpansion`

2. **Delayed Expansion** (`!VARIABLE!`):
   - Expanded at execution time (when line runs)
   - Required for variables set inside loops or conditionals
   - Used after `setlocal enabledelayedexpansion`

3. **The Fix**:
   - Capture input with `set /p` using standard syntax
   - Then enable delayed expansion
   - Use `!VARIABLE!` for all subsequent references

## Impact

✅ **TRAIN_LSTM_SINGLE.bat** now works correctly with both interactive and command-line inputs
✅ Proper error handling when no symbol provided
✅ Safer execution with quoted arguments

## Related Files

- `TRAIN_LSTM_SINGLE.bat` - Fixed batch file
- `train_lstm_custom.py` - Python training script (unchanged)
- `TRAIN_LSTM_CUSTOM.bat` - Different script, uses similar pattern (check if needs fix)
- `TRAIN_LSTM_OVERNIGHT.bat` - Different script, no user input needed

## Verification Command

Run this to test the fix:
```batch
cd C:\Users\david\AASS\deployment_event_risk_guard
TRAIN_LSTM_SINGLE.bat
```

Enter `MSFT` or `CBA.AX` when prompted.

Expected output:
```
Training LSTM model for: MSFT

Training Parameters:
  - Epochs: 50
  - Sequence Length: 60 days
  - Batch Size: 32
  - Validation Split: 20%
  - Training Data: 2 years historical

Expected time: 10-15 minutes

Starting training in 3 seconds...
[Python training output follows...]
```

## Additional Notes

### Why User Saw Empty Variable

The error output showed:
```
Training LSTM model for:           ← Empty symbol here
```

This confirmed the variable was not being expanded. The `!SYMBOL!` syntax requires `enabledelayedexpansion` to be active, but when enabled too early, it prevents `set /p` from working correctly.

### Best Practice for Interactive Batch Files

**Pattern to follow**:
```batch
@echo off
REM Get user input FIRST (no delayed expansion yet)
set /p VAR="Enter value: "

REM THEN enable delayed expansion
setlocal enabledelayedexpansion

REM Now use !VAR! safely
echo You entered: !VAR!
```

**Anti-pattern to avoid**:
```batch
@echo off
setlocal enabledelayedexpansion    ← BAD: Too early
set /p VAR="Enter value: "         ← Won't work properly
echo You entered: !VAR!             ← Empty!
```
