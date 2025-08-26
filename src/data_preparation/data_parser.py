"""
Script untuk mem-parse file CSV yang diberikan.
Karena format datanya tidak standar, kita perlu script khusus.
"""
import pandas as pd
import re
import os

def parse_data_csv(file_path):
    """
    Parse file CSV dengan format khusus yang diberikan.
    
    Args:
        file_path (str): Path ke file CSV
        
    Returns:
        pd.DataFrame: DataFrame dengan kolom id, video_url, emotion
    """
    # Pastikan file ada
    if not os.path.exists(file_path):
        print(f"ERROR: File tidak ditemukan di {os.path.abspath(file_path)}")
        return pd.DataFrame(columns=['id', 'video_url', 'emotion'])
    
    # Membaca semua baris sebagai teks
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Siapkan list untuk menyimpan data
    data = []
    
    # Daftar emosi yang valid
    valid_emotions = ['Proud', 'Trust', 'Joy', 'Surprise', 'Fear', 'Sadness', 'Disgust', 'Anger', 'Neutral']
    
    # Proses setiap baris
    for line_num, line in enumerate(lines[1:], 1):  # Lewati header dan lacak nomor baris
        # Hapus karakter aneh dan split
        parts = [p.strip() for p in line.split(',') if p.strip()]
        
        # Cari pasangan URL dan label
        i = 0
        while i < len(parts):
            # Cek apakah bagian saat ini mengandung URL
            if 'http' in parts[i] or 'www.instagram.com' in parts[i] or 'drive.google.com' in parts[i]:
                url = parts[i]
                
                # Cari ID sebelum URL (biasanya ada di bagian sebelumnya)
                video_id = f"video_{line_num}_{i}"
                if i > 0:
                    # Cari ID yang terlihat seperti angka atau string pendek
                    potential_id = parts[i-1]
                    if re.match(r'^[\w-]+$', potential_id) and len(potential_id) < 20:
                        video_id = potential_id
                
                # Cari label setelah URL
                emotion = None
                if i + 1 < len(parts):
                    label_text = parts[i + 1]
                    
                    # Cek semua emosi valid
                    for emo in valid_emotions:
                        if emo in label_text:
                            emotion = emo
                            break
                    
                    # Handle kasus typo atau variasi
                    if not emotion:
                        if 'Terkjut' in label_text or 'Trkejut' in label_text or 'Kaget' in label_text:
                            emotion = 'Surprise'
                        elif 'Bangga' in label_text:
                            emotion = 'Proud'
                        elif 'Trek' in label_text:
                            emotion = 'Surprise'
                
                # Simpan data jika emosi valid
                if emotion:
                    data.append({
                        'id': video_id,
                        'video_url': url,
                        'emotion': emotion
                    })
                
                i += 2
            else:
                i += 1
    
    if not data:
        print("PERINGATAN: Tidak ada data yang berhasil diparse. Periksa format file CSV.")
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Dapatkan path absolut ke file CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    train_path = os.path.join(project_root, 'data', 'datatrain.csv')
    test_path = os.path.join(project_root, 'data', 'datatest.csv')
    
    print(f"Path absolut ke datatrain.csv: {train_path}")
    print(f"Path absolut ke datatest.csv: {test_path}")
    
    # Pastikan file ada
    if not os.path.exists(train_path):
        print(f"ERROR: File datatrain.csv tidak ditemukan di {train_path}")
        print("Pastikan file CSV ditempatkan di folder data/")
    else:
        # Contoh penggunaan
        train_df = parse_data_csv(train_path)
        print(f"\nJumlah data train yang berhasil diparse: {len(train_df)}")
        if not train_df.empty:
            print("Distribusi emosi:")
            print(train_df['emotion'].value_counts())
            
            # Simpan hasil parsing
            output_path = os.path.join(project_root, 'data', 'train_parsed.csv')
            train_df.to_csv(output_path, index=False)
            print(f"Hasil parsing disimpan di: {output_path}")
        else:
            print("Tidak ada data train yang berhasil diparse.")
    
    # Lakukan hal yang sama untuk data test
    if not os.path.exists(test_path):
        print(f"ERROR: File datatest.csv tidak ditemukan di {test_path}")
    else:
        test_df = parse_data_csv(test_path)
        print(f"\nJumlah data test yang berhasil diparse: {len(test_df)}")
        if not test_df.empty:
            output_path = os.path.join(project_root, 'data', 'test_parsed.csv')
            test_df.to_csv(output_path, index=False)
            print(f"Hasil parsing disimpan di: {output_path}")
        else:
            print("Tidak ada data test yang berhasil diparse.")