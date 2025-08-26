import cv2
import numpy as np
import os
from tqdm import tqdm

def extract_frames(video_path, num_frames=30, target_size=(224, 224)):
    if not os.path.exists(video_path):
        return None
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Hitung interval frame
    frame_interval = max(1, total_frames // num_frames)
    
    frames = []
    for i in range(num_frames):
        frame_idx = i * frame_interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if ret:
            # Resize dan preprocess frame
            frame = cv2.resize(frame, target_size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = frame.astype(np.float32) / 255.0
            frames.append(frame)
    
    cap.release()
    
    if not frames:
        return None
        
    return np.array(frames)

def extract_all_visual_features(video_paths, num_frames=30, target_size=(224, 224)):
    all_features = []
    
    for path in tqdm(video_paths, desc="Extracting visual features"):
        features = extract_frames(path, num_frames, target_size)
        if features is not None:
            all_features.append(features)
    
    return np.array(all_features)

if __name__ == "__main__":
    import pandas as pd
    
    train_df = pd.read_csv('../data/train_parsed.csv')
    video_paths = [f"../data/raw_videos/{id}.mp4" for id in train_df['id'].head(500)]
    
    # Ekstraksi fitur visual
    visual_features = extract_all_visual_features(video_paths)
    
    print(f"\nShape fitur visual: {visual_features.shape}")