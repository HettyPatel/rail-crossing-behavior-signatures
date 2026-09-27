#!/usr/bin/env python3
import av
from pathlib import Path

videos = [
    # 35th and Cornhusker Hwy (23 videos)
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 1.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 5.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 6.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 7.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 9.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 10.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 11.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_03-20-23 - Trim 12.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 1.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 2.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 3.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 4.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 5.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 6.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 7.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 8.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 9.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 10.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 11.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 12.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 13.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 14.mp4'),
    ('35th and Cornhusker Hwy', '2024-02-10_15-10-43 - Trim 15.mp4'),
    # 27th and NE Pkwy (1 video)
    ('27th and NE Pkwy', '2024-02-10_03-20-40 - Trim 1.mp4'),
    # 56 & Old Cheney (1 video)
    ('56 & Old Cheney', '2024-02-12_16-24-58 - Trim 1.mp4'),
    # NW 12th & Cornhusker (6 videos)
    ('NW 12th & Cornhusker', '2024-02-14_14-58-11 - Trim 1.mp4'),
    ('NW 12th & Cornhusker', '2024-02-14_14-58-11 - Trim 2.mp4'),
    ('NW 12th & Cornhusker', '2024-02-16_12-18-46 - Trim 1.mp4'),
    ('NW 12th & Cornhusker', '2024-02-16_12-18-46 - Trim 2.mp4'),
    ('NW 12th & Cornhusker', '2024-02-16_12-18-46 - Trim 3.mp4'),
    ('NW 12th & Cornhusker', '2024-02-16_12-18-46 - Trim 4.mp4'),
]

for crossing, video in videos:
    video_path = Path(__file__).resolve().parents[1] / 'data' / crossing / video
    container = av.open(str(video_path))
    duration = float(container.duration) / av.time_base
    mins = int(duration // 60)
    secs = int(duration % 60)
    print(f'{video}: {mins}:{secs:02d} ({duration:.1f} seconds)')
    container.close()
