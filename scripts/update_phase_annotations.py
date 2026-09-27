#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS_PATH = REPO_ROOT / 'data' / 'phase_annotations.json'

def parse_time_to_seconds(time_str):
    """Convert time string (M:SS or MM:SS) to seconds"""
    parts = time_str.strip().split(':')
    if len(parts) == 2:
        mins, secs = parts
        return int(mins) * 60 + int(secs)
    elif len(parts) == 3:
        hours, mins, secs = parts
        return int(hours) * 3600 + int(mins) * 60 + int(secs)
    else:
        return int(parts[0])

def categorize_time_of_day(timestamp_str):
    """Categorize time based on 4-category traffic-focused system"""
    # Parse timestamp format like "17:36:57" or "07:39:37"
    parts = timestamp_str.strip().split(':')
    hour = int(parts[0])

    if 19 <= hour or hour < 6:  # 7PM-6AM
        return "off_peak"
    elif 6 <= hour < 10:  # 6AM-10AM
        return "morning_rush"
    elif 10 <= hour < 15:  # 10AM-3PM
        return "midday"
    else:  # 3PM-7PM (15-19)
        return "afternoon_evening"

# Video annotations with timestamps and phase timings
annotations = {
    "35th and Cornhusker Hwy": {
        "2024-02-10_03-20-23 - Trim 1.mp4": {
            "timestamp": "17:36:57",
            "duration": 224.8,
            "lights_start": 26,
            "gates_horizontal": 41,
            "train_clears": "3:15",
            "gates_vertical": "3:30"
        },
        "2024-02-10_03-20-23 - Trim 5.mp4": {
            "timestamp": "22:04:55",
            "duration": 453.8,
            "lights_start": 36,
            "gates_horizontal": 51,
            "train_clears": "4:09",
            "gates_vertical": "4:26"
        },
        "2024-02-10_03-20-23 - Trim 6.mp4": {
            "timestamp": "23:48:02",
            "duration": 37.8,
            "lights_start": 0,
            "gates_horizontal": 0,
            "train_clears": 15,
            "gates_vertical": 33
        },
        "2024-02-10_03-20-23 - Trim 7.mp4": {
            "timestamp": "00:29:50",
            "duration": 219.4,
            "lights_start": 0,
            "gates_horizontal": 9,
            "train_clears": "3:02",
            "gates_vertical": "3:18"
        },
        "2024-02-10_03-20-23 - Trim 9.mp4": {
            "timestamp": "00:50:53",
            "duration": 189.4,
            "lights_start": 0,
            "gates_horizontal": 8,
            "train_clears": "2:51",
            "gates_vertical": "3:08"
        },
        "2024-02-10_03-20-23 - Trim 10.mp4": {
            "timestamp": "01:13:13",
            "duration": 101.5,
            "lights_start": 0,
            "gates_horizontal": 0,
            "train_clears": "1:18",
            "gates_vertical": "1:33"
        },
        "2024-02-10_03-20-23 - Trim 11.mp4": {
            "timestamp": "02:05:37",
            "duration": 157.6,
            "lights_start": 0,
            "gates_horizontal": 1,
            "train_clears": "2:19",
            "gates_vertical": "2:33"
        },
        "2024-02-10_03-20-23 - Trim 12.mp4": {
            "timestamp": "02:51:15",
            "duration": 360.8,
            "lights_start": 0,
            "gates_horizontal": 7,
            "train_clears": "5:29",
            "gates_vertical": "5:49"
        },
        "2024-02-10_15-10-43 - Trim 1.mp4": {
            "timestamp": "03:32:02",
            "duration": 228.0,
            "lights_start": 0,
            "gates_horizontal": 3,
            "train_clears": "3:12",
            "gates_vertical": "3:30"
        },
        "2024-02-10_15-10-43 - Trim 2.mp4": {
            "timestamp": "03:50:02",
            "duration": 56.7,
            "lights_start": 0,
            "gates_horizontal": 3,
            "train_clears": 34,
            "gates_vertical": 51
        },
        "2024-02-10_15-10-43 - Trim 3.mp4": {
            "timestamp": "05:05:01",
            "duration": 234.2,
            "lights_start": 0,
            "gates_horizontal": 10,
            "train_clears": "3:18",
            "gates_vertical": "3:35"
        },
        "2024-02-10_15-10-43 - Trim 4.mp4": {
            "timestamp": "05:34:54",
            "duration": 62.7,
            "lights_start": 0,
            "gates_horizontal": 9,
            "train_clears": 37,
            "gates_vertical": 52
        },
        "2024-02-10_15-10-43 - Trim 5.mp4": {
            "timestamp": "06:02:43",
            "duration": 146.9,
            "lights_start": 5,
            "gates_horizontal": 20,
            "train_clears": "2:10",
            "gates_vertical": "2:26"
        },
        "2024-02-10_15-10-43 - Trim 6.mp4": {
            "timestamp": "07:16:55",
            "duration": 214.4,
            "lights_start": 0,
            "gates_horizontal": 13,
            "train_clears": "2:59",
            "gates_vertical": "3:16"
        },
        "2024-02-10_15-10-43 - Trim 7.mp4": {
            "timestamp": "07:27:55",
            "duration": 180.3,
            "lights_start": 0,
            "gates_horizontal": 14,
            "train_clears": "2:29",
            "gates_vertical": "2:46"
        },
        "2024-02-10_15-10-43 - Trim 8.mp4": {
            "timestamp": "07:35:40",
            "duration": 229.5,
            "lights_start": 0,
            "gates_horizontal": 14,
            "train_clears": "3:11",
            "gates_vertical": "3:29"
        },
        "2024-02-10_15-10-43 - Trim 9.mp4": {
            "timestamp": "08:01:14",
            "duration": 226.6,
            "lights_start": 0,
            "gates_horizontal": 12,
            "train_clears": "2:59",
            "gates_vertical": "3:17"
        },
        "2024-02-10_15-10-43 - Trim 10.mp4": {
            "timestamp": "09:47:53",
            "duration": 128.5,
            "lights_start": 0,
            "gates_horizontal": 13,
            "train_clears": "1:36",
            "gates_vertical": "1:50"
        },
        "2024-02-10_15-10-43 - Trim 11.mp4": {
            "timestamp": "11:13:59",
            "duration": 680.9,
            "lights_start": 0,
            "gates_horizontal": 13,
            "train_clears": "10:20",
            "gates_vertical": "10:41"
        },
        "2024-02-10_15-10-43 - Trim 12.mp4": {
            "timestamp": "11:30:36",
            "duration": 268.9,
            "lights_start": 0,
            "gates_horizontal": 12,
            "train_clears": "3:07",
            "gates_vertical": "3:25"
        },
        "2024-02-10_15-10-43 - Trim 13.mp4": {
            "timestamp": "11:51:01",
            "duration": 149.3,
            "lights_start": 0,
            "gates_horizontal": 12,
            "train_clears": "1:45",
            "gates_vertical": "2:00"
        },
        "2024-02-10_15-10-43 - Trim 14.mp4": {
            "timestamp": "12:26:49",
            "duration": 321.0,
            "lights_start": 0,
            "gates_horizontal": 0,
            "train_clears": "4:32",
            "gates_vertical": "4:51"
        },
        "2024-02-10_15-10-43 - Trim 15.mp4": {
            "timestamp": "12:56:20",
            "duration": 279.5,
            "lights_start": 0,
            "gates_horizontal": 13,
            "train_clears": "3:28",
            "gates_vertical": "3:44"
        }
    },
    "27th and NE Pkwy": {
        "2024-02-10_03-20-40 - Trim 1.mp4": {
            "timestamp": "23:38:25",
            "duration": 308.1,
            "lights_start": 0,
            "gates_horizontal": 12,
            "train_clears": "4:18",
            "gates_vertical": "4:36"
        }
    },
    "56 & Old Cheney": {
        "2024-02-12_16-24-58 - Trim 1.mp4": {
            "timestamp": "07:39:37",
            "duration": 829.6,
            "lights_start": "1:24",
            "gates_horizontal": "1:38",
            "train_clears": "6:06",
            "gates_vertical": "6:16"
        }
    },
    "NW 12th & Cornhusker": {
        "2024-02-14_14-58-11 - Trim 1.mp4": {
            "timestamp": "08:07:15",
            "duration": 272.4,
            "lights_start": 0,
            "gates_horizontal": 13,
            "train_clears": "3:31",
            "gates_vertical": "3:47"
        },
        "2024-02-14_14-58-11 - Trim 2.mp4": {
            "timestamp": "10:41:53",
            "duration": 251.7,
            "lights_start": "1:03",
            "gates_horizontal": "1:18",
            "train_clears": "3:45",
            "gates_vertical": "4:00"
        },
        "2024-02-16_12-18-46 - Trim 1.mp4": {
            "timestamp": "08:35:49",
            "duration": 158.3,
            "lights_start": 14,
            "gates_horizontal": 30,
            "train_clears": "1:33",
            "gates_vertical": "2:04"
        },
        "2024-02-16_12-18-46 - Trim 2.mp4": {
            "timestamp": "10:09:07",
            "duration": 95.2,
            "lights_start": 0,
            "gates_horizontal": 13,
            "train_clears": "1:16",
            "gates_vertical": "1:30"
        },
        "2024-02-16_12-18-46 - Trim 3.mp4": {
            "timestamp": "13:27:15",
            "duration": 284.9,
            "lights_start": 0,
            "gates_horizontal": 12,
            "train_clears": "4:07",
            "gates_vertical": "4:20"
        },
        "2024-02-16_12-18-46 - Trim 4.mp4": {
            "timestamp": "15:51:21",
            "duration": 178.5,
            "lights_start": 19,
            "gates_horizontal": 33,
            "train_clears": "2:30",
            "gates_vertical": "2:44"
        }
    }
}

# Load existing phase_annotations.json
with open(ANNOTATIONS_PATH, 'r') as f:
    phase_data = json.load(f)

# Create a lookup dictionary for easy access
video_lookup = {}
for entry in phase_data:
    key = (entry['crossing'], entry['video_filename'])
    video_lookup[key] = entry

# Update existing entries with correct time_of_day and phase timings
for crossing, videos in annotations.items():
    for video_filename, video_data in videos.items():
        key = (crossing, video_filename)

        # Get time_of_day category
        time_of_day = categorize_time_of_day(video_data['timestamp'])

        # Convert time strings to seconds
        lights_start_sec = parse_time_to_seconds(str(video_data['lights_start']))
        gates_horizontal_sec = parse_time_to_seconds(str(video_data['gates_horizontal']))
        train_clears_sec = parse_time_to_seconds(str(video_data['train_clears']))
        gates_vertical_sec = parse_time_to_seconds(str(video_data['gates_vertical']))
        duration_sec = video_data['duration']

        # Build phases
        phases = {}

        # Pre-event phase (if lights don't start at 0)
        if lights_start_sec > 0:
            phases['pre_event'] = {
                "start_sec": 0,
                "end_sec": lights_start_sec,
                "duration_sec": lights_start_sec,
                "description": "Normal traffic before warning"
            }
        else:
            phases['pre_event'] = None

        # Phase A (approach) - from lights start to gates horizontal
        if lights_start_sec < gates_horizontal_sec:
            phases['phase_a_approach'] = {
                "start_sec": lights_start_sec,
                "end_sec": gates_horizontal_sec,
                "duration_sec": gates_horizontal_sec - lights_start_sec,
                "description": "Lights flashing -> Gates fully down" if lights_start_sec == 0 and gates_horizontal_sec > 0 else "Gates moving -> Gates fully down"
            }
        elif lights_start_sec == 0 and gates_horizontal_sec == 0:
            phases['phase_a_approach'] = None
        else:
            phases['phase_a_approach'] = None

        # Phase B (waiting) - from gates horizontal to train clears
        phases['phase_b_waiting'] = {
            "start_sec": gates_horizontal_sec,
            "end_sec": train_clears_sec,
            "duration_sec": train_clears_sec - gates_horizontal_sec,
            "description": f"Gates down -> Train clears ({video_data['train_clears']} = {train_clears_sec} sec)" if isinstance(video_data['train_clears'], str) else f"Gates down -> Train clears"
        }

        # Phase C (clearance) - from train clears to gates vertical
        phases['phase_c_clearance'] = {
            "start_sec": train_clears_sec,
            "end_sec": gates_vertical_sec,
            "duration_sec": gates_vertical_sec - train_clears_sec,
            "description": f"Train clears -> Gates fully up ({video_data['gates_vertical']} = {gates_vertical_sec} sec)" if isinstance(video_data['gates_vertical'], str) else f"Train clears -> Gates fully up"
        }

        # Post-event phase (if video continues after gates are up)
        if gates_vertical_sec < duration_sec:
            post_duration = round(duration_sec - gates_vertical_sec, 1)
            phases['post_event'] = {
                "start_sec": gates_vertical_sec,
                "end_sec": duration_sec,
                "duration_sec": post_duration,
                "description": f"Normal traffic after event (video ends at {int(duration_sec//60)}:{int(duration_sec%60):02d} = {duration_sec} sec)"
            }
        else:
            phases['post_event'] = None

        # Update or add entry
        if key in video_lookup:
            # Update existing entry
            video_lookup[key]['time_of_day'] = time_of_day
            video_lookup[key]['phases'] = phases
            print(f"Updated: {crossing} - {video_filename} -> {time_of_day}")
        else:
            # Add new entry
            new_entry = {
                "crossing": crossing,
                "video_filename": video_filename,
                "video_path": f"data/{crossing}/{video_filename}",
                "file_timestamp": f"2024-{video_filename[5:7]}-{video_filename[8:10]}T{video_filename[11:13]}:{video_filename[14:16]}:{video_filename[17:19]}",
                "time_of_day": time_of_day,
                "phases": phases,
                "notes": f"{time_of_day.replace('_', ' ').title()} footage."
            }
            phase_data.append(new_entry)
            print(f"Added: {crossing} - {video_filename} -> {time_of_day}")

# Sort by crossing and filename
phase_data.sort(key=lambda x: (x['crossing'], x['video_filename']))

# Save updated phase_annotations.json
with open(ANNOTATIONS_PATH, 'w') as f:
    json.dump(phase_data, f, indent=2)

print("\nphase_annotations.json updated successfully!")
print(f"Total videos: {len(phase_data)}")

# Print time_of_day distribution
time_categories = {}
for entry in phase_data:
    tod = entry['time_of_day']
    time_categories[tod] = time_categories.get(tod, 0) + 1

print("\nTime of day distribution:")
for category, count in sorted(time_categories.items()):
    print(f"  {category}: {count}")
