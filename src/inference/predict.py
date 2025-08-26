import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

from ..data_preparation.data_parser import parse_data_csv
from ..data_preparation.video_downloader import download_video
from ..feature_extraction.visual_features import extract_frames
from ..feature_extraction.audio_features import extract_audio_features
from ..utils import load_label_encoder

def predict_test_data():
    """Prediksi data test dan buat file submission"""
    # 1. Muat data test
    print("Memuat dan mem-parse data test...")
    test_df = parse_data_csv('../data/datatest.csv')
    test_df.to_csv('../data/test_parsed.csv', index=False)
    
    # 2. Muat model
    print("Memuat model...")
    model = load_model('../outputs/models/emotion_model_final.h5')
    label_encoder = load_label_encoder()
    
    # 3. Prediksi untuk setiap video
    predictions = []
    
    for idx, row in test_df.iterrows():
        print(f"\nMemproses video {idx+1}/{len(test_df)}: {row['id']}")
        
        # Unduh video
        video_path = download_video(row['video_url'])
        if not video_path or not os.path.exists(video_path):
            print(f"  Gagal mengunduh video, menggunakan fallback (Surprise)")
            predictions.append(3)  # Surprise sebagai fallback
            continue
        
        # Ekstraksi fitur visual
        visual_features = extract_frames(video_path)
        if visual_features is None:
            print(f"  Gagal ekstraksi fitur visual, menggunakan fallback (Surprise)")
            predictions.append(3)
            continue
            
        # Ekstraksi fitur audio
        audio_features = extract_audio_features(video_path)
        if audio_features is None:
            print(f"  Gagal ekstraksi fitur audio, menggunakan fallback (Surprise)")
            predictions.append(3)
            continue
        
        # Prediksi
        visual_features = np.expand_dims(visual_features, axis=0)
        audio_features = np.expand_dims(audio_features, axis=0)
        
        pred = model.predict(
            {'visual_input': visual_features, 'audio_input': audio_features},
            verbose=0
        )
        
        pred_class = np.argmax(pred, axis=1)[0]
        predictions.append(pred_class)
        
        # Cleanup video
        if os.path.exists(video_path):
            os.remove(video_path)
    
    # 4. Buat submission file
    submission = pd.DataFrame({
        'id': test_df['id'],
        'predicted': predictions
    })
    
    os.makedirs('../outputs/submissions', exist_ok=True)
    submission_path = '../outputs/submissions/submission.csv'
    submission.to_csv(submission_path, index=False)
    
    print(f"\nFile submission berhasil dibuat di {submission_path}")
    print("5 prediksi pertama:")
    print(submission.head())
    
    return submission

if __name__ == "__main__":
    predict_test_data()