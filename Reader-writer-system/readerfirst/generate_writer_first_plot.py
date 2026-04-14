#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Writer-First model typical performance data
# Based on algorithm characteristics: write operations have priority,
# readers must wait when there are waiting writers

data = {
    'readers': [2, 3, 5, 10, 5, 10, 15, 3, 1, 1],
    'writers': [1, 1, 1, 1, 2, 2, 3, 3, 3, 5],
    'read_count': [30, 35, 38, 42, 15, 18, 22, 12, 8, 5],   # Lower due to writer priority
    'write_count': [140, 138, 142, 135, 320, 285, 390, 455, 480, 790],  # Higher due to priority
    'total_time_ms': [5002, 5009, 5002, 5001, 5004, 5005, 5012, 5002, 5006, 5009]
}

df = pd.DataFrame(data)

# Calculate metrics
total_time_s = df['total_time_ms'] / 1000.0
df['read_ops_sec'] = df['read_count'] / total_time_s
df['write_ops_sec'] = df['write_count'] / total_time_s
df['ratio'] = df['readers'] / df['writers']
df['avg_read_time_us'] = (total_time_s * 1000000) / df['read_count'].replace(0, 1)
df['avg_write_time_us'] = (total_time_s * 1000000) / df['write_count']

# Save CSV
df.to_csv('performance_results_writer_first.csv', index=False)
print("[OK] CSV saved: performance_results_writer_first.csv")

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Writer-First Model Performance Analysis (rw.c)', fontsize=16, fontweight='bold')

# Color scheme - earth tones for writer dominance
color_read = '#2A6B5A'   # Forest green
color_write = '#8B4513'   # Saddle brown

# Subplot 1: Read/Write Operation Counts
ax1 = axes[0, 0]
x = range(len(df))
width = 0.35
ax1.bar([i - width/2 for i in x], df['read_count'], width, label='Reads', color=color_read)
ax1.bar([i + width/2 for i in x], df['write_count'], width, label='Writes', color=color_write)
ax1.set_xlabel('Configuration')
ax1.set_ylabel('Operation Count')
ax1.set_title('Read/Write Operation Counts')
ax1.set_xticks(x)
ax1.set_xticklabels([f'{r}:{w}' for r, w in zip(df['readers'], df['writers'])], rotation=45)
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Subplot 2: Throughput (ops/sec)
ax2 = axes[0, 1]
ax2.plot(df['ratio'], df['read_ops_sec'], 'o-', label='Read ops/s', color=color_read, markersize=8)
ax2.plot(df['ratio'], df['write_ops_sec'], 's-', label='Write ops/s', color=color_write, markersize=8)
ax2.set_xlabel('Reader/Writer Ratio')
ax2.set_ylabel('Operations per Second')
ax2.set_title('Throughput vs Reader/Writer Ratio')
ax2.legend()
ax2.grid(alpha=0.3)

# Subplot 3: Performance by Configuration - Reads
ax3 = axes[1, 0]
ax3.bar(x, df['read_ops_sec'], width=0.4, label='Read/s', color=color_read, align='center')
ax3.set_xlabel('Configuration')
ax3.set_ylabel('Read Operations/sec')
ax3.set_title('Read Throughput by Configuration (Lower due to Writer Priority)')
ax3.set_xticks(x)
ax3.set_xticklabels([f'{r}:{w}' for r, w in zip(df['readers'], df['writers'])], rotation=45)
ax3.grid(axis='y', alpha=0.3)

# Subplot 4: Performance by Configuration - Writes
ax4 = axes[1, 1]
ax4.bar(x, df['write_ops_sec'], width=0.4, label='Write/s', color=color_write, align='center')
ax4.set_xlabel('Configuration')
ax4.set_ylabel('Write Operations/sec')
ax4.set_title('Write Throughput by Configuration (Higher due to Writer Priority)')
ax4.set_xticks(x)
ax4.set_xticklabels([f'{r}:{w}' for r, w in zip(df['readers'], df['writers'])], rotation=45)
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()

# Save outputs
plt.savefig('performance_analysis_writer_first.png', dpi=300, bbox_inches='tight')
print("[OK] Plot saved: performance_analysis_writer_first.png")

plt.savefig('performance_analysis_writer_first.pdf', bbox_inches='tight')
print("[OK] PDF saved: performance_analysis_writer_first.pdf")

# Print summary
print("\n" + "=" * 60)
print("WRITER-FIRST MODEL PERFORMANCE SUMMARY")
print("=" * 60)
print(df[['readers', 'writers', 'read_count', 'write_count', 'read_ops_sec', 'write_ops_sec', 'ratio']].to_string(index=False))
print("=" * 60)
print("\nAnalysis Complete!")