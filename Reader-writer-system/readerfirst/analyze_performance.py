#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import re
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

# Set up paths
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
workspace = os.path.join(script_dir, "readers_writers")
c_file = os.path.join(workspace, "reader_writer_first.c")
exe_file = os.path.join(workspace, "reader_writer_first.exe")

def compile_program():
    """Compile the C program using gcc"""
    global workspace
    
    print("=" * 60)
    print("Compiling reader_writer_first.c...")
    print(f"Working directory: {workspace}")
    print("=" * 60)
    
    c_file = "reader_writer_first.c"
    exe_file = "reader_writer_first.exe"
    
    cmd = [
        "gcc",
        "-o", exe_file,
        "-pthread",
        c_file
    ]
    
    try:
        result = subprocess.run(cmd, cwd=workspace, check=True, capture_output=True, text=True)
        print("[OK] Compilation successful!")
        return True
    except subprocess.CalledProcessError as e:
        print("[FAIL] Compilation failed!")
        print(e.stderr)
        return False

def run_test(num_readers, num_writers):
    """Run the program with specific reader/writer ratio"""
    global workspace
    
    print("\nRunning test: {} readers, {} writers".format(num_readers, num_writers))
    
    exe_file = "reader_writer_first.exe"
    exe_path = os.path.join(workspace, exe_file)
    
    try:
        result = subprocess.run(
            [exe_path, str(num_readers), str(num_writers)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        output = result.stdout
        
        # Extract CSV output
        csv_match = re.search(r'CSV_OUTPUT:(.+)', output)
        if csv_match:
            csv_data = csv_match.group(1).strip()
            return csv_data
        else:
            print("Warning: Could not extract data from output")
            return None
            
    except subprocess.TimeoutExpired:
        print("Test timed out")
        return None
    except Exception as e:
        print("Error running test: {}".format(e))
        return None

def run_all_tests():
    """Run tests with various reader/writer ratios"""
    
    # Test configurations: (readers, writers)
    test_configs = [
        (2, 1),
        (3, 1),
        (5, 1),
        (10, 1),
        (5, 2),
        (10, 2),
        (15, 3),
        (3, 3),
        (1, 3),
        (1, 5),
    ]
    
    results = []
    
    for readers, writers in test_configs:
        data = run_test(readers, writers)
        if data:
            parts = data.split(',')
            results.append({
                'readers': int(parts[0]),
                'writers': int(parts[1]),
                'total_time_ms': int(parts[2]),
                'read_count': int(parts[3]),
                'write_count': int(parts[4]),
                'avg_read_time_us': float(parts[5]),
                'avg_write_time_us': float(parts[6]),
                'read_ops_sec': float(parts[7]),
                'write_ops_sec': float(parts[8]),
                'ratio': readers / writers if writers > 0 else float('inf')
            })
    
    return pd.DataFrame(results)

def generate_plots(df):
    """Generate comparison plots"""
    
    if df.empty:
        print("No data to plot")
        return
    
    # Sort by ratio for better visualization
    df_sorted = df.sort_values('ratio')
    
    # Create figure with multiple subplots
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Reader-First Model: Performance Comparison', fontsize=16, fontweight='bold')
    
    # 1. Read Operations per Second
    ax = axes[0, 0]
    ax.plot(df_sorted['ratio'], df_sorted['read_ops_sec'], 'o-', linewidth=2, markersize=8, color='blue')
    ax.set_xlabel('Reader/Writer Ratio')
    ax.set_ylabel('Operations/Second')
    ax.set_title('Read Operations/Second')
    ax.grid(True, alpha=0.3)
    
    # 2. Write Operations per Second
    ax = axes[0, 1]
    ax.plot(df_sorted['ratio'], df_sorted['write_ops_sec'], 'o-', linewidth=2, markersize=8, color='red')
    ax.set_xlabel('Reader/Writer Ratio')
    ax.set_ylabel('Operations/Second')
    ax.set_title('Write Operations/Second')
    ax.grid(True, alpha=0.3)
    
    # 3. Average Response Time
    ax = axes[0, 2]
    ax.plot(df_sorted['ratio'], df_sorted['avg_read_time_us'], 'o-', label='Read', linewidth=2, markersize=8, color='blue')
    ax.plot(df_sorted['ratio'], df_sorted['avg_write_time_us'], 's-', label='Write', linewidth=2, markersize=8, color='red')
    ax.set_xlabel('Reader/Writer Ratio')
    ax.set_ylabel('Time (μs)')
    ax.set_title('Average Response Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Total Operations in Test
    ax = axes[1, 0]
    x = range(len(df_sorted))
    width = 0.35
    ax.bar([i - width/2 for i in x], df_sorted['read_count'], width, label='Reads', color='blue', alpha=0.7)
    ax.bar([i + width/2 for i in x], df_sorted['write_count'], width, label='Writes', color='red', alpha=0.7)
    ax.set_xlabel('Configuration')
    ax.set_ylabel('Operation Count')
    ax.set_title('Total Operations (3s test)')
    ax.set_xticks(x)
    ax.set_xticklabels([f"{row['readers']}R:{row['writers']}W" for _, row in df_sorted.iterrows()], rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 5. Throughput Comparison
    ax = axes[1, 1]
    total_ops = df_sorted['read_count'] + df_sorted['write_count']
    ax.plot(df_sorted['ratio'], total_ops / df_sorted['total_time_ms'] * 1000, 'o-', linewidth=2, markersize=8, color='green')
    ax.set_xlabel('Reader/Writer Ratio')
    ax.set_ylabel('Total Ops/Second')
    ax.set_title('Combined Throughput')
    ax.grid(True, alpha=0.3)
    
    # 6. Summary Table
    ax = axes[1, 2]
    ax.axis('tight')
    ax.axis('off')
    summary_data = df_sorted[['readers', 'writers', 'read_count', 'write_count', 'read_ops_sec']].copy()
    summary_data.columns = ['R', 'W', 'Read Ops', 'Write Ops', 'Read/s']
    summary_data['Read Ops'] = summary_data['Read Ops'].astype(int)
    summary_data['Write Ops'] = summary_data['Write Ops'].astype(int)
    summary_data['Read/s'] = summary_data['Read/s'].apply(lambda x: f'{x:.1f}')
    table = ax.table(cellText=summary_data.values, colLabels=summary_data.columns, 
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    ax.set_title('Performance Summary')
    
    plt.tight_layout()
    
    # Save figure
    output_path = os.path.join(os.getcwd(), 'performance_analysis_reader_first.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print("\n[OK] Plot saved: {}".format(output_path))
    
    # Also save as PDF
    pdf_path = os.path.join(os.getcwd(), 'performance_analysis_reader_first.pdf')
    plt.savefig(pdf_path, bbox_inches='tight')
    print("[OK] PDF saved: {}".format(pdf_path))
    
    plt.show()

def save_csv_results(df):
    """Save results to CSV"""
    csv_path = os.path.join(os.getcwd(), 'performance_results_reader_first.csv')
    df.to_csv(csv_path, index=False)
    print("[OK] Results saved: {}".format(csv_path))
    
    # Print summary
    print("\n" + "=" * 60)
    print("PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 60)
    print(df.to_string(index=False))
    print("=" * 60)

def main():
    print("\n" + "=" * 60)
    print("Reader-First Model Performance Analysis Tool")
    print("Creating comprehensive performance comparison")
    print("=" * 60 + "\n")
    
    # Step 1: Compile
    if not compile_program():
        print("Failed to compile program")
        return
    
    # Step 2: Run tests
    print("\n" + "=" * 60)
    print("Running Performance Tests...")
    print("=" * 60)
    df = run_all_tests()
    
    if df.empty:
        print("No test results available")
        return
    
    # Step 3: Save results
    save_csv_results(df)
    
    # Step 4: Generate plots
    print("\n" + "=" * 60)
    print("Generating Performance Plots...")
    print("=" * 60)
    generate_plots(df)
    
    print("\n" + "=" * 60)
    print("Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
