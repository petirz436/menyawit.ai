# PROGRESION.md — Proyek Prediksi Multi-Horizon Harga Minyak Sawit Berjangka

Catatan progres, notulensi prompt input/output, serta riwayat perubahan file dan program.

---

## Ringkasan Log Sesi

| No | Tanggal & Waktu | Topik / Aktivitas | Status |
| :--- | :--- | :--- | :--- |
| 1 | `2026-11-22 16:19 WIB` | Diskusi awal, validasi judul terhadap revisi dosen, & review/roast rencana skripsi | Selesai |
| 2 | `2026-11-22 16:21 WIB` | Perapihan format `PROGRESION.md` ke bentuk tabel | Selesai |
| 3 | `2026-11-22 16:29 WIB` | Pembuatan `WORKING_PATH.md`, struktur folder, & eksekusi `src/scrape_data.py` | Sebagian (Terblokir 403/429) |
| 4 | `2026-11-22 16:46 WIB` | Pembuatan skrip & panduan plot grafik historis FCPO (`src/plot_fcpo.py`) | Selesai |
| 5 | `2026-11-22 16:50 WIB` | Konfirmasi & ekspor dataset bersih FCPO (`data/processed/fcpo_clean.csv`) | Selesai |
| 6 | `2026-11-22 16:53 WIB` | Interpretasi grafik FCPO (`outputs/fcpo_price_plot.png`) & penentuan langkah lanjut | Selesai |
| 7 | `2026-11-22 16:58 WIB` | Penjelasan konsep grafik (Volatilitas, 20H, MA20/60, Harga Penutupan, Median 23,5%, & Rezim Pasar) | Selesai |
| 8 | `2026-11-22 19:48 WIB` | Pemberian daftar tautan, rentang tanggal, & nama file target untuk 4 data eksternal | Selesai |
| 9 | `2026-11-22 19:55 WIB` | Konversi HTML Yahoo Finance `IDR=X` menjadi `data/raw/idr_usd.csv` (`src/parse_yahoo_html.py`) | Selesai |
| 10 | `2026-11-22 19:58 WIB` | Konversi HTML `BZ=F`, `ZL=F`, & `MYR=X` ke CSV (`Tahap 0` selesai 100%) | Selesai |
| 11 | `2026-11-22 20:01 WIB` | Tahap 1: Alignment, lagging bebas leakage, fitur multi-horizon, rezim pasar, & plot tiap dataset | Selesai |

---

## Sesi #1 — `2026-11-22 16:19 WIB`

### 1. Prompt Input
- **Topik**: `#diskusi` dan `/roast me` terkait kelayakan judul baru, dataset, algoritma, serta langkah awal pengerjaan.
- **Judul Diajukan**: *Prediksi Multi-Horizon Harga Minyak Sawit Berjangka Menggunakan XGBoost dan LSTM Berbasis Variabel Eksternal dengan Evaluasi Walk-Forward*
- **Catatan Revisi Dosen**: *"Relevan untuk komoditas Indonesia, tetapi perbandingan dua algoritma belum cukup. Fokuskan pada prediksi multi-horizon, perubahan rezim pasar, variabel eksternal, dan evaluasi walk-forward. Jika tidak bisa dapat dataset tsb, ganti judul"*

| Komponen | Rencana Awal |
| :--- | :--- |
| **Algoritma** | XGBoost dan LSTM |
| **Target** | Harga Minyak Sawit Berjangka / FCPO (Investing.com) |
| **Variabel Eksternal** | `ZL=F` (Soybean Oil), `BZ=F` (Brent Crude), `MYR=X` (USD/MYR), `IDR=X` (USD/IDR) via Yahoo Finance |

### 2. Hasil Output — Evaluasi & Poin Revisi

| Aspek | Status | Temuan / Catatan Kritis | Rekomendasi Perbaikan |
| :--- | :--- | :--- | :--- |
| **Multi-Horizon** | Ada | Sudah tercantum di judul, belum ada definisi horizon spesifik | Tetapkan horizon tegas (mis. `h = 1, 5, 20` hari bursa) dengan strategi *Direct Multi-Step* |
| **Perubahan Rezim Pasar** | **Hilang** | Diminta dosen, tetapi tidak muncul di judul maupun skema analisis | Tambahkan di judul dan lakukan *Regime-Aware Evaluation* (mis. Rolling Volatility / 2-state HMM) |
| **Variabel Eksternal** | Ada | Pemilihan fitur eksternal sudah relevan secara ekonomi | Wajib lakukan *ablation study* (tanpa vs dengan eksternal) + analisis fitur (SHAP) |
| **Evaluasi Walk-Forward** | Ada | Rawan *data leakage* jika scaling dilakukan sebelum split | Gunakan *expanding/sliding window*; `Scaler` di-`fit` ulang di tiap window training |
| **Akuisisi Data FCPO** | Risiko Tinggi | Investing.com sering membatasi CSV historis & memblokir scraping | Pastikan unduh penuh minimal 5–10 tahun (2015–2025/2026) sebelum mengunci judul |
| **Timezone & Kalender** | Risiko Tinggi | `ZL=F` & `BZ=F` tutup setelah pasar Malaysia (FCPO) tutup | Gunakan kalender FCPO sebagai acuan dan terapkan *lag* ketat untuk mencegah *look-ahead bias* |
| **Target Prediksi** | Risiko Tinggi | XGBoost tidak bisa ekstrapolasi harga mentah di luar range training | Ubah target ke *log-return* / `% change`, lalu rekonstruksi ke harga bila diperlukan |
| **Baseline Pembanding** | **Belum Ada** | Belum ada patokan minimum performa model | Tambahkan **Naive / Random Walk** (dan opsional ARIMA/Ridge) |

### 3. Roadmap Pengerjaan Bertahap

| Tahap | Fokus Utama | Output yang Diharapkan |
| :--- | :--- | :--- |
| **Tahap 0** | Akuisisi & Verifikasi Data | Dataset CSV bersih untuk FCPO, `ZL=F`, `BZ=F`, `MYR=X`, dan `IDR=X` (histori 5–10 tahun) |
| **Tahap 1** | Data Alignment & EDA | Penyelarasan kalender & lag (bebas *look-ahead bias*), transformasi *log-return*, pemetaan rezim volatilitas |
| **Tahap 2** | Kerangka Walk-Forward & Baseline | Pipeline *expanding/sliding window* bebas leakage + hasil evaluasi Naive/Random Walk |
| **Tahap 3** | Modeling Multi-Horizon | Model XGBoost & LSTM per horizon (`h = 1, 5, 20`) untuk skenario *Internal Only* & *Internal + Eksternal* |
| **Tahap 4** | Evaluasi Rezim, Ablation, & SHAP | Perbandingan error per horizon & per rezim pasar, bukti kontribusi fitur eksternal |

### 4. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `PROGRESION.md` | Inisialisasi file notulensi progres proyek |
| **Diubah** | — | Tidak ada |
| **Dihapus** | — | Tidak ada |

---

## Sesi #2 — `2026-11-22 16:21 WIB`

### 1. Prompt Input
- Meminta perapihan format `PROGRESION.md` menggunakan tabel agar lebih terstruktur dan mudah dibaca.

### 2. Hasil Output
- Menata ulang seluruh bagian log sesi, komponen rencana, hasil evaluasi/roast, roadmap pengerjaan, dan riwayat perubahan file ke dalam format tabel Markdown.

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | — | Tidak ada |
| **Diubah** | `PROGRESION.md` | Perapihan format keseluruhan menjadi berbasis tabel + penambahan log Sesi #2 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #3 — `2026-11-22 16:29 WIB`

### 1. Prompt Input
- Meminta pembuatan `WORKING_PATH.md` berceklis agar progres proyek mudah dilacak.
- Menegaskan aturan agar setiap agen selalu membaca dan mencatat notulensi di `PROGRESION.md`.
- Meminta scraping/pengambilan data dari tautan Yahoo Finance (`ZL=F`, `BZ=F`, `MYR=X`, `IDR=X`) dan Investing.com (`https://share.google/Zjl2F9L7QktfnB4e0`).

### 2. Hasil Output & Status Eksekusi

| Komponen / Sumber | Status | Detail Hasil |
| :--- | :--- | :--- |
| **`WORKING_PATH.md`** | Selesai | Dibuat dengan peta struktur direktori, aturan wajib baca/catat `PROGRESION.md`, dan checklist Tahap 0–4 |
| **Struktur Direktori** | Selesai | Dibuat folder `data/raw/`, `data/processed/`, `src/`, `notebooks/`, dan `outputs/` |
| **`src/scrape_data.py`** | Selesai | Skrip akuisisi untuk Yahoo Finance chart API dan resolver URL Investing.com |
| **Yahoo Finance (`ZL=F`, `BZ=F`, `MYR=X`, `IDR=X`)** | **Gagal (429 / Exit 22)** | Terkena *rate limit* (`429 Too Many Requests` / `curl` exit 22) dari IP saat ini |
| **Investing.com (`https://id.investing.com/commodities/palm-oil-historical-data`)** | **Gagal (403)** | Diblokir proteksi anti-bot/Cloudflare (`HTTP 403`); perlu unduh CSV manual lewat browser ke `data/raw/fcpo_investing.csv` |

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `WORKING_PATH.md` | Peta kerja, aturan agen, dan checklist progres proyek Tahap 0–4 |
| **Ditambah** | `src/scrape_data.py` | Skrip akuisisi data Yahoo Finance & pengecekan Investing.com |
| **Ditambah** | `data/raw/`, `data/processed/`, `notebooks/`, `outputs/` | Struktur direktori proyek |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #3 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #4 — `2026-11-22 16:46 WIB`

### 1. Prompt Input
- Meminta diajarkan kode untuk membuat grafik dari `data/raw/fcpo_investing.csv`.

### 2. Hasil Output & Verifikasi
- Berhasil mengidentifikasi format CSV Investing.com versi Indonesia (pemisah ribuan `.`, pemisah desimal `,`, format tanggal `DD/MM/YYYY` terurut menurun).
- Membuat skrip `src/plot_fcpo.py` untuk membersihkan angka format Indonesia, mengurutkan tanggal menaik, menghitung `Log_Return`, `MA20`, `MA60`, dan `Vol20_Annualized`, serta menyimpan grafik 2 panel ke `outputs/fcpo_price_plot.png`.
- **Hasil eksekusi**: `2.913` baris, rentang `2014-08-18` s.d. `2026-11-20`, `0` missing value pada kolom `Terakhir`.

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `src/plot_fcpo.py` | Skrip pembersihan data & plotting grafik harga + volatilitas FCPO |
| **Ditambah** | `outputs/fcpo_price_plot.png` | Output grafik 2 panel harga penutupan FCPO (`MA20`, `MA60`) & volatilitas bergulir |
| **Diubah** | `WORKING_PATH.md` | Ceklis `[x]` untuk akuisisi data `fcpo_investing.csv` |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #4 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #5 — `2026-11-22 16:50 WIB`

### 1. Prompt Input
- Memastikan apakah masalah 1, 2, dan 3 (format angka Indonesia, format/urutan tanggal, serta 2 panel harga + volatilitas) sudah diatur pada data/kode, dan meminta pengaturan jika belum.

### 2. Hasil Output & Verifikasi
- Mengonfirmasi bahwa ketiga hal tersebut sudah otomatis ditangani di `src/plot_fcpo.py`.
- Melengkapi `src/plot_fcpo.py` dengan parsing kolom `Vol.` (`K`/`M`) dan `Perubahan%`, serta menyimpan hasil bersihnya ke `data/processed/fcpo_clean.csv` (`2.913` baris, terurut naik `2014-08-18` s.d. `2026-11-20`, `0` missing value pada `Terakhir`).

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `data/processed/fcpo_clean.csv` | Dataset FCPO bersih (angka standar, tanggal urut naik, `Volume`, `Perubahan_Pct`, `Log_Return`, `MA20`, `MA60`, `Vol20_Annualized`) |
| **Diubah** | `src/plot_fcpo.py` | Penambahan parsing `Vol.` & `Perubahan%` serta ekspor ke `data/processed/fcpo_clean.csv` |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #5 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #6 — `2026-11-22 16:53 WIB`

### 1. Prompt Input
- Meminta penjelasan menyeluruh dari grafik `outputs/fcpo_price_plot.png` serta langkah selanjutnya yang harus dilakukan.

### 2. Hasil Output & Temuan Kunci
- **Statistik terverifikasi**: Harga minimum `1.759,0` MYR/ton (`2018-11-14`), maksimum `8.163,0` MYR/ton (`2022-03-01`), terakhir `4.217,0` MYR/ton (`2026-11-20`); median volatilitas 20H `23,51%` dengan puncak `99,04%` (`2022-03-23`).
- **Temuan metodologis**: Grafik memperlihatkan *structural break* harga (pra-2020 vs pasca-2020) dan *volatility clustering* yang jelas (rezim tenang vs krisis 2020 & 2022), memperkuat kebutuhan target *log-return*, *regime-aware evaluation*, dan *walk-forward*.
- **Langkah berikut**: Melengkapi 4 CSV variabel eksternal (`ZL=F`, `BZ=F`, `MYR=X`, `IDR=X`) ke `data/raw/` lalu masuk ke Tahap 1 (*alignment*, *lagging*, dan pelabelan rezim).

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | — | Tidak ada |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #6 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #7 — `2026-11-22 16:58 WIB`

### 1. Prompt Input
- Meminta penjelasan istilah dan angka pada grafik: volatilitas, 20H, MA 20 hari, MA 60 hari, harga penutupan, asal angka median 23,5%, serta maksud dari rezim pasar.

### 2. Hasil Output
- Memberikan penjelasan konseptual dan matematis (mengacu pada implementasi di `src/plot_fcpo.py`) mengenai harga penutupan, `MA20`, `MA60`, volatilitas bergulir 20 hari (`Vol20_Annualized`), asal nilai median `23,51%`, dan konsep rezim pasar untuk kebutuhan pemahaman skripsi.

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | — | Tidak ada |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #7 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #8 — `2026-11-22 19:48 WIB`

### 1. Prompt Input
- Meminta daftar data lainnya yang perlu diunduh beserta detailnya.

### 2. Hasil Output
- Memberikan daftar lengkap 4 dataset variabel eksternal (`ZL=F`, `BZ=F`, `MYR=X`, `IDR=X`), tautan sumber, rentang tanggal (`2014-08-18` s.d. `2026-11-20`), dan nama file tujuan di `data/raw/`.

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | — | Tidak ada |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #8 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #9 — `2026-11-22 19:55 WIB`

### 1. Prompt Input
- Mengonfirmasi apakah data `IDR=X` yang disimpan sebagai HTML dari Yahoo Finance (`USD_IDR (IDR=X) Stock Historical Prices & Data - Yahoo Finance.html`) sudah berisi datanya.

### 2. Hasil Output & Verifikasi
- Mengonfirmasi bahwa tabel historis lengkap ada di dalam file HTML (`6.416` baris, `2001-06-28` s.d. `2026-11-22`).
- Membuat `src/parse_yahoo_html.py` untuk mengonversi file `.html` Yahoo Finance di `data/raw/` menjadi CSV bersih, dan menghasilkan `data/raw/idr_usd.csv`.

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `src/parse_yahoo_html.py` | Skrip parser HTML Yahoo Finance ke CSV |
| **Ditambah** | `data/raw/idr_usd.csv` | Dataset bersih USD/IDR (`6.416` baris, `2001-06-28` s.d. `2026-11-22`) |
| **Diubah** | `WORKING_PATH.md` | Ceklis `[x]` untuk akuisisi data `IDR=X` |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #9 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #10 — `2026-11-22 19:58 WIB`

### 1. Prompt Input
- Meminta ekstraksi/scraping untuk 3 dataset eksternal lainnya (`BZ=F`, `ZL=F`, `MYR=X`) yang sudah disimpan sebagai file HTML di `data/raw/`.

### 2. Hasil Output & Verifikasi
- Menjalankan `src/parse_yahoo_html.py` dan berhasil mengonversi seluruh file HTML menjadi CSV bersih:
  - `bz_brent_crude.csv` (`BZ=F`): `4.809` baris (`2007-07-30` s.d. `2026-11-20`)
  - `zl_soybean_oil.csv` (`ZL=F`): `6.635` baris (`2000-03-15` s.d. `2026-11-20`)
  - `myr_usd.csv` (`MYR=X`): `5.982` baris (`2003-12-01` s.d. `2026-11-22`)
- **Tahap 0 (Akuisisi & Verifikasi Data) selesai 100%**: seluruh 5 dataset mencakup penuh rentang target FCPO (`2014-08-18` s.d. `2026-11-20`).

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `data/raw/bz_brent_crude.csv` | Dataset Brent Crude Oil (`4.809` baris) |
| **Ditambah** | `data/raw/zl_soybean_oil.csv` | Dataset Soybean Oil (`6.635` baris) |
| **Ditambah** | `data/raw/myr_usd.csv` | Dataset USD/MYR (`5.982` baris) |
| **Diubah** | `WORKING_PATH.md` | Ceklis `[x]` untuk seluruh item Tahap 0 |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #10 |
| **Dihapus** | — | Tidak ada |

---

## Sesi #11 — `2026-11-22 20:01 WIB`

### 1. Prompt Input
- Meminta lanjut ke Tahap 1 serta membuatkan plot grafik dari masing-masing dataset.

### 2. Hasil Output & Verifikasi
- Membuat dan menjalankan `src/prepare_dataset.py` untuk menyelaraskan seluruh variabel eksternal ke kalender FCPO (`2014-08-18` s.d. `2026-11-20`), menerapkan *lagging* minimal 1 hari (`shift(1)`) pada variabel eksternal, membangun target multi-horizon (`target_ret_h1`, `target_ret_h5`, `target_ret_h20`), dan melabeli rezim volatilitas (`regime_high_vol` berbasis *expanding median*).
- **Dataset hasil**: `data/processed/dataset_aligned.csv` (`2.913` baris x `43` kolom, `0` missing values pada seluruh kolom `Close`).
- **Distribusi Rezim**: `High_Vol (1.0)` = `1.702` hari, `Low_Vol (0.0)` = `1.132` hari.
- **Korelasi lag-1 eksternal terhadap `fcpo_ret_1d`**: `zl_ret_lag1` (`+0.2146`), `bz_ret_lag1` (`+0.0719`), `myr_ret_lag1` (`+0.0131`), `idr_ret_lag1` (`-0.0135`).
- **Grafik dihasilkan**: `zl_plot.png`, `bz_plot.png`, `myr_plot.png`, `idr_plot.png`, dan `all_datasets_comparison.png` di `outputs/`.

### 3. Perubahan File & Program

| Aksi | File / Program | Keterangan |
| :--- | :--- | :--- |
| **Ditambah** | `src/prepare_dataset.py` | Skrip Tahap 1 (alignment, feature engineering, regime labeling, & plotting) |
| **Ditambah** | `data/processed/dataset_aligned.csv` | Dataset gabungan siap latih (`2.913` baris x `43` kolom) |
| **Ditambah** | `outputs/zl_plot.png`, `outputs/bz_plot.png`, `outputs/myr_plot.png`, `outputs/idr_plot.png`, `outputs/all_datasets_comparison.png` | Grafik harga + volatilitas tiap variabel eksternal & perbandingan indeks ternormalisasi |
| **Diubah** | `WORKING_PATH.md` | Ceklis `[x]` untuk seluruh item Tahap 1 |
| **Diubah** | `PROGRESION.md` | Penambahan log Sesi #11 |
| **Dihapus** | — | Tidak ada |
