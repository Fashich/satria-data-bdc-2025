# src/data_preparation/video_downloader.py
import os
import argparse
import pandas as pd
from tqdm import tqdm
import yt_dlp

def download_video(url, output_path=None):
    """
    Unduh video dari URL yang diberikan

    Args:
        url (str): URL video
        output_path (str, optional): Path untuk menyimpan video. Defaults to None.

    Returns:
        str: Path ke file video yang diunduh atau None jika gagal
    """
    if not url or 'http' not in url:
        return None

    # Pastikan direktori output ada
    if output_path and not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    # Konfigurasi yt-dlp
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path if output_path else 'video.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'nocheckcertificate': True,
        'retries': 3,
        'fragment-retries': 10,
        'continuedl': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if output_path:
                return output_path % {'id': info.get('id', 'video')}
            else:
                return ydl.prepare_filename(info)
    except Exception as e:
        print(f"  Gagal mengunduh {url}: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Unduh video dari dataset')
    parser.add_argument('--max-videos', type=int, default=5, help='Jumlah maksimum video yang akan diunduh')
    parser.add_argument('--test-data', action='store_true', help='Unduh data test (default: data train)')
    args = parser.parse_args()

    # Tentukan path file CSV yang akan diparse
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir = os.path.join(project_root, 'data')

    # Tentukan file CSV berdasarkan apakah ini data test atau train
    if args.test_data:
        csv_path = os.path.join(data_dir, 'test_parsed.csv')
        output_dir = os.path.join(data_dir, 'test_videos')
        print("Mengunduh data test...")
    else:
        csv_path = os.path.join(data_dir, 'train_parsed.csv')
        output_dir = os.path.join(data_dir, 'train_videos')
        print("Mengunduh data train...")

    # Pastikan file CSV ada
    if not os.path.exists(csv_path):
        print(f"ERROR: File {csv_path} tidak ditemukan. Jalankan data_parser.py terlebih dahulu.")
        return

    # Muat data
    df = pd.read_csv(csv_path)
    print(f"Jumlah data yang ditemukan: {len(df)}")

    # Batasi jumlah video yang diunduh
    max_videos = min(args.max_videos, len(df))
    print(f"Mengunduh {max_videos} dari {len(df)} video...")

    # Buat direktori output jika belum ada
    os.makedirs(output_dir, exist_ok=True)

    # Unduh video
    failed_downloads = 0
    for i, row in tqdm(df.head(max_videos).iterrows(), total=max_videos):
        video_id = row['id']
        url = row['video_url']

        # Tentukan path output
        output_path = os.path.join(output_dir, f"{video_id}.%(ext)s")

        # Unduh video
        video_path = download_video(url, output_path)
        if not video_path or not os.path.exists(video_path):
            failed_downloads += 1

    # Tampilkan ringkasan
    print(f"\nProses unduh selesai!")
    print(f"Berhasil: {max_videos - failed_downloads}")
    print(f"Gagal: {failed_downloads}")
    print(f"Total: {max_videos}")
    print(f"Video disimpan di: {output_dir}")

if __name__ == "__main__":
    main()