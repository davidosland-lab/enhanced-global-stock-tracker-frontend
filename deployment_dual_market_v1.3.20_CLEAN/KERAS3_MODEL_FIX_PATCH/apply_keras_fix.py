"""
Apply Keras 3 Model Saving Fix
Automatically patches lstm_predictor.py to add save_format='h5' parameter
"""

import sys
from pathlib import Path
import re

print("Applying Keras 3 fix to lstm_predictor.py...")

# Target file
lstm_file = Path("finbert_v4.4.4/models/lstm_predictor.py")

if not lstm_file.exists():
    print(f"ERROR: File not found: {lstm_file}")
    sys.exit(1)

# Read the file
try:
    content = lstm_file.read_text(encoding='utf-8')
except Exception as e:
    try:
        content = lstm_file.read_text(encoding='latin-1')
    except Exception as e2:
        print(f"ERROR: Cannot read file: {e2}")
        sys.exit(1)

# Check if already patched
if "save_format='h5'" in content or 'save_format="h5"' in content:
    print("[OK] Fix already applied!")
    sys.exit(0)

# Find and replace the save_model function
old_save_function = '''    def save_model(self):
        """Save model and scaler to disk"""
        if self.model and self.is_trained:
            try:
                # Save model
                self.model.save(self.model_path)
                
                # Save scaler
                with open(self.scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
                
                logger.info(f"Model saved to {self.model_path}")
                return True
            except Exception as e:
                logger.error(f"Error saving model: {e}")
                return False
        return False'''

new_save_function = '''    def save_model(self):
        """Save model and scaler to disk"""
        if self.model and self.is_trained:
            try:
                # Save model with Keras 3 compatibility
                # Keras 3.x requires explicit save_format='h5' for .h5 files
                try:
                    # Try Keras 3 save format first
                    self.model.save(self.model_path, save_format='h5')
                    logger.info(f"Model saved to {self.model_path} (Keras 3 format)")
                except Exception as keras_error:
                    # Fallback for older Keras 2.x
                    logger.warning(f"Keras 3 save failed, trying legacy format: {keras_error}")
                    self.model.save(self.model_path)
                    logger.info(f"Model saved to {self.model_path} (legacy format)")
                
                # Save scaler
                with open(self.scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
                
                return True
            except Exception as e:
                logger.error(f"Error saving model: {e}")
                import traceback
                logger.error(traceback.format_exc())
                return False
        return False'''

# Apply the fix
if old_save_function in content:
    content = content.replace(old_save_function, new_save_function)
    print("[OK] Found and replaced save_model() function")
else:
    # Try a more flexible pattern match
    print("[INFO] Exact match not found, trying pattern-based replacement...")
    
    # Pattern to find the save_model function and the specific line
    pattern = r'(def save_model\(self\):.*?# Save model\s+)self\.model\.save\(self\.model_path\)'
    
    replacement = r'\1try:\n                    # Try Keras 3 save format first\n                    self.model.save(self.model_path, save_format=\'h5\')\n                    logger.info(f"Model saved to {self.model_path} (Keras 3 format)")\n                except Exception as keras_error:\n                    # Fallback for older Keras 2.x\n                    logger.warning(f"Keras 3 save failed, trying legacy format: {keras_error}")\n                    self.model.save(self.model_path)\n                    logger.info(f"Model saved to {self.model_path} (legacy format)")'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content != content:
        content = new_content
        print("[OK] Applied pattern-based fix")
    else:
        # Last resort: simple line replacement
        print("[INFO] Pattern match failed, trying simple line replacement...")
        
        if 'self.model.save(self.model_path)' in content:
            # Find the line and replace just that line
            lines = content.split('\n')
            modified = False
            
            for i, line in enumerate(lines):
                if 'self.model.save(self.model_path)' in line and 'save_format' not in line:
                    # Get the indentation
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent
                    
                    # Replace with Keras 3 compatible version
                    lines[i] = f"{indent_str}# Keras 3 compatibility: requires save_format='h5' for .h5 files"
                    lines.insert(i + 1, f"{indent_str}try:")
                    lines.insert(i + 2, f"{indent_str}    self.model.save(self.model_path, save_format='h5')")
                    lines.insert(i + 3, f"{indent_str}    logger.info(f\"Model saved to {{self.model_path}} (Keras 3 format)\")")
                    lines.insert(i + 4, f"{indent_str}except Exception as keras_error:")
                    lines.insert(i + 5, f"{indent_str}    logger.warning(f\"Keras 3 save failed: {{keras_error}}\")")
                    lines.insert(i + 6, f"{indent_str}    self.model.save(self.model_path)")
                    lines.insert(i + 7, f"{indent_str}    logger.info(f\"Model saved to {{self.model_path}} (legacy)\")")
                    modified = True
                    break
            
            if modified:
                content = '\n'.join(lines)
                print("[OK] Applied simple line replacement")
            else:
                print("[ERROR] Could not find line to replace!")
                print("\nPlease apply manual fix:")
                print("1. Open: finbert_v4.4.4/models/lstm_predictor.py")
                print("2. Find line: self.model.save(self.model_path)")
                print("3. Replace with: self.model.save(self.model_path, save_format='h5')")
                sys.exit(1)

# Write the modified content
try:
    lstm_file.write_text(content, encoding='utf-8')
    print(f"[OK] File updated: {lstm_file}")
except Exception as e:
    try:
        lstm_file.write_text(content, encoding='utf-8', errors='ignore')
        print(f"[OK] File updated with error handling: {lstm_file}")
    except Exception as e2:
        print(f"[ERROR] Cannot write file: {e2}")
        sys.exit(1)

print("\n" + "="*70)
print("FIX APPLIED SUCCESSFULLY!")
print("="*70)
print("\nChanges made:")
print("  - Added save_format='h5' parameter to model.save()")
print("  - Added Keras 3 compatibility check")
print("  - Added fallback for Keras 2.x")
print("  - Added detailed error logging")
print("\nFile modified: finbert_v4.4.4/models/lstm_predictor.py")
print("="*70)
