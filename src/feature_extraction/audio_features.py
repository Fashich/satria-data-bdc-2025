import librosa
import numpy as np
import os
from tqdm import tqdm

def extract_audio_features(video_path, n_mfcc=40, max_len=64):
    if not os.path.exists(video_path):
        return None
    
    try:
        # Load audio dari video
        y, sr = librosa.load(video_path, sr=None)
        
        # Ekstrak MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        
        # Normalisasi
        mfcc = (mfcc - np.mean(mfcc)) / np.std(mfcc)
        
        # Padding atau cropping
        if mfcc.shape[1] < max_len:
            pad_width = max_len - mfcc.shape[1]
            mfcc = np.pad(mfcc, ((0, 0), (0, pad_width)), mode='constant')
        else:
            mfcc = mfcc[:, :max_len]
            
        return mfcc
    except Exception as e:
        print(f"Error extracting audio from {video_path}: {str(e)}")
        return None

def extract_all_audio_features(video_paths, n_mfcc=40, max_len=64):
    """
    Ekstraksi fitur audio dari semua video
    
    Args:
        video_paths (list): Daftar path video
        n_mfcc (int): Jumlah koefisien MFCC
        max_len (int): Panjang maksimum fitur
        
    Returns:
        np.array: Array fitur audio
    """
    all_features = []
    
    for path in tqdm(video_paths, desc="Extracting audio features"):
        features = extract_audio_features(path, n_mfcc, max_len)
        if features is not None:
            all_features.append(features)
    
    return np.array(all_features)

if __name__ == "__main__":

    import pandas as pd
    
    # Ambil beberapa video yang sudah diunduh
    train_df = pd.read_csv('../data/train_parsed.csv')
    video_paths = [f"../data/raw_videos/{id}.mp4" for id in train_df['id'].head(500)]
    
    # Ekstraksi fitur audio
    audio_features = extract_all_audio_features(video_paths)
    
    print(f"\nShape fitur audio: {audio_features.shape}")
    # Output: (5, 40, 64) - [batch, n_mfcc, max_len]