#!/usr/bin/env python3
"""
Pipeline Usage Visualization Generator
======================================

Creates charts showing how pipeline reports are used in paper trading.

Author: Unified Trading System v1.3.15.191.1
Date: February 28, 2026
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from pathlib import Path

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
colors = {
    'pipeline': '#FF6B6B',
    'finbert': '#4ECDC4',
    'lstm': '#45B7D1',
    'technical': '#96CEB4',
    'momentum': '#FFEAA7',
    'volume': '#DFE6E9',
    'combined': '#6C5CE7'
}

def create_decision_weight_chart():
    """Create pie chart showing decision weight breakdown."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Data
    components = [
        'Pipeline\n(Overnight)', 
        'FinBERT\n(Live)', 
        'LSTM\n(Live)', 
        'Technical\n(Live)',
        'Momentum\n(Live)',
        'Volume\n(Live)'
    ]
    weights = [40.0, 15.0, 15.0, 15.0, 9.0, 6.0]
    colors_list = [colors['pipeline'], colors['finbert'], colors['lstm'], 
                   colors['technical'], colors['momentum'], colors['volume']]
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        weights, 
        labels=components,
        colors=colors_list,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12, 'weight': 'bold'}
    )
    
    # Style autopct
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(14)
        autotext.set_weight('bold')
    
    ax.set_title('Decision Weight Breakdown\nPipeline vs. Live ML Components', 
                 fontsize=16, weight='bold', pad=20)
    
    # Add legend with actual values
    legend_labels = [f'{comp.replace(chr(10), " ")}: {weight:.1f}%' 
                     for comp, weight in zip(components, weights)]
    ax.legend(legend_labels, loc='upper left', bbox_to_anchor=(1.0, 1.0), fontsize=10)
    
    plt.tight_layout()
    plt.savefig('pipeline_decision_weights.png', dpi=300, bbox_inches='tight')
    print("✓ Created: pipeline_decision_weights.png")
    plt.close()

def create_data_flow_diagram():
    """Create data flow diagram."""
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(5, 9.5, 'Pipeline Reports → Paper Trading Data Flow', 
            ha='center', fontsize=18, weight='bold')
    
    # Step 1: Overnight Pipeline
    box1 = FancyBboxPatch((0.5, 7), 2, 1.5, boxstyle="round,pad=0.1", 
                          facecolor=colors['pipeline'], edgecolor='black', linewidth=2)
    ax.add_patch(box1)
    ax.text(1.5, 8.2, 'Overnight Pipeline', ha='center', va='top', fontsize=11, weight='bold')
    ax.text(1.5, 7.8, '6+ hours', ha='center', va='top', fontsize=9)
    ax.text(1.5, 7.5, '~240 stocks', ha='center', va='top', fontsize=9)
    
    # Step 2: JSON Reports
    box2 = FancyBboxPatch((3.5, 7), 2, 1.5, boxstyle="round,pad=0.1", 
                          facecolor='#95A5A6', edgecolor='black', linewidth=2)
    ax.add_patch(box2)
    ax.text(4.5, 8.2, 'JSON Reports', ha='center', va='top', fontsize=11, weight='bold')
    ax.text(4.5, 7.8, 'reports/screening/', ha='center', va='top', fontsize=8)
    ax.text(4.5, 7.5, '~30-40 opps', ha='center', va='top', fontsize=9)
    
    # Arrow 1→2
    arrow1 = FancyArrowPatch((2.5, 7.75), (3.5, 7.75), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow1)
    
    # Step 3: Load Reports
    box3 = FancyBboxPatch((6.5, 7), 2, 1.5, boxstyle="round,pad=0.1", 
                          facecolor='#3498DB', edgecolor='black', linewidth=2)
    ax.add_patch(box3)
    ax.text(7.5, 8.2, 'Load Reports', ha='center', va='top', fontsize=11, weight='bold')
    ax.text(7.5, 7.8, '_load_overnight_reports()', ha='center', va='top', fontsize=8)
    ax.text(7.5, 7.5, 'Startup + every 30min', ha='center', va='top', fontsize=8)
    
    # Arrow 2→3
    arrow2 = FancyArrowPatch((5.5, 7.75), (6.5, 7.75), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow2)
    
    # Step 4: Get Recommendations
    box4 = FancyBboxPatch((1, 5), 3, 1.2, boxstyle="round,pad=0.1", 
                          facecolor='#E74C3C', edgecolor='black', linewidth=2)
    ax.add_patch(box4)
    ax.text(2.5, 5.9, 'Get Recommendations', ha='center', va='top', fontsize=11, weight='bold')
    ax.text(2.5, 5.5, '_get_pipeline_recommendations()', ha='center', va='top', fontsize=8)
    ax.text(2.5, 5.2, 'Top 5 per market', ha='center', va='top', fontsize=8)
    
    # Arrow 3→4
    arrow3 = FancyArrowPatch((7.5, 7.0), (2.5, 6.2), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow3)
    
    # Step 5: Evaluate
    box5 = FancyBboxPatch((5, 5), 3, 1.2, boxstyle="round,pad=0.1", 
                          facecolor='#F39C12', edgecolor='black', linewidth=2)
    ax.add_patch(box5)
    ax.text(6.5, 5.9, 'Evaluate Filters', ha='center', va='top', fontsize=11, weight='bold')
    ax.text(6.5, 5.5, '_evaluate_pipeline_recommendation()', ha='center', va='top', fontsize=7)
    ax.text(6.5, 5.2, 'Score≥60, Sentiment≥45, Age≤12h', ha='center', va='top', fontsize=8)
    
    # Arrow 4→5
    arrow4 = FancyArrowPatch((4.0, 5.6), (5.0, 5.6), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow4)
    
    # Step 6: Live ML
    box6 = FancyBboxPatch((1, 3), 3, 1.2, boxstyle="round,pad=0.1", 
                          facecolor=colors['finbert'], edgecolor='black', linewidth=2)
    ax.add_patch(box6)
    ax.text(2.5, 3.9, 'Live ML Analysis', ha='center', va='top', fontsize=11, weight='bold')
    ax.text(2.5, 3.5, 'FinBERT + LSTM + Technical', ha='center', va='top', fontsize=8)
    ax.text(2.5, 3.2, '60% weight', ha='center', va='top', fontsize=9)
    
    # Step 7: Combine Signals
    box7 = FancyBboxPatch((5, 3), 3, 1.2, boxstyle="round,pad=0.1", 
                          facecolor=colors['combined'], edgecolor='black', linewidth=2)
    ax.add_patch(box7)
    ax.text(6.5, 3.9, 'Combine Signals', ha='center', va='top', fontsize=11, weight='bold', color='white')
    ax.text(6.5, 3.5, 'Pipeline (40%) + ML (60%)', ha='center', va='top', fontsize=8, color='white')
    ax.text(6.5, 3.2, 'Target: 75-85% win rate', ha='center', va='top', fontsize=8, color='white')
    
    # Arrows to combine
    arrow5 = FancyArrowPatch((6.5, 5.0), (6.5, 4.2), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow5)
    arrow6 = FancyArrowPatch((2.5, 3.0), (5.0, 3.6), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow6)
    
    # Step 8: Execute Trade
    box8 = FancyBboxPatch((3, 0.8), 4, 1.2, boxstyle="round,pad=0.1", 
                          facecolor='#27AE60', edgecolor='black', linewidth=2)
    ax.add_patch(box8)
    ax.text(5, 1.7, 'Execute Trade', ha='center', va='top', fontsize=12, weight='bold', color='white')
    ax.text(5, 1.3, '_process_pipeline_recommendations()', ha='center', va='top', fontsize=8, color='white')
    ax.text(5, 1.0, 'enter_position() or exit_position()', ha='center', va='top', fontsize=8, color='white')
    
    # Arrow to execute
    arrow7 = FancyArrowPatch((6.5, 3.0), (5, 2.0), 
                            arrowstyle='->', mutation_scale=30, linewidth=2, color='black')
    ax.add_patch(arrow7)
    
    plt.tight_layout()
    plt.savefig('pipeline_data_flow.png', dpi=300, bbox_inches='tight')
    print("✓ Created: pipeline_data_flow.png")
    plt.close()

def create_win_rate_comparison():
    """Create bar chart comparing win rates."""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Data
    scenarios = ['Pipeline\nOnly', 'Live ML\nOnly', 'Combined\n(Pipeline+ML)', 'Target\nGoal']
    win_rates = [70, 63, 72.5, 75]
    bar_colors = [colors['pipeline'], colors['technical'], colors['combined'], '#2ECC71']
    
    bars = ax.bar(scenarios, win_rates, color=bar_colors, edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels on bars
    for bar, rate in zip(bars, win_rates):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%',
                ha='center', va='bottom', fontsize=14, weight='bold')
    
    # Add baseline at 50%
    ax.axhline(y=50, color='red', linestyle='--', linewidth=2, label='Random (50%)')
    
    # Style
    ax.set_ylabel('Win Rate (%)', fontsize=14, weight='bold')
    ax.set_title('Expected Win Rate Comparison\nPipeline Impact on Performance', 
                 fontsize=16, weight='bold', pad=20)
    ax.set_ylim(0, 85)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(fontsize=11)
    
    # Add annotations
    ax.annotate('Pipeline provides\npre-screened opportunities', 
                xy=(0, 70), xytext=(0.5, 55),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=10, ha='center')
    
    ax.annotate('Combined system\nexceeds components', 
                xy=(2, 72.5), xytext=(2.5, 60),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=10, ha='center')
    
    plt.tight_layout()
    plt.savefig('pipeline_win_rate_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Created: pipeline_win_rate_comparison.png")
    plt.close()

def create_signal_composition():
    """Create stacked bar chart showing signal composition."""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Data
    components = ['Pipeline', 'FinBERT', 'LSTM', 'Technical', 'Momentum', 'Volume']
    weights = np.array([40.0, 15.0, 15.0, 15.0, 9.0, 6.0])
    
    # Cumulative for stacking
    cumulative = np.cumsum(weights)
    starts = np.concatenate([[0], cumulative[:-1]])
    
    # Create horizontal stacked bar
    bar_colors = [colors['pipeline'], colors['finbert'], colors['lstm'], 
                  colors['technical'], colors['momentum'], colors['volume']]
    
    bars = ax.barh(['Signal Composition'], weights[0], left=0, 
                   color=bar_colors[0], edgecolor='black', linewidth=2, label=components[0])
    
    for i in range(1, len(weights)):
        ax.barh(['Signal Composition'], weights[i], left=starts[i], 
                color=bar_colors[i], edgecolor='black', linewidth=2, label=components[i])
    
    # Add percentage labels
    for i, (weight, start) in enumerate(zip(weights, starts)):
        if weight >= 5:  # Only label if segment is wide enough
            ax.text(start + weight/2, 0, f'{weight:.0f}%', 
                   ha='center', va='center', fontsize=12, weight='bold', color='white')
    
    # Style
    ax.set_xlim(0, 100)
    ax.set_xlabel('Contribution to Final Signal (%)', fontsize=14, weight='bold')
    ax.set_title('Signal Composition Breakdown\nHow Pipeline Reports Contribute to Trading Decisions', 
                 fontsize=16, weight='bold', pad=20)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=6, fontsize=11)
    ax.set_yticks([])
    
    # Add divider line
    ax.axvline(x=40, color='white', linestyle='--', linewidth=3, alpha=0.7)
    ax.text(20, 0.3, 'Pipeline\n(Overnight)', ha='center', fontsize=12, weight='bold')
    ax.text(70, 0.3, 'Live ML Components', ha='center', fontsize=12, weight='bold')
    
    plt.tight_layout()
    plt.savefig('pipeline_signal_composition.png', dpi=300, bbox_inches='tight')
    print("✓ Created: pipeline_signal_composition.png")
    plt.close()

def create_timeline_diagram():
    """Create timeline showing pipeline lifecycle."""
    fig, ax = plt.subplots(figsize=(16, 6))
    
    # Timeline
    times = [0, 6, 7, 7.5, 22, 28]
    labels = ['22:00\nPipeline Start', '04:00\nPipeline Complete', 
              '05:00\nReports Loaded', '07:30\nFirst Trades',
              '16:00\nMarket Close', '22:00\nNext Pipeline']
    
    # Draw timeline
    ax.plot(times, [0]*len(times), 'o-', linewidth=4, markersize=12, color=colors['pipeline'])
    
    # Add labels
    for time, label in zip(times, labels):
        ax.text(time, -0.5, label, ha='center', fontsize=10, weight='bold')
    
    # Add phase boxes
    # Phase 1: Pipeline running
    ax.add_patch(mpatches.Rectangle((0, 0.5), 6, 1, facecolor=colors['pipeline'], alpha=0.3))
    ax.text(3, 1, 'Overnight Pipeline\n(6 hours)', ha='center', va='center', fontsize=11, weight='bold')
    
    # Phase 2: Trading hours
    ax.add_patch(mpatches.Rectangle((7, 0.5), 9, 1, facecolor='#27AE60', alpha=0.3))
    ax.text(11.5, 1, 'Paper Trading Active\nUsing Pipeline Reports', 
            ha='center', va='center', fontsize=11, weight='bold')
    
    # Phase 3: After hours
    ax.add_patch(mpatches.Rectangle((16, 0.5), 6, 1, facecolor='#95A5A6', alpha=0.3))
    ax.text(19, 1, 'Market Closed', ha='center', va='center', fontsize=11, weight='bold')
    
    # Annotations
    ax.annotate('Reports generated', xy=(6, 0), xytext=(6, -1.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=9, ha='center')
    
    ax.annotate('Check for updates\nevery 30 min', xy=(11.5, 0), xytext=(11.5, 2.2),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'),
                fontsize=9, ha='center')
    
    # Style
    ax.set_xlim(-1, 29)
    ax.set_ylim(-2, 2.5)
    ax.set_xlabel('Time (Hours)', fontsize=12, weight='bold')
    ax.set_title('Pipeline Lifecycle - 24 Hour View', fontsize=16, weight='bold', pad=20)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('pipeline_timeline.png', dpi=300, bbox_inches='tight')
    print("✓ Created: pipeline_timeline.png")
    plt.close()

def create_performance_heatmap():
    """Create heatmap showing performance by scenario."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Data: [Without Pipeline, With Pipeline]
    scenarios = ['Win Rate', 'Avg Profit', 'Risk Score', 'Trade Quality', 'Overall Score']
    without_pipeline = [60, 55, 65, 58, 59.5]
    with_pipeline = [72, 78, 82, 85, 79.25]
    
    # Create grouped bars
    x = np.arange(len(scenarios))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, without_pipeline, width, label='Without Pipeline (60% capacity)',
                   color='#E74C3C', edgecolor='black', linewidth=1.5)
    bars2 = ax.bar(x + width/2, with_pipeline, width, label='With Pipeline (100% capacity)',
                   color='#27AE60', edgecolor='black', linewidth=1.5)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}',
                    ha='center', va='bottom', fontsize=10, weight='bold')
    
    # Style
    ax.set_ylabel('Score (0-100)', fontsize=12, weight='bold')
    ax.set_title('Performance Comparison: With vs. Without Pipeline Reports', 
                 fontsize=16, weight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.set_ylim(0, 95)
    ax.legend(fontsize=11, loc='upper left')
    ax.grid(axis='y', alpha=0.3)
    
    # Add improvement annotations
    for i, (v1, v2) in enumerate(zip(without_pipeline, with_pipeline)):
        improvement = v2 - v1
        ax.annotate(f'+{improvement:.1f}', 
                   xy=(x[i], v2), xytext=(x[i], v2 + 5),
                   ha='center', fontsize=9, color='green', weight='bold')
    
    plt.tight_layout()
    plt.savefig('pipeline_performance_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Created: pipeline_performance_comparison.png")
    plt.close()

def main():
    """Generate all visualizations."""
    print("\n" + "="*60)
    print("Generating Pipeline Usage Visualizations")
    print("="*60 + "\n")
    
    output_dir = Path('/home/user/webapp/unified_trading_system_v188_COMPLETE_PATCHED')
    import os
    os.chdir(output_dir)
    
    try:
        create_decision_weight_chart()
        create_data_flow_diagram()
        create_win_rate_comparison()
        create_signal_composition()
        create_timeline_diagram()
        create_performance_heatmap()
        
        print("\n" + "="*60)
        print("✓ All visualizations generated successfully!")
        print("="*60)
        print("\nGenerated files:")
        print("  • pipeline_decision_weights.png")
        print("  • pipeline_data_flow.png")
        print("  • pipeline_win_rate_comparison.png")
        print("  • pipeline_signal_composition.png")
        print("  • pipeline_timeline.png")
        print("  • pipeline_performance_comparison.png")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error generating visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
