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
echo 2. Mengunduh video (contoh 10 video pertama)...
python -m src.data_preparation.video_downloader --max-videos 10

echo.
echo 3. Melatih model...
python -m src.training.train

echo.
echo 4. Membuat prediksi untuk data test...
python -m src.inference.predict

echo.
echo 5. Menjalankan simulasi real-time (consumer)...
echo Silakan buka terminal baru dan jalankan: python -m src.real_time.kafka_producer
echo Untuk menghentikan consumer, tekan CTRL+C
python -m src.real_time.kafka_consumer

echo.
echo ===== PIPELINE SELESAI =====
pause