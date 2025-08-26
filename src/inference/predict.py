# src/inference/predict.py
import os
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import openpyxl

from ..data_preparation.data_parser import parse_data_csv
from ..data_preparation.video_downloader import download_video
from ..feature_extraction.visual_features import extract_frames
from ..feature_extraction.audio_features import extract_audio_features
from ..utils import load_label_encoder

def predict_test_data():
    """Prediksi data test dan buat file submission"""
    # 1. Muat data test yang sudah diparse
    print("Memuat data test yang sudah diparse...")
    test_parsed_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'test_parsed.csv')
    if not os.path.exists(test_parsed_path):
        print(f"ERROR: File test_parsed.csv tidak ditemukan di {test_parsed_path}")
        print("Jalankan data_parser.py terlebih dahulu")
        return None
    test_df = pd.read_csv(test_parsed_path)
    print(f"Jumlah data test yang akan diproses: {len(test_df)}")
    
    # 2. Muat model
    print("Memuat model...")
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'outputs', 'models', 'emotion_model_final.h5')
    if not os.path.exists(model_path):
        print(f"ERROR: Model tidak ditemukan di {model_path}")
        print("Jalankan pelatihan model terlebih dahulu")
        return None
    model = load_model(model_path)
    label_encoder = load_label_encoder()
    
    # 3. Mapping emosi ke angka sesuai aturan kompetisi
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
    # 4. Prediksi untuk setiap video
    predictions = []
    
    for idx, row in test_df.iterrows():
        print(f"\nMemproses video {idx+1}/{len(test_df)}: ID {row['id']}")
        
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
        # Konversi ke format numerik sesuai aturan kompetisi
        # Pastikan kita mengembalikan angka sesuai mapping
        emotion_name = label_encoder.classes_[pred_class]
        if emotion_name in emotion_to_num:
            pred_num = emotion_to_num[emotion_name]
        else:
            # Jika emosi tidak sesuai, gunakan Surprise sebagai fallback
            pred_num = 3
        predictions.append(pred_num)
        
        # Cleanup video
        if os.path.exists(video_path):
            os.remove(video_path)
    
    # 5. Buat submission file dalam format yang benar
    submission = pd.DataFrame({
        'id': test_df['id'],
        'predicted': predictions
    })
    
    # Pastikan urutan sesuai dengan data test asli
    submission = submission.sort_values('id')
    # Simpan ke CSV
    outputs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'outputs', 'submissions')
    os.makedirs(outputs_dir, exist_ok=True)
    csv_path = os.path.join(outputs_dir, 'submission.csv')
    submission.to_csv(csv_path, index=False)
    print(f"\nFile submission CSV berhasil dibuat di {csv_path}")
    # Simpan ke Excel
    excel_path = os.path.join(outputs_dir, 'submission.xlsx')
    submission.to_excel(excel_path, index=False)
    print(f"File submission Excel berhasil dibuat di {excel_path}")
    
    # Tampilkan contoh hasil
    print("\n5 Prediksi pertama:")
    print(submission.head())
    
    return submission

if __name__ == "__main__":
    predict_test_data()