# src/utils.py
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import tensorflow as tf

def load_data():
    # Dapatkan path absolut
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    # Cek apakah data sudah diproses
    visual_path = os.path.join(project_root, 'data', 'visual_features.npy')
    audio_path = os.path.join(project_root, 'data', 'audio_features.npy')
    labels_path = os.path.join(project_root, 'data', 'labels.npy')
    if (os.path.exists(visual_path) and os.path.exists(audio_path) and os.path.exists(labels_path)):
        print("Memuat data yang sudah diproses...")
        visual_data = np.load(visual_path)
        audio_data = np.load(audio_path)
        labels = np.load(labels_path)
        return visual_data, audio_data, labels
    # Jika belum, proses data

    print("Memproses data train...")
    # Muat data yang sudah diparse
    train_parsed_path = os.path.join(project_root, 'data', 'train_parsed.csv')
    if not os.path.exists(train_parsed_path):
        print(f"ERROR: File train_parsed.csv tidak ditemukan di {train_parsed_path}")
        print("Jalankan data_parser.py terlebih dahulu")
        return None, None, None
    train_df = pd.read_csv(train_parsed_path)
    # Mapping emosi ke angka
    emotion_to_num = {
        'Proud': 0,
        'Trust': 1,
        'Joy': 2,
        'Surprise': 3,
        'Fear': 4,
        'Sadness': 5,
        'Disgust': 6,
        'Anger': 7
    }
    # Ekstraksi fitur visual
    from .feature_extraction.visual_features import extract_all_visual_features
    print("Mengekstraksi fitur visual...")
    video_paths = []
    for _, row in train_df.iterrows():
        # Dalam implementasi nyata, unduh video dan simpan path-nya
        # Untuk contoh ini, kita asumsikan video sudah diunduh
        video_id = row['id']
        video_path = os.path.join(project_root, 'data', 'raw_videos', f"{video_id}.mp4")
        if os.path.exists(video_path):
            video_paths.append(video_path)
    visual_data = extract_all_visual_features(video_paths)

    # Ekstraksi fitur audio
    from .feature_extraction.audio_features import extract_all_audio_features
    print("Mengekstraksi fitur audio...")
    audio_data = extract_all_audio_features(video_paths)

    # Simpan label
    labels = []
    for _, row in train_df.iterrows():
        emotion = row['emotion']
        if emotion in emotion_to_num:
            labels.append(emotion_to_num[emotion])
        # Abaikan label yang tidak valid sesuai aturan kompetisi
    labels = np.array(labels)[:len(visual_data)]  # Pastikan ukuran sesuai
    # Simpan data yang diproses
    np.save(visual_path, visual_data)
    np.save(audio_path, audio_data)
    np.save(labels_path, labels)

    return visual_data, audio_data, labels

def load_label_encoder():
    """Muat label encoder"""
    # Dapatkan path absolut
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    classes_path = os.path.join(project_root, 'outputs', 'models', 'label_encoder_classes.npy')
    if not os.path.exists(classes_path):
        # Buat label encoder default jika file tidak ada
        classes = np.array(['Proud', 'Trust', 'Joy', 'Surprise', 'Fear', 'Sadness', 'Disgust', 'Anger'])
        return type('LabelEncoder', (), {
            'classes_': classes,
            'transform': lambda self, x: [np.where(self.classes_ == item)[0][0] for item in x],
            'inverse_transform': lambda self, x: [self.classes_[i] for i in x]
        })()
    classes = np.load(classes_path, allow_pickle=True)
    return type('LabelEncoder', (), {
        'classes_': classes,
        'transform': lambda self, x: [np.where(self.classes_ == item)[0][0] for item in x],
        'inverse_transform': lambda self, x: [self.classes_[i] for i in x]
    })()

if __name__ == "__main__":
    # Contoh penggunaan
    visual_data, audio_data, labels = load_data()
    if visual_data is not None:
        print(f"Shape visual data: {visual_data.shape}")
        print(f"Shape audio data: {audio_data.shape}")
        print(f"Jumlah label: {len(labels)}")
        print(f"Distribusi label: {np.unique(labels, return_counts=True)}")