# Aplikasi Pemantauan Gas Rumah Kaca Jakarta

## Deskripsi
Aplikasi GUI berbasis Python untuk memantau CO₂ & CH₄ di Jakarta menggunakan data Open-Meteo.
Menampilkan:
- Dashboard Realtime (Hari ini)
- Proyeksi Beberapa Jam Kedepan
- Data Periode (maksimal 7 hari terakhir)
- KPI dan status kualitas udara

## Instalasi

1. Clone repository:
```bash
git clone https://github.com/username/GrkApp.git

2. Masuk ke folder proyek:
```bash
cd GrkApp

3. Install dependensi:
```bash
pip install -r requirements.txt


## Menjalankan Aplikasi
```bash
python gui11.py


Ambang Batas CO₂ & CH₄ (Luar Ruangan)
Gas	Normal	Waspada	Tinggi
CO₂	< 450 ppm	450 – 500 ppm	> 500 ppm
CH₄	< 1950 ppb	1950 – 2000 ppb	> 2000 ppb

Sumber: Global Carbon Project, WMO

Referensi
Open-Meteo API
Global Carbon Project
