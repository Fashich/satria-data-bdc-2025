# src/data_preparation/data_parser.py
import pandas as pd
import re
import os

def parse_data_csv(file_path, is_test=False):
    """
    Parse file CSV dengan format khusus yang diberikan oleh Satria Data.
    Format data sangat tidak standar: [ID,URL,LabelID,URL,Label...] untuk train
    dan [ID,URL,ID,URL,...] untuk test

    Args:
        file_path (str): Path ke file CSV
        is_test (bool): True jika parsing data test (tanpa label emosi)

    Returns:
        pd.DataFrame: DataFrame dengan kolom id, video_url, dan emotion (jika train)
    """
    # Pastikan file ada
    if not os.path.exists(file_path):
        print(f"ERROR: File tidak ditemukan di {os.path.abspath(file_path)}")
        return pd.DataFrame(columns=['id', 'video_url', 'emotion'] if not is_test else ['id', 'video_url'])

    # Daftar emosi yang valid sesuai deskripsi soal
    valid_emotions = {
        'Proud': 0,
        'Trust': 1,
        'Joy': 2,
        'Surprise': 3,
        'Fear': 4,
        'Sadness': 5,
        'Disgust': 6,
        'Anger': 7,
        'Terkjut': 3,   # Koreksi typo untuk Surprise
        'Trkejut': 3,   # Koreksi typo untuk Surprise
        'Trekejut': 3,  # Koreksi typo untuk Surprise
        'Bangga': 0,    # Koreksi untuk Proud
        'Sad': 5,       # Koreksi untuk Sadness
        'Kaget': 3,     # Koreksi untuk Surprise
        'Marah': 7,     # Koreksi untuk Anger
        'Takut': 4      # Koreksi untuk Fear
    }

    # Siapkan list untuk menyimpan data
    data = []

    # Membaca semua baris sebagai teks
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Proses setiap baris (lewati header)
    for line_num, line in enumerate(lines[1:], 1):
        # Hapus karakter aneh dan split
        parts = [p.strip() for p in line.split(',') if p.strip()]

        i = 0
        while i < len(parts):
            # Cari ID
            id_match = re.search(r'^(\d+)', parts[i])
            if id_match:
                video_id = id_match.group(1)
                i += 1
            else:
                # Coba cari ID di bagian tengah string
                id_in_text = re.search(r'(\d+)$', parts[i])
                if id_in_text:
                    video_id = id_in_text.group(1)
                    # Hapus ID dari teks
                    parts[i] = re.sub(r'\d+$', '', parts[i])
                else:
                    video_id = f"video_{line_num}_{i}"

            # Cari URL
            url = None
            while i < len(parts):
                if 'http' in parts[i] or 'www.instagram.com' in parts[i] or 'drive.google.com' in parts[i]:
                    url = parts[i]
                    i += 1
                    break
                i += 1

            if not url:
                break

            # Untuk data train, cari label emosi
            emotion = None
            if not is_test and i < len(parts):
                # Cek semua kemungkinan label
                for emo in valid_emotions.keys():
                    if emo in parts[i]:
                        emotion = emo
                        break

                # Jika tidak ditemukan, cek kasus khusus
                if not emotion:
                    # Coba cari emosi di dalam teks
                    for emo in valid_emotions.keys():
                        if re.search(emo, parts[i], re.IGNORECASE):
                            emotion = emo
                            break

            # Simpan data
            if is_test:
                data.append({
                    'id': video_id,
                    'video_url': url
                })
            else:
                if emotion:
                    data.append({
                        'id': video_id,
                        'video_url': url,
                        'emotion': emotion
                    })

    return pd.DataFrame(data)

if __name__ == "__main__":
    # Dapatkan path absolut ke file CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    train_path = os.path.join(project_root, 'data', 'datatrain.csv')
    test_path = os.path.join(project_root, 'data', 'datatest.csv')

    # Parse data train
    if os.path.exists(train_path):
        train_df = parse_data_csv(train_path, is_test=False)
        print(f"\nJumlah data train yang berhasil diparse: {len(train_df)}")
        if not train_df.empty:
            print("Distribusi emosi:")
            print(train_df['emotion'].value_counts())

            # Simpan hasil parsing
            output_path = os.path.join(project_root, 'data', 'train_parsed.csv')
            train_df.to_csv(output_path, index=False)
            print(f"Hasil parsing train disimpan di: {output_path}")
        else:
            print("Tidak ada data train yang berhasil diparse.")

    # Parse data test
    if os.path.exists(test_path):
        test_df = parse_data_csv(test_path, is_test=True)
        print(f"\nJumlah data test yang berhasil diparse: {len(test_df)}")
        if not test_df.empty:
            output_path = os.path.join(project_root, 'data', 'test_parsed.csv')
            test_df.to_csv(output_path, index=False)
            print(f"Hasil parsing test disimpan di: {output_path}")
        else:
            print("Tidak ada data test yang berhasil diparse.")