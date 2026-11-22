# WORKING_PATH.md — Peta Kerja & Checklist Proyek

> **Aturan Agen**: Setiap agen yang bekerja di proyek ini **WAJIB** membaca `PROGRESION.md` dan `WORKING_PATH.md` terlebih dahulu, lalu mencatat setiap sesi prompt (tanggal, jam WIB, input, output, serta perubahan file/program) di `PROGRESION.md` dan memperbarui status ceklis di file ini.

---

## Struktur Direktori Target

```text
proyek_machine_learning/
├── PROGRESION.md          # Notulensi wajib tiap sesi (input, output, changelog, timestamp)
├── WORKING_PATH.md        # Peta kerja & checklist progres (file ini)
├── data/
│   ├── raw/               # Data mentah hasil scraping/download (FCPO, ZL=F, BZ=F, MYR=X, IDR=X)
│   └── processed/         # Data bersih, aligned, log-return, & label rezim pasar
├── src/
│   └── scrape_data.py     # Skrip akuisisi data Yahoo Finance & Investing.com
├── notebooks/             # Eksplorasi (EDA) & visualisasi
└── outputs/               # Model, metrik evaluasi, grafik, & hasil SHAP
```

---

## Checklist Progres Proyek

### Tahap 0 — Akuisisi & Verifikasi Data
- [x] Inisialisasi dokumentasi `PROGRESION.md` & `WORKING_PATH.md`
- [x] Buat skrip akuisisi data (`src/scrape_data.py`)
- [x] Unduh / scraping data `ZL=F` (Soybean Oil Futures) ke `data/raw/` (`zl_soybean_oil.csv`: 6.635 baris, `2000-03-15` s.d. `2026-11-20`)
- [x] Unduh / scraping data `BZ=F` (Brent Crude Oil Futures) ke `data/raw/` (`bz_brent_crude.csv`: 4.809 baris, `2007-07-30` s.d. `2026-11-20`)
- [x] Unduh / scraping data `MYR=X` (Kurs USD/MYR) ke `data/raw/` (`myr_usd.csv`: 5.982 baris, `2003-12-01` s.d. `2026-11-22`)
- [x] Unduh / scraping data `IDR=X` (Kurs USD/IDR) ke `data/raw/` (`idr_usd.csv`: 6.416 baris, `2001-06-28` s.d. `2026-11-22`)
- [x] Unduh / scraping data FCPO (Investing.com: `https://share.google/Zjl2F9L7QktfnB4e0`) ke `data/raw/` (`fcpo_investing.csv`: 2.913 baris, `2014-08-18` s.d. `2026-11-20`)
- [x] Verifikasi rentang tanggal (minimal 5–10 tahun), kelengkapan kolom, dan *missing values* (semua 5 dataset mencakup penuh rentang `2014-08-18` s.d. `2026-11-20`)

### Tahap 1 — Data Alignment, EDA, & Rezim Pasar
- [x] Penyelarasan kalender perdagangan (acuan hari bursa FCPO) (`src/prepare_dataset.py`)
- [x] Penanganan timezone & *lagging* variabel eksternal (bebas *look-ahead bias*) (`shift(1)` untuk seluruh variabel eksternal)
- [x] Transformasi target menjadi *log-return* / `% change` (`target_ret_h1`, `target_ret_h5`, `target_ret_h20`)
- [x] Identifikasi & pelabelan rezim pasar (Rolling Volatility / *expanding median* bebas *future leakage*)
- [x] Simpan dataset siap latih ke `data/processed/` (`data/processed/dataset_aligned.csv`: 2.913 baris x 43 kolom)

### Tahap 2 — Kerangka Walk-Forward & Baseline
- [ ] Implementasi *walk-forward validation* (expanding/sliding window tanpa *data leakage*)
- [ ] Implementasi baseline **Naive / Random Walk**
- [ ] Implementasi baseline pembanding (opsional: Ridge / ARIMA)

### Tahap 3 — Modeling Multi-Horizon (`h = 1, 5, 20`)
- [ ] Model **XGBoost** (*Internal Only* & *Internal + Eksternal*)
- [ ] Model **LSTM** (*Internal Only* & *Internal + Eksternal*)
- [ ] Rekonstruksi prediksi *return* ke skala harga untuk metrik evaluasi harga

### Tahap 4 — Evaluasi Multi-Aspek & Interpretabilitas
- [ ] Perbandingan metrik (RMSE, MAE, MAPE, Directional Accuracy) per horizon
- [ ] *Regime-Aware Evaluation* (performa saat *low volatility* vs *high volatility*)
- [ ] *Ablation Study* (kontribusi variabel eksternal)
- [ ] Analisis SHAP untuk interpretabilitas fitur XGBoost
- [ ] Finalisasi laporan & ringkasan temuan

