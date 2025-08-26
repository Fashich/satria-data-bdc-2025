from confluent_kafka import Consumer
import json
import time
import numpy as np
from tensorflow.keras.models import load_model

from ..feature_extraction.visual_features import extract_frames
from ..feature_extraction.audio_features import extract_audio_features
from ..utils import load_label_encoder

def process_message(message, model, label_encoder):
    """
    Proses pesan dari Kafka dan lakukan prediksi
    
    Args:
        message (dict): Pesan dari Kafka
        model: Model prediksi
        label_encoder: Label encoder
    """
    video_url = message['video_url']
    print(f"\nMenerima video baru: {video_url}")
    
    # Unduh video (dalam implementasi nyata, ini sudah diunduh sebelumnya)
    # video_path = download_video(video_url)
    # Untuk simulasi, kita asumsikan video sudah ada
    video_path = f"../data/raw_videos/{video_url.split('/')[-2]}.mp4"
    
    if not video_path or not os.path.exists(video_path):
        print(f"  Gagal mengunduh video")
        return
    
    # Ekstraksi fitur
    visual_features = extract_frames(video_path)
    audio_features = extract_audio_features(video_path)
    
    if visual_features is None or audio_features is None:
        print(f"  Gagal ekstraksi fitur")
        return
    
    # Prediksi
    visual_features = np.expand_dims(visual_features, axis=0)
    audio_features = np.expand_dims(audio_features, axis=0)
    
    pred = model.predict(
        {'visual_input': visual_features, 'audio_input': audio_features},
        verbose=0
    )
    
    pred_class = np.argmax(pred, axis=1)[0]
    emotion = label_encoder.classes_[pred_class]
    
    print(f"  Prediksi: {emotion} (kelas {pred_class}) dengan confidence {np.max(pred):.2f}")

def start_consumer():
    """Mulai consumer Kafka"""
    # Konfigurasi Kafka
    kafka_config = {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'emotion-detection-group',
        'auto.offset.reset': 'earliest'
    }
    
    # Muat model
    model = load_model('../outputs/models/emotion_model_final.h5')
    label_encoder = load_label_encoder()
    
    consumer = Consumer(kafka_config)
    consumer.subscribe(['video-input-topic'])
    
    print("Consumer siap menerima pesan...")
    
    try:
        while True:
            msg = consumer.poll(1.0)
            
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            
            # Proses pesan
            try:
                data = json.loads(msg.value().decode('utf-8'))
                process_message(data, model, label_encoder)
            except Exception as e:
                print(f"Error processing message: {str(e)}")
                
    except KeyboardInterrupt:
        print("Stopping consumer...")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_consumer()