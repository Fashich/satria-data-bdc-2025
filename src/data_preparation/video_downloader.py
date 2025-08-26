"""
Script untuk mengunduh video dari berbagai sumber (Google Drive, Instagram)
"""
import os
import re
import yt_dlp
import argparse
from tqdm import tqdm
import time
import pandas as pd
import sys

def download_video(url, output_path=None):
    """
    Download video dari berbagai sumber
    
    Args:
        url (str): URL video
        output_path (str, optional): Path output file
        
    Returns:
        str: Path ke file video yang diunduh, atau None jika gagal
    """
    if output_path is None:
        # Buat nama file berdasarkan URL
        video_id = re.search(r'[a-zA-Z0-9_-]{11,}', url)
        if video_id:
            output_path = f"../data/raw_videos/{video_id.group()}.mp4"
        else:
            output_path = f"../data/raw_videos/video_{int(time.time())}.mp4"
    
    # Pastikan direktori output ada
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Konfigurasi yt-dlp
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'quiet': False,  # Set ke False untuk melihat progress
        'no_warnings': False,
        'retries': 3,
        'fragment-retries': 5,
        'extractor-retries': 3,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return output_path
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}", file=sys.stderr)
        return None

def download_all_videos(df, max_videos=None):
    """
    Download semua video dalam DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame dengan kolom 'video_url'
        max_videos (int, optional): Batas jumlah video yang diunduh
        
    Returns:
        list: Daftar path ke file video yang berhasil diunduh
    """
    video_paths = []
    
    # Batasi jumlah video jika diperlukan
    videos = df['video_url'].head(max_videos) if max_videos else df['video_url']
    
    for url in tqdm(videos, desc="Downloading videos"):
        path = download_video(url)
        if path:
            video_paths.append(path)
    
    return video_paths

if __name__ == "__main__":
    # Dapatkan path absolut
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    
    # Parse argumen
    parser = argparse.ArgumentParser()
    parser.add_argument('--max-videos', type=int, default=None, help='Maksimal jumlah video yang diunduh')
    args = parser.parse_args()
    
    # Pastikan folder raw_videos ada
    raw_videos_dir = os.path.join(project_root, 'data', 'raw_videos')
    os.makedirs(raw_videos_dir, exist_ok=True)
    
    # Muat data yang sudah diparse
    train_parsed_path = os.path.join(project_root, 'data', 'train_parsed.csv')
    
    if not os.path.exists(train_parsed_path):
        print(f"ERROR: File train_parsed.csv tidak ditemukan di {train_parsed_path}")
        print("Jalankan data_parser.py terlebih dahulu")
        sys.exit(1)
    
    train_df = pd.read_csv(train_parsed_path)
    
    print(f"Menemukan {len(train_df)} video dalam dataset")
    if args.max_videos:
        print(f"Mengunduh {args.max_videos} video pertama")
    else:
        print("Mengunduh semua video")
    
    # Unduh video
    downloaded_videos = download_all_videos(train_df, max_videos=args.max_videos)
    
    print(f"\nBerhasil mengunduh {len(downloaded_videos)} video")
    print(f"Video disimpan di: {raw_videos_dir}")