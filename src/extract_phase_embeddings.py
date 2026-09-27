"""
Extract a TimeSformer embedding for each annotated phase of each video.

Reads data/phase_annotations.json, samples several 8-frame clips (stride 4)
from every phase, averages the clip embeddings, and writes:
  data/phase_embeddings.pkl           dict: phase name -> list of 768-d tensors (or None)
  data/phase_embeddings_metadata.json one record per extracted phase

Usage:
  python src/extract_phase_embeddings.py [--device cuda:0]
"""

import argparse
import json
import pickle
from pathlib import Path

import av
import numpy as np
import torch
from transformers import AutoImageProcessor, TimesformerModel

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / 'data'

MODEL_NAME = "facebook/timesformer-base-finetuned-k400"
PROCESSOR_NAME = "MCG-NJU/videomae-base"
CLIP_LEN = 8            # frames per clip
FRAME_STRIDE = 4        # sampling stride within a clip
CLIPS_PER_PHASE = 5     # reduced automatically for very short phases
PHASES = ['pre_event', 'phase_a_approach', 'phase_b_waiting', 'phase_c_clearance', 'post_event']


def read_video_pyav(container, indices):
    """Decode the frames at the given indices; returns (num_frames, H, W, 3)."""
    frames = []
    container.seek(0)
    start_index = indices[0]
    end_index = indices[-1]
    for i, frame in enumerate(container.decode(video=0)):
        if i > end_index:
            break
        if i >= start_index and i in indices:
            frames.append(frame)
    return np.stack([x.to_ndarray(format="rgb24") for x in frames])


def sample_frame_indices(clip_len, frame_sample_rate, seg_len):
    """
    Sample clip_len frames at the given stride from a window centered in seg_len.
    For seg_len shorter than the stride window, evenly space across the whole segment.
    """
    converted_len = int(clip_len * frame_sample_rate)
    if seg_len < converted_len:
        indices = np.linspace(0, seg_len - 1, num=clip_len)
    else:
        center = (seg_len - 1) / 2
        start_idx = max(0, int(round(center - converted_len / 2)))
        end_idx = start_idx + converted_len - 1
        if end_idx > seg_len - 1:
            end_idx = seg_len - 1
            start_idx = end_idx - converted_len + 1
        indices = np.linspace(start_idx, end_idx, num=clip_len)
    return np.clip(indices, 0, seg_len - 1).astype(np.int64)


def extract_segment_embedding(video_path, start_sec, end_sec, fps, image_processor, model, device,
                              num_clips=CLIPS_PER_PHASE):
    """
    Embed the [start_sec, end_sec] segment of a video as the mean of several clip embeddings.
    Returns a 768-d tensor, or None if no clip could be decoded.
    """
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)
    segment_length = end_frame - start_frame

    min_clip_frames = CLIP_LEN * FRAME_STRIDE
    if segment_length < min_clip_frames:
        num_clips = 1
    elif segment_length < min_clip_frames * 2:
        num_clips = min(2, num_clips)

    container = av.open(str(video_path))
    embeddings = []

    for i in range(num_clips):
        clip_start_frame = start_frame + int(i * segment_length / num_clips)
        clip_end_frame = start_frame + int((i + 1) * segment_length / num_clips)
        clip_segment_length = max(CLIP_LEN, clip_end_frame - clip_start_frame)

        relative_indices = sample_frame_indices(CLIP_LEN, FRAME_STRIDE, clip_segment_length)
        absolute_indices = relative_indices + clip_start_frame

        try:
            video_frames = read_video_pyav(container, absolute_indices)
            inputs = image_processor(list(video_frames), return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = model(**inputs)
                clip_embedding = outputs.last_hidden_state.mean(1).cpu()  # (1, 768)
            embeddings.append(clip_embedding.squeeze(0))
        except Exception as e:
            print(f"      Warning: failed to extract clip {i + 1}/{num_clips}: {e}")

    container.close()

    if not embeddings:
        return None
    return torch.stack(embeddings).mean(dim=0)


def process_video(ann, image_processor, model, device):
    """Return ({phase: embedding or None}, [metadata records]) for one annotated video."""
    video_path = Path(ann['video_path'])
    if not video_path.is_absolute():
        video_path = REPO_ROOT / video_path

    container = av.open(str(video_path))
    fps = float(container.streams.video[0].average_rate)
    container.close()

    phase_embeddings = {}
    metadata = []

    print(f"Processing: {ann['crossing']} - {ann['video_filename']}")

    for phase_name, phase_data in ann['phases'].items():
        if phase_data is None:
            phase_embeddings[phase_name] = None
            continue

        start_sec = phase_data['start_sec']
        end_sec = phase_data['end_sec']
        duration = phase_data['duration_sec']
        print(f"  {phase_name}: {start_sec}s-{end_sec}s ({duration}s)")

        embedding = extract_segment_embedding(video_path, start_sec, end_sec, fps,
                                              image_processor, model, device)
        phase_embeddings[phase_name] = embedding

        if embedding is not None:
            metadata.append({
                'crossing': ann['crossing'],
                'video_filename': ann['video_filename'],
                'phase': phase_name,
                'start_sec': start_sec,
                'end_sec': end_sec,
                'duration_sec': duration,
                'time_of_day': ann['time_of_day'],
                'embedding_shape': list(embedding.shape),
            })

    return phase_embeddings, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--annotations', default=DATA_DIR / 'phase_annotations.json', type=Path)
    parser.add_argument('--output-dir', default=DATA_DIR, type=Path)
    args = parser.parse_args()

    with open(args.annotations, 'r') as f:
        annotations = json.load(f)

    device = torch.device(args.device)
    print(f"Videos to process: {len(annotations)}")
    print(f"Device: {device}")

    image_processor = AutoImageProcessor.from_pretrained(PROCESSOR_NAME)
    model = TimesformerModel.from_pretrained(MODEL_NAME).to(device)
    model.eval()

    all_embeddings = {phase: [] for phase in PHASES}
    all_metadata = []

    for ann in annotations:
        try:
            video_embeddings, metadata = process_video(ann, image_processor, model, device)
        except Exception as e:
            print(f"  Error processing {ann['video_filename']}: {e}")
            video_embeddings, metadata = {}, []
        for phase in PHASES:
            all_embeddings[phase].append(video_embeddings.get(phase))
        all_metadata.extend(metadata)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    embeddings_path = args.output_dir / 'phase_embeddings.pkl'
    metadata_path = args.output_dir / 'phase_embeddings_metadata.json'

    with open(embeddings_path, 'wb') as f:
        pickle.dump(all_embeddings, f)
    with open(metadata_path, 'w') as f:
        json.dump(all_metadata, f, indent=2)

    print(f"\nSaved embeddings to {embeddings_path}")
    print(f"Saved metadata to {metadata_path}")
    for phase, embeddings in all_embeddings.items():
        valid = sum(e is not None for e in embeddings)
        print(f"  {phase}: {valid}/{len(embeddings)} phases embedded")


if __name__ == "__main__":
    main()
