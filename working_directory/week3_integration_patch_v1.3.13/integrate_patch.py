#!/usr/bin/env python3
"""
Week 3 Integration Patch - Automatic Integration Script
Safely integrates Week 3 enhancements into your existing project

Version: v1.3.13
Date: January 6, 2026
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


class Week3Integrator:
    """Automatic integration of Week 3 patch"""
    
    def __init__(self, target_dir: str, backup: bool = True):
        self.target_dir = Path(target_dir).resolve()
        self.patch_dir = Path(__file__).parent.resolve()
        self.backup = backup
        self.backup_dir = None
        
    def validate_target(self):
        """Validate target directory"""
        print(f"🔍 Validating target directory: {self.target_dir}")
        
        if not self.target_dir.exists():
            print(f"❌ Error: Target directory does not exist: {self.target_dir}")
            return False
        
        # Check for required directories
        required_dirs = ['models']
        for dir_name in required_dirs:
            dir_path = self.target_dir / dir_name
            if not dir_path.exists():
                print(f"⚠️  Warning: {dir_name}/ directory not found")
                create = input(f"Create {dir_name}/ directory? (y/n): ")
                if create.lower() == 'y':
                    dir_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Created {dir_name}/ directory")
                else:
                    print(f"❌ Cannot proceed without {dir_name}/ directory")
                    return False
        
        print("✅ Target directory validated")
        return True
    
    def create_backup(self):
        """Create backup of existing files"""
        if not self.backup:
            return True
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.target_dir / f"backup_week3_{timestamp}"
        
        print(f"💾 Creating backup: {self.backup_dir}")
        
        try:
            # Backup regime_aware_opportunity_scorer.py if it exists
            scorer_path = self.target_dir / 'models' / 'regime_aware_opportunity_scorer.py'
            if scorer_path.exists():
                backup_models = self.backup_dir / 'models'
                backup_models.mkdir(parents=True, exist_ok=True)
                shutil.copy2(scorer_path, backup_models / 'regime_aware_opportunity_scorer.py')
                print(f"  ✅ Backed up regime_aware_opportunity_scorer.py")
            
            print(f"✅ Backup created: {self.backup_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def integrate_optimized_scorer(self):
        """Integrate optimized regime_aware_opportunity_scorer.py"""
        print("\n📊 Integrating optimized parameters...")
        
        src = self.patch_dir / 'models' / 'regime_aware_opportunity_scorer.py'
        dst = self.target_dir / 'models' / 'regime_aware_opportunity_scorer.py'
        
        if not src.exists():
            print(f"❌ Source file not found: {src}")
            return False
        
        try:
            # Check if destination exists
            if dst.exists():
                print(f"  ⚠️  Existing file will be replaced: {dst.name}")
                replace = input("  Continue? (y/n): ")
                if replace.lower() != 'y':
                    print("  ⏭️  Skipped")
                    return True
            
            shutil.copy2(src, dst)
            print(f"  ✅ Integrated: regime_aware_opportunity_scorer.py")
            print(f"     - Regime weight: 40% → 20%")
            print(f"     - Confidence threshold: NEW 30%")
            print(f"     - Adaptive weights: 5 regime-specific settings")
            return True
            
        except Exception as e:
            print(f"  ❌ Integration failed: {e}")
            return False
    
    def integrate_enhanced_backtester(self):
        """Integrate enhanced_regime_backtester.py"""
        print("\n🧪 Integrating enhanced backtester...")
        
        src = self.patch_dir / 'models' / 'enhanced_regime_backtester.py'
        dst = self.target_dir / 'models' / 'enhanced_regime_backtester.py'
        
        if not src.exists():
            print(f"❌ Source file not found: {src}")
            return False
        
        try:
            if dst.exists():
                print(f"  ⚠️  File already exists: {dst.name}")
                replace = input("  Replace? (y/n): ")
                if replace.lower() != 'y':
                    print("  ⏭️  Skipped")
                    return True
            
            shutil.copy2(src, dst)
            print(f"  ✅ Integrated: enhanced_regime_backtester.py")
            print(f"     - Transaction costs: Commission + spread + slippage")
            print(f"     - Dynamic position sizing")
            print(f"     - Risk management rules")
            return True
            
        except Exception as e:
            print(f"  ❌ Integration failed: {e}")
            return False
    
    def integrate_production_dashboard(self):
        """Integrate production dashboard"""
        print("\n🌐 Integrating production dashboard...")
        
        files = [
            ('regime_dashboard_production.py', 'regime_dashboard_production.py'),
            ('wsgi_config.py', 'wsgi_config.py')
        ]
        
        success = True
        for src_name, dst_name in files:
            src = self.patch_dir / src_name
            dst = self.target_dir / dst_name
            
            if not src.exists():
                print(f"  ❌ Source file not found: {src_name}")
                success = False
                continue
            
            try:
                if dst.exists():
                    print(f"  ⚠️  File already exists: {dst_name}")
                    replace = input("  Replace? (y/n): ")
                    if replace.lower() != 'y':
                        print("  ⏭️  Skipped")
                        continue
                
                shutil.copy2(src, dst)
                print(f"  ✅ Integrated: {dst_name}")
                
            except Exception as e:
                print(f"  ❌ Integration failed for {dst_name}: {e}")
                success = False
        
        if success:
            print(f"  📝 Note: Default credentials are admin / change_me_in_production")
            print(f"  ⚠️  CHANGE PASSWORD before production deployment!")
        
        return success
    
    def integrate_documentation(self):
        """Integrate documentation"""
        print("\n📚 Integrating documentation...")
        
        # Create docs directory if it doesn't exist
        docs_dir = self.target_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        files = [
            'PRODUCTION_DEPLOYMENT_GUIDE.md',
            'WEEK_3_COMPLETE_SUMMARY.md'
        ]
        
        success = True
        for filename in files:
            src = self.patch_dir / 'docs' / filename
            dst = docs_dir / filename
            
            if not src.exists():
                print(f"  ❌ Source file not found: {filename}")
                success = False
                continue
            
            try:
                shutil.copy2(src, dst)
                print(f"  ✅ Integrated: {filename}")
                
            except Exception as e:
                print(f"  ❌ Integration failed for {filename}: {e}")
                success = False
        
        return success
    
    def verify_integration(self):
        """Verify integration"""
        print("\n✅ Verifying integration...")
        
        checks = [
            ('models/regime_aware_opportunity_scorer.py', 'Optimized scorer'),
            ('models/enhanced_regime_backtester.py', 'Enhanced backtester'),
            ('regime_dashboard_production.py', 'Production dashboard'),
            ('wsgi_config.py', 'WSGI config'),
            ('docs/PRODUCTION_DEPLOYMENT_GUIDE.md', 'Deployment guide'),
            ('docs/WEEK_3_COMPLETE_SUMMARY.md', 'Week 3 summary')
        ]
        
        all_good = True
        for path, name in checks:
            full_path = self.target_dir / path
            if full_path.exists():
                print(f"  ✅ {name}")
            else:
                print(f"  ❌ {name} - MISSING")
                all_good = False
        
        return all_good
    
    def run(self):
        """Run integration"""
        print("=" * 80)
        print("WEEK 3 INTEGRATION PATCH v1.3.13")
        print("=" * 80)
        print()
        
        # Step 1: Validate target
        if not self.validate_target():
            print("\n❌ Integration aborted")
            return False
        
        # Step 2: Create backup
        if not self.create_backup():
            print("\n❌ Integration aborted")
            return False
        
        # Step 3: Integrate components
        success = True
        success &= self.integrate_optimized_scorer()
        success &= self.integrate_enhanced_backtester()
        success &= self.integrate_production_dashboard()
        success &= self.integrate_documentation()
        
        # Step 4: Verify
        if success:
            success &= self.verify_integration()
        
        # Summary
        print("\n" + "=" * 80)
        if success:
            print("✅ INTEGRATION COMPLETE!")
            print("=" * 80)
            print()
            print("📦 Integrated Components:")
            print("  ✅ Optimized Parameters (20% regime weight)")
            print("  ✅ Enhanced Backtesting (transaction costs)")
            print("  ✅ Production Dashboard (authenticated)")
            print("  ✅ Documentation (deployment guides)")
            print()
            if self.backup_dir:
                print(f"💾 Backup Location: {self.backup_dir}")
            print()
            print("🚀 Next Steps:")
            print("  1. Test optimized parameters:")
            print("     python -c 'from models.regime_aware_opportunity_scorer import RegimeAwareOpportunityScorer; s=RegimeAwareOpportunityScorer(); print(f\"Regime weight: {s.regime_weight}\")'")
            print()
            print("  2. Test production dashboard:")
            print("     python regime_dashboard_production.py")
            print("     Visit: http://localhost:5002")
            print()
            print("  3. Read deployment guide:")
            print("     cat docs/PRODUCTION_DEPLOYMENT_GUIDE.md")
            print()
        else:
            print("❌ INTEGRATION FAILED")
            print("=" * 80)
            print()
            if self.backup_dir:
                print(f"💾 Restore from backup: {self.backup_dir}")
            print()
        
        return success


def main():
    parser = argparse.ArgumentParser(
        description='Week 3 Integration Patch - Automatic Integration'
    )
    parser.add_argument(
        '--target',
        type=str,
        required=True,
        help='Target project directory'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip backup creation'
    )
    
    args = parser.parse_args()
    
    integrator = Week3Integrator(
        target_dir=args.target,
        backup=not args.no_backup
    )
    
    success = integrator.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
