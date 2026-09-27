"""
Analyze manual phase annotations to understand temporal patterns.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Load annotations
REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / 'data'
annotations_path = DATA_DIR / 'phase_annotations.json'
with open(annotations_path, 'r') as f:
    annotations = json.load(f)

print("="*70)
print("PHASE ANNOTATION ANALYSIS")
print("="*70)

# Collect phase durations
phase_stats = {
    'pre_event': [],
    'phase_a_approach': [],
    'phase_b_waiting': [],
    'phase_c_clearance': [],
    'post_event': []
}

crossing_names = []

for ann in annotations:
    crossing_names.append(ann['crossing'].split(' ')[0])  # Short name

    print(f"\n{ann['crossing']}")
    print(f"  Video: {ann['video_filename']}")
    print(f"  Time of day: {ann['time_of_day']}")
    print(f"  Phases:")

    for phase_name, phase_data in ann['phases'].items():
        if phase_data:
            duration = phase_data['duration_sec']
            phase_stats[phase_name].append(duration)
            print(f"    {phase_name}: {duration}s ({duration/60:.1f} min)")
        else:
            phase_stats[phase_name].append(None)
            print(f"    {phase_name}: Not available")

# Print summary statistics
print("\n" + "="*70)
print("PHASE DURATION STATISTICS")
print("="*70)

for phase_name, durations in phase_stats.items():
    valid_durations = [d for d in durations if d is not None]

    if valid_durations:
        print(f"\n{phase_name.upper()}:")
        print(f"  Count: {len(valid_durations)}/{len(annotations)} videos")
        print(f"  Mean: {np.mean(valid_durations):.1f}s ({np.mean(valid_durations)/60:.1f} min)")
        print(f"  Std: {np.std(valid_durations):.1f}s")
        print(f"  Range: {min(valid_durations):.1f}s - {max(valid_durations):.1f}s")
        print(f"  Median: {np.median(valid_durations):.1f}s")

# Create visualization
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

# Plot 1: Phase durations by crossing
core_phases = ['phase_a_approach', 'phase_b_waiting', 'phase_c_clearance']
for idx, phase_name in enumerate(core_phases):
    ax = axes[idx]
    durations = []
    labels = []

    for i, ann in enumerate(annotations):
        if ann['phases'][phase_name]:
            durations.append(ann['phases'][phase_name]['duration_sec'])
            labels.append(crossing_names[i])

    bars = ax.bar(labels, durations, edgecolor='black', alpha=0.7)
    ax.set_ylabel('Duration (seconds)')
    ax.set_title(phase_name.replace('_', ' ').title())
    ax.tick_params(axis='x', rotation=45)

    # Color by time of day
    for i, ann in enumerate(annotations):
        if ann['phases'][phase_name]:
            color = 'navy' if ann['time_of_day'] == 'night' else 'orange'
            bars[i].set_color(color)

# Plot 4: Total event duration
ax = axes[3]
event_durations = []
event_labels = []

for i, ann in enumerate(annotations):
    # Sum all core phases
    total = sum([
        ann['phases'][p]['duration_sec']
        for p in core_phases
        if ann['phases'][p]
    ])
    event_durations.append(total)
    event_labels.append(crossing_names[i])

bars = ax.bar(event_labels, event_durations, edgecolor='black', alpha=0.7)
ax.set_ylabel('Duration (seconds)')
ax.set_title('Total Event Duration (A + B + C)')
ax.tick_params(axis='x', rotation=45)

for i, ann in enumerate(annotations):
    color = 'navy' if ann['time_of_day'] == 'night' else 'orange'
    bars[i].set_color(color)

# Plot 5: Context availability (pre/post event footage)
ax = axes[4]
context_data = {
    'Pre-event': [1 if ann['phases']['pre_event'] else 0 for ann in annotations],
    'Post-event': [1 if ann['phases']['post_event'] else 0 for ann in annotations]
}

x = np.arange(len(annotations))
width = 0.35

ax.bar(x - width/2, context_data['Pre-event'], width, label='Pre-event', alpha=0.7)
ax.bar(x + width/2, context_data['Post-event'], width, label='Post-event', alpha=0.7)
ax.set_ylabel('Available (1) or Not (0)')
ax.set_title('Context Footage Availability')
ax.set_xticks(x)
ax.set_xticklabels(crossing_names, rotation=45)
ax.legend()
ax.set_ylim([0, 1.2])

# Plot 6: Phase proportion breakdown
ax = axes[5]
proportions = []

for ann in annotations:
    total = sum([ann['phases'][p]['duration_sec'] for p in core_phases if ann['phases'][p]])
    props = [
        ann['phases'][p]['duration_sec'] / total * 100 if ann['phases'][p] else 0
        for p in core_phases
    ]
    proportions.append(props)

proportions = np.array(proportions)
bottom = np.zeros(len(annotations))

colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
for idx, phase_name in enumerate(core_phases):
    ax.bar(crossing_names, proportions[:, idx], bottom=bottom,
           label=phase_name.replace('phase_', '').replace('_', ' ').title(),
           color=colors[idx], alpha=0.8)
    bottom += proportions[:, idx]

ax.set_ylabel('Percentage (%)')
ax.set_title('Phase Proportion Breakdown')
ax.legend()
ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig(DATA_DIR / 'phase_analysis.png', dpi=300, bbox_inches='tight')
print(f"\n{'='*70}")
print(f"Visualization saved to: {DATA_DIR / 'phase_analysis.png'}")
print("="*70)

plt.show()

# Key observations
print("\n" + "="*70)
print("KEY OBSERVATIONS")
print("="*70)

print("\n1. PHASE A (Approach) - Warning to Gates Down:")
phase_a_durations = [d for d in phase_stats['phase_a_approach'] if d]
print(f"   Very consistent: {min(phase_a_durations)}-{max(phase_a_durations)}s (likely standardized)")

print("\n2. PHASE B (Waiting) - Gates Down to Train Clears:")
phase_b_durations = [d for d in phase_stats['phase_b_waiting'] if d]
print(f"   High variance: {min(phase_b_durations)}-{max(phase_b_durations)}s")
print(f"   Depends on train speed and length")

print("\n3. PHASE C (Clearance) - Train Clears to Gates Up:")
phase_c_durations = [d for d in phase_stats['phase_c_clearance'] if d]
print(f"   Fairly consistent: {min(phase_c_durations)}-{max(phase_c_durations)}s")

print("\n4. CONTEXT FOOTAGE:")
pre_count = sum(1 for d in phase_stats['pre_event'] if d)
post_count = sum(1 for d in phase_stats['post_event'] if d)
print(f"   Pre-event available: {pre_count}/{len(annotations)} videos")
print(f"   Post-event available: {post_count}/{len(annotations)} videos")
print(f"   Most videos are tightly trimmed to events")

print("\n5. DAY vs NIGHT:")
day_videos = [ann for ann in annotations if ann['time_of_day'] == 'day']
night_videos = [ann for ann in annotations if ann['time_of_day'] == 'night']
print(f"   Day videos: {len(day_videos)}")
print(f"   Night videos: {len(night_videos)}")
print(f"   Enables time-of-day comparison!")

print("\n" + "="*70)
