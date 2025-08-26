from confluent_kafka import Producer
import json
import time
import pandas as pd
from tqdm import tqdm

def delivery_report(err, msg):

    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}]')

def start_producer(video_urls, topic='video-input-topic'):

    # Konfigurasi Kafka
    kafka_config = {
        'bootstrap.servers': 'localhost:9092',
        'client.id': 'video-producer'
    }
    
    producer = Producer(kafka_config)
    
    print(f"Memulai producer untuk {len(video_urls)} video...")
    
    for url in tqdm(video_urls, desc="Mengirim pesan ke Kafka"):
        # Buat pesan
        message = {
            'video_url': url,
            'timestamp': time.time()
        }
        
        # Kirim ke Kafka
        producer.produce(
            topic,
            json.dumps(message).encode('utf-8'),
            callback=delivery_report
        )
        
        # Flush setiap 10 pesan
        producer.poll(0)
        
        # Tambahkan delay untuk simulasi aliran data
        time.sleep(0.5)
    
    # Tunggu semua pesan terkirim
    producer.flush()
    print("Semua pesan telah dikirim")

if __name__ == "__main__":
    test_df = pd.read_csv('../data/test_parsed.csv')
    sample_urls = test_df['video_url'].head(500).tolist()
    
    start_producer(sample_urls)