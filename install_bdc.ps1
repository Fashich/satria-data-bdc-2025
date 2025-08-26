# BDC Satria Data 2025 - Instalasi Lengkap via PowerShell (REVISED)
# Simpan sebagai install_bdc_fixed.ps1 dan jalankan sebagai Administrator

# 1. Persiapan: Pastikan eksekusi script diizinkan
Set-ExecutionPolicy Bypass -Scope Process -Force

# Tambahkan TLS 1.2 untuk koneksi yang aman
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host "===== MEMULAI INSTALASI LENGKAP BDC Satria Data 2025 =====" -ForegroundColor Cyan

# 2. Instal Chocolatey (jika belum)
Write-Host "`n[1/5] Memeriksa/menginstal Chocolatey..." -ForegroundColor Yellow
if (-not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Chocolatey belum terinstal. Menginstal sekarang..."
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
} else {
    Write-Host "Chocolatey sudah terinstal."
}

# 3. Instal Python 3.11 dengan benar
Write-Host "`n[2/5] Menginstal Python 3.11..." -ForegroundColor Yellow
choco uninstall python --all -y
choco install python --version=3.11.10 -y --params="'/InstallDir:C:\Python311'" --no-progress

# Refresh environment
RefreshEnv
Write-Host "Memverifikasi instalasi Python 3.11..."
$pythonPath = (Get-Command python).Source
if ($pythonPath -like "*Python311*") {
    Write-Host "Python 3.11 berhasil diinstal di: $pythonPath" -ForegroundColor Green
} else {
    Write-Host "ERROR: Python 3.11 tidak terdeteksi dengan benar." -ForegroundColor Red
    Write-Host "Coba instal manual dari: https://www.python.org/downloads/release/python-31110/" -ForegroundColor Red
    exit 1
}

# 4. Instal FFmpeg untuk pemrosesan video
Write-Host "`n[3/5] Menginstal FFmpeg..." -ForegroundColor Yellow
choco install ffmpeg -y --no-progress

# Verifikasi FFmpeg
$ffmpegPath = (Get-Command ffmpeg).Source
if ($ffmpegPath) {
    Write-Host "FFmpeg berhasil diinstal di: $ffmpegPath" -ForegroundColor Green
} else {
    Write-Host "ERROR: FFmpeg tidak terinstal dengan benar." -ForegroundColor Red
    Write-Host "Coba instal manual dari: https://www.gyan.dev/ffmpeg/builds/" -ForegroundColor Red
    exit 1
}

# 5. Persiapkan environment Python
Write-Host "`n[4/5] Mempersiapkan virtual environment..." -ForegroundColor Yellow
$projectDir = (Get-Item -Path ".\" -Verbose).FullName
$venvPath = Join-Path $projectDir "bdc_env"

# Hapus virtual environment lama jika ada
if (Test-Path $venvPath) {
    Remove-Item -Recurse -Force $venvPath
}

# Buat virtual environment baru dengan Python 3.11
C:\Python311\python.exe -m venv $venvPath
$activateScript = Join-Path $venvPath "Scripts\activate.ps1"
. $activateScript

# Upgrade pip, setuptools, dan wheel
python -m pip install --upgrade pip setuptools wheel

# 6. Perbaiki requirements.txt untuk kompatibilitas
Write-Host "`n[5/5] Memperbaiki dependencies..." -ForegroundColor Yellow

# File requirements.txt yang sudah disesuaikan untuk Python 3.11
$requirements = @"
numpy==1.26.4
pandas==2.2.2
tensorflow==2.16.1
opencv-python==4.12.0.88
librosa==0.10.1
yt-dlp==2024.5.20
scikit-learn==1.4.2
tqdm==4.66.2
confluent-kafka==2.4.0
matplotlib==3.8.4
seaborn==0.13.2
openpyxl==3.1.3
"@

# Simpan ke requirements.txt
$requirementsPath = Join-Path $projectDir "requirements.txt"
$requirements | Out-File -FilePath $requirementsPath -Encoding utf8

# Instal dependencies
Write-Host "Menginstal dependencies dengan Python 3.11..."
pip install -r $requirementsPath

# 7. Perbaiki parser data yang tidak standar
Write-Host "`nMemperbaiki parser data untuk format CSV yang tidak standar..." -ForegroundColor Yellow

$dataPrepDir = Join-Path $projectDir "src\data_preparation"
if (-not (Test-Path $dataPrepDir)) {
    New-Item -ItemType Directory -Path $dataPrepDir | Out-Null
}

# File data_parser.py yang sudah diperbaiki
$dataParser = @"
# src/data_preparation/data_parser.py
import pandas as pd
import re
import os

def parse_data_csv(file_path):
    """
    Parse file CSV dengan format khusus yang diberikan oleh Satria Data.
    Format data sangat tidak standar: [ID,URL,LabelID,URL,Label...]
    
    Args:
        file_path (str): Path ke file CSV
        
    Returns:
        pd.DataFrame: DataFrame dengan kolom id, video_url, emotion
    """
    # Pastikan file ada
    if not os.path.exists(file_path):
        print(f"ERROR: File tidak ditemukan di {os.path.abspath(file_path)}")
        return pd.DataFrame(columns=['id', 'video_url', 'emotion'])
    
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
        'Neutral': 3    # Neutral dianggap Surprise (sesuai aturan kompetisi)
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
            
            # Cari label emosi
            emotion = None
            if i < len(parts):
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
            
            # Simpan data jika emosi valid
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
        train_df = parse_data_csv(train_path)
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
        test_df = parse_data_csv(test_path)
        print(f"\nJumlah data test yang berhasil diparse: {len(test_df)}")
        if not test_df.empty:
            output_path = os.path.join(project_root, 'data', 'test_parsed.csv')
            test_df.to_csv(output_path, index=False)
            print(f"Hasil parsing test disimpan di: {output_path}")
        else:
            print("Tidak ada data test yang berhasil diparse.")
"@

# Simpan ke data_parser.py
$parserPath = Join-Path $dataPrepDir "data_parser.py"
$dataParser | Out-File -FilePath $parserPath -Encoding utf8

# 8. Perbaiki run_pipeline.bat untuk Windows
Write-Host "Memperbaiki run_pipeline.bat..." -ForegroundColor Yellow

$runPipeline = @"
@echo off
echo ===== MEMULAI PIPELINE BDC Satria Data 2025 =====
echo Pastikan file datatrain.csv dan datatest.csv sudah ditempatkan di folder data/

REM Cek keberadaan file CSV
set "PROJECT_ROOT=%CD%"
set "TRAIN_PATH=%PROJECT_ROOT%\data\datatrain.csv"
set "TEST_PATH=%PROJECT_ROOT%\data\datatest.csv"

if not exist "%TRAIN_PATH%" (
    echo ERROR: File datatrain.csv tidak ditemukan di %TRAIN_PATH%
    echo Pastikan file CSV sudah ditempatkan di folder data/
    pause
    exit /b 1
)

if not exist "%TEST_PATH%" (
    echo ERROR: File datatest.csv tidak ditemukan di %TEST_PATH%
    echo Pastikan file CSV sudah ditempatkan di folder data/
    pause
    exit /b 1
)

echo 1. Mem-parse data CSV...
python -m src.data_preparation.data_parser

REM Cek apakah parsing berhasil
if not exist "%PROJECT_ROOT%\data\train_parsed.csv" (
    echo ERROR: Parsing data train gagal. Proses dihentikan.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\data\test_parsed.csv" (
    echo ERROR: Parsing data test gagal. Proses dihentikan.
    pause
    exit /b 1
)

echo.
echo 2. Mengunduh video (contoh 5 video pertama untuk pengujian)...
python -m src.data_preparation.video_downloader --max-videos 5

echo.
echo 3. Melatih model...
python -m src.training.train

echo.
echo 4. Membuat prediksi untuk data test...
python -m src.inference.predict

echo.
echo ===== PIPELINE SELESAI =====
echo File submission telah dibuat di outputs/submissions/
echo Format: submission.csv (CSV) dan submission.xlsx (Excel)
pause
"@

# Simpan ke run_pipeline.bat
$runPipelinePath = Join-Path $projectDir "run_pipeline.bat"
$runPipeline | Out-File -FilePath $runPipelinePath -Encoding utf8

# 9. Selesai
Write-Host "`n===== INSTALASI SELESAI =====" -ForegroundColor Green
Write-Host "Semua dependensi telah terinstal dan file yang diperlukan telah diperbaiki." -ForegroundColor Green
Write-Host "Untuk menjalankan pipeline, ketik: .\run_pipeline.bat" -ForegroundColor Green
Write-Host "Pastikan file datatrain.csv dan datatest.csv sudah ada di folder data/" -ForegroundColor Green