"""
Tahap 1: Data Alignment, Lagging (Bebas Look-Ahead Bias), Feature Engineering,
Pelabelan Rezim Pasar, & Visualisasi Seluruh Dataset.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

EXTERNAL_FILES = {
    "zl": ("zl_soybean_oil.csv", "Soybean Oil Futures (ZL=F)", "US cents/lb", "#ff7f0e"),
    "bz": ("bz_brent_crude.csv", "Brent Crude Oil Futures (BZ=F)", "USD/barrel", "#2ca02c"),
    "myr": ("myr_usd.csv", "Kurs USD/MYR (MYR=X)", "MYR per USD", "#9467bd"),
    "idr": ("idr_usd.csv", "Kurs USD/IDR (IDR=X)", "IDR per USD", "#8c564b"),
}

HORIZONS = [1, 5, 20]


def load_external_close(filename: str, prefix: str) -> pd.DataFrame:
    """Memuat tanggal dan harga Close dari CSV Yahoo Finance yang sudah dibersihkan."""
    path = os.path.join(RAW_DIR, filename)
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df[["Date", "Close"]].dropna().drop_duplicates(subset=["Date"]).sort_values("Date")
    df = df.rename(columns={"Date": "Tanggal", "Close": f"{prefix}_close"})
    return df


def align_to_fcpo_calendar(fcpo_df: pd.DataFrame) -> pd.DataFrame:
    """
    Menyelaraskan seluruh variabel eksternal ke kalender hari bursa FCPO
    menggunakan merge_asof arah backward (hanya memakai harga terakhir yang sudah terjadi).
    """
    aligned = fcpo_df[["Tanggal", "Terakhir", "Volume"]].rename(
        columns={"Terakhir": "fcpo_close", "Volume": "fcpo_volume"}
    )
    aligned = aligned.sort_values("Tanggal").reset_index(drop=True)

    for prefix, (filename, _, _, _) in EXTERNAL_FILES.items():
        ext_df = load_external_close(filename, prefix)
        aligned = pd.merge_asof(
            aligned,
            ext_df,
            on="Tanggal",
            direction="backward",
        )

    return aligned


def build_features_and_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Membangun fitur lag, log-return, volatilitas, target multi-horizon (h=1,5,20),
    dan label rezim pasar tanpa look-ahead bias.
    """
    out = df.copy()

    # 1. Log-return harian FCPO & fitur internal (tersedia saat penutupan FCPO hari t)
    out["fcpo_ret_1d"] = np.log(out["fcpo_close"] / out["fcpo_close"].shift(1))
    for lag in [1, 2, 3, 5, 10]:
        out[f"fcpo_ret_lag{lag}"] = out["fcpo_ret_1d"].shift(lag)

    out["fcpo_ma20"] = out["fcpo_close"].rolling(20).mean()
    out["fcpo_ma60"] = out["fcpo_close"].rolling(60).mean()
    out["fcpo_ma20_ratio"] = (out["fcpo_close"] / out["fcpo_ma20"]) - 1.0
    out["fcpo_ma60_ratio"] = (out["fcpo_close"] / out["fcpo_ma60"]) - 1.0
    out["fcpo_vol20_ann"] = out["fcpo_ret_1d"].rolling(20).std() * np.sqrt(252) * 100
    out["fcpo_vol60_ann"] = out["fcpo_ret_1d"].rolling(60).std() * np.sqrt(252) * 100

    # 2. Variabel eksternal: WAJIB di-lag minimal 1 hari (shift(1)) karena pasar US/FX
    #    tutup setelah bursa Malaysia (FCPO) tutup pada hari kalender yang sama.
    for prefix in EXTERNAL_FILES:
        ret_col = f"{prefix}_ret_1d"
        out[ret_col] = np.log(out[f"{prefix}_close"] / out[f"{prefix}_close"].shift(1))
        for lag in [1, 2, 5]:
            out[f"{prefix}_ret_lag{lag}"] = out[ret_col].shift(lag)
        out[f"{prefix}_vol20_lag1"] = (out[ret_col].rolling(20).std() * np.sqrt(252) * 100).shift(1)

    # 3. Pelabelan rezim pasar (expanding median hingga hari t agar bebas future leakage)
    expanding_med_vol = out["fcpo_vol20_ann"].expanding(min_periods=60).median()
    out["regime_high_vol"] = (out["fcpo_vol20_ann"] > expanding_med_vol).astype(float)
    out.loc[expanding_med_vol.isna(), "regime_high_vol"] = np.nan

    # 4. Target multi-horizon: cumulative log-return ln(P_{t+h} / P_t)
    for h in HORIZONS:
        out[f"target_ret_h{h}"] = np.log(out["fcpo_close"].shift(-h) / out["fcpo_close"])

    return out


def plot_single_external(df: pd.DataFrame, prefix: str, title: str, unit: str, color: str) -> str:
    """Membuat grafik harga + MA20/MA60 dan volatilitas bergulir 20H untuk 1 variabel eksternal."""
    col = f"{prefix}_close"
    ret = np.log(df[col] / df[col].shift(1))
    ma20 = df[col].rolling(20).mean()
    ma60 = df[col].rolling(60).mean()
    vol20 = ret.rolling(20).std() * np.sqrt(252) * 100

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 7), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]}
    )
    ax1.plot(df["Tanggal"], df[col], label="Harga Penutupan", color=color, linewidth=1.2)
    ax1.plot(df["Tanggal"], ma20, label="MA 20 Hari", color="#1f77b4", linewidth=1.0, alpha=0.85)
    ax1.plot(df["Tanggal"], ma60, label="MA 60 Hari", color="#333333", linewidth=1.0, alpha=0.75)
    ax1.set_title(f"{title} — Harga & Volatilitas (2014–2026)", fontsize=12, fontweight="bold")
    ax1.set_ylabel(unit)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle="--", alpha=0.4)

    ax2.plot(df["Tanggal"], vol20, label="Volatilitas Bergulir 20H (%)", color="#d62728", linewidth=1.0)
    med = vol20.median()
    ax2.axhline(med, color="gray", linestyle="--", linewidth=1.0, label=f"Median ({med:.1f}%)")
    ax2.set_ylabel("Volatilitas (%)")
    ax2.set_xlabel("Tanggal")
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle="--", alpha=0.4)

    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    out_path = os.path.join(OUT_DIR, f"{prefix}_plot.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_combined_overview(df: pd.DataFrame) -> str:
    """Membuat grafik perbandingan indeks harga ternormalisasi (base=100) seluruh 5 variabel."""
    fig, ax = plt.subplots(figsize=(13, 6))

    series_map = [
        ("fcpo_close", "FCPO (Sawit)", "#1f77b4", 1.6),
        ("zl_close", "ZL=F (Soybean Oil)", "#ff7f0e", 1.2),
        ("bz_close", "BZ=F (Brent Crude)", "#2ca02c", 1.2),
        ("myr_close", "MYR=X (USD/MYR)", "#9467bd", 1.1),
        ("idr_close", "IDR=X (USD/IDR)", "#8c564b", 1.1),
    ]
    for col, label, color, lw in series_map:
        norm = (df[col] / df[col].iloc[0]) * 100.0
        ax.plot(df["Tanggal"], norm, label=label, color=color, linewidth=lw)

    ax.set_title("Perbandingan Pergerakan Relatif Seluruh Dataset (Indeks Awal 2014-08-18 = 100)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Indeks Harga (Base = 100)")
    ax.set_xlabel("Tanggal")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    out_path = os.path.join(OUT_DIR, "all_datasets_comparison.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main() -> None:
    os.makedirs(PROC_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)

    fcpo_path = os.path.join(PROC_DIR, "fcpo_clean.csv")
    fcpo_df = pd.read_csv(fcpo_path, parse_dates=["Tanggal"])

    aligned = align_to_fcpo_calendar(fcpo_df)
    dataset = build_features_and_targets(aligned)

    out_csv = os.path.join(PROC_DIR, "dataset_aligned.csv")
    dataset.to_csv(out_csv, index=False)

    print(f"Dataset aligned tersimpan : {out_csv}")
    print(f"Dimensi total             : {dataset.shape[0]} baris x {dataset.shape[1]} kolom")
    print(f"Rentang tanggal           : {dataset['Tanggal'].min().date()} s.d. {dataset['Tanggal'].max().date()}")

    # Cek missing value pada kolom Close hasil alignment
    close_cols = ["fcpo_close"] + [f"{p}_close" for p in EXTERNAL_FILES]
    print("Missing values (Close)    :", dataset[close_cols].isna().sum().to_dict())

    # Distribusi rezim pasar
    regime_counts = dataset["regime_high_vol"].value_counts(dropna=True).to_dict()
    print("Distribusi Rezim (0=Low, 1=High):", regime_counts)

    # Korelasi log-return (lag1 eksternal vs return FCPO hari t)
    corr_cols = ["fcpo_ret_1d"] + [f"{p}_ret_lag1" for p in EXTERNAL_FILES]
    print("\nKorelasi dengan fcpo_ret_1d (lag1 eksternal):")
    print(dataset[corr_cols].corr()["fcpo_ret_1d"].round(4).to_dict())

    # Buat plot masing-masing dataset eksternal & plot perbandingan gabungan
    print("\nMembuat grafik:")
    for prefix, (_, title, unit, color) in EXTERNAL_FILES.items():
        p = plot_single_external(aligned, prefix, title, unit, color)
        print(f"  - {p}")
    comp_path = plot_combined_overview(aligned)
    print(f"  - {comp_path}")


if __name__ == "__main__":
    main()

