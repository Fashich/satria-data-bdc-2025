import os
import numpy as np
import pandas as pd
from tqdm import tqdm

def load_data():

    # Cek apakah data sudah diproses
    if (os.path.exists('../data/visual_features.npy') and 
        os.path.exists('../data/audio_features.npy') and
        os.path.exists('../data/labels.npy')):
        
        print("Memuat data yang sudah diproses...")
        visual_data = np.load('../data/visual_features.npy')
        audio_data = np.load('../data/audio_features.npy')
        labels = np.load('../data/labels.npy')
        
        return visual_data, audio_data, labels
    
    # Jika belum, proses data
    print("Memproses data train...")
    train_df = pd.read_csv('../data/train_parsed.csv')
    
    # Unduh video
    video_paths = []
    for url in tqdm(train_df['video_url'], desc="Mengunduh video"):
        path = f"../data/raw_videos/{train_df['id'][0]}.mp4"  # Simplified for example
        # Di implementasi nyata, gunakan video_downloader.download_video(url)
        if os.path.exists(path):
            video_paths.append(path)
    
    # Ekstraksi fitur visual
    from .feature_extraction.visual_features import extract_all_visual_features
    visual_data = extract_all_visual_features(video_paths)
    
    # Ekstraksi fitur audio
    from .feature_extraction.audio_features import extract_all_audio_features
    audio_data = extract_all_audio_features(video_paths)
    
    # Simpan label
    labels = train_df['emotion'].values[:len(visual_data)]
    
    # Simpan data yang diproses
    np.save('../data/visual_features.npy', visual_data)
    np.save('../data/audio_features.npy', audio_data)
    np.save('../data/labels.npy', labels)
    
    return visual_data, audio_data, labels

def load_label_encoder():
    """Muat label encoder"""
    classes = np.load('../outputs/models/label_encoder_classes.npy', allow_pickle=True)
    
    class LabelEncoderMock:
        def __init__(self, classes):
            self.classes_ = classes
            
        def inverse_transform(self, y):
            return np.array([self.classes_[i] for i in y])
            
    return LabelEncoderMock(classes)

if __name__ == "__main__":
    visual_data, audio_data, labels = load_data()
    print(f"Shape visual data: {visual_data.shape}")
    print(f"Shape audio data: {audio_data.shape}")
    print(f"Jumlah label: {len(labels)}")
    print(f"Distribusi label: {np.unique(labels, return_counts=True)}")