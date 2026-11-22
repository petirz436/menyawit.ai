"""
Skrip pembersihan dasar dan visualisasi grafik historis FCPO (Investing.com format Indonesia).
Menghasilkan grafik harga penutupan + Moving Average serta volatilitas bergulir (indikasi rezim pasar).
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "raw", "fcpo_investing.csv")
PROCESSED_PATH = os.path.join(BASE_DIR, "data", "processed", "fcpo_clean.csv")
OUT_PATH = os.path.join(BASE_DIR, "outputs", "fcpo_price_plot.png")


def parse_id_number(series: pd.Series) -> pd.Series:
    """Mengonversi angka format Indonesia ('4.217,00') menjadi float ('4217.00')."""
    cleaned = (
        series.astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def parse_volume(series: pd.Series) -> pd.Series:
    """Mengonversi kolom volume ('38,49K', '1,20M', '-') menjadi angka float."""
    s = series.astype(str).str.strip().replace({"-": np.nan, "nan": np.nan})
    multiplier = np.where(
        s.str.endswith("M", na=False), 1e6,
        np.where(s.str.endswith("K", na=False), 1e3, 1.0),
    )
    numeric = parse_id_number(s.str.rstrip("KMkm"))
    return numeric * multiplier


def load_fcpo(csv_path: str) -> pd.DataFrame:
    """Memuat dan merapikan data historis FCPO dari Investing.com."""
    df = pd.read_csv(csv_path)
    df["Tanggal"] = pd.to_datetime(df["Tanggal"], format="%d/%m/%Y")

    for col in ["Terakhir", "Pembukaan", "Tertinggi", "Terendah"]:
        df[col] = parse_id_number(df[col])

    if "Vol." in df.columns:
        df["Volume"] = parse_volume(df["Vol."])
    if "Perubahan%" in df.columns:
        df["Perubahan_Pct"] = parse_id_number(df["Perubahan%"].astype(str).str.rstrip("%"))

    df = df.sort_values("Tanggal").drop_duplicates(subset=["Tanggal"]).reset_index(drop=True)
    df["Log_Return"] = np.log(df["Terakhir"] / df["Terakhir"].shift(1))
    df["MA20"] = df["Terakhir"].rolling(20).mean()
    df["MA60"] = df["Terakhir"].rolling(60).mean()
    df["Vol20_Annualized"] = df["Log_Return"].rolling(20).std() * np.sqrt(252) * 100
    return df


def plot_fcpo(df: pd.DataFrame, out_path: str) -> None:
    """Membuat grafik 2 panel: Harga + MA dan Volatilitas Bergulir 20 Hari."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(13, 8), sharex=True, gridspec_kw={"height_ratios": [2.2, 1]}
    )

    # Panel 1: Harga Penutupan & Moving Average
    ax1.plot(df["Tanggal"], df["Terakhir"], label="Harga Penutupan (Terakhir)", color="#1f77b4", linewidth=1.2)
    ax1.plot(df["Tanggal"], df["MA20"], label="MA 20 Hari", color="#ff7f0e", linewidth=1.1, alpha=0.9)
    ax1.plot(df["Tanggal"], df["MA60"], label="MA 60 Hari", color="#2ca02c", linewidth=1.1, alpha=0.9)
    ax1.set_title("Harga Minyak Sawit Berjangka (FCPO) & Indikasi Rezim Volatilitas", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Harga (MYR/ton)")
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle="--", alpha=0.4)

    # Panel 2: Volatilitas Bergulir 20 Hari
    ax2.plot(df["Tanggal"], df["Vol20_Annualized"], label="Volatilitas Bergulir 20H (Annualized %)", color="#d62728", linewidth=1.0)
    median_vol = df["Vol20_Annualized"].median()
    ax2.axhline(median_vol, color="gray", linestyle="--", linewidth=1.0, label=f"Median ({median_vol:.1f}%)")
    ax2.set_ylabel("Volatilitas (%)")
    ax2.set_xlabel("Tanggal")
    ax2.legend(loc="upper left")
    ax2.grid(True, linestyle="--", alpha=0.4)

    ax2.xaxis.set_major_locator(mdates.YearLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def main() -> None:
    df = load_fcpo(CSV_PATH)
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    cols_to_save = [
        "Tanggal", "Terakhir", "Pembukaan", "Tertinggi", "Terendah",
        "Volume", "Perubahan_Pct", "Log_Return", "MA20", "MA60", "Vol20_Annualized",
    ]
    df[[c for c in cols_to_save if c in df.columns]].to_csv(PROCESSED_PATH, index=False)
    plot_fcpo(df, OUT_PATH)
    print(f"Baris data : {len(df)}")
    print(f"Rentang    : {df['Tanggal'].min().date()} s.d. {df['Tanggal'].max().date()}")
    print(f"Missing    : {df['Terakhir'].isna().sum()}")
    print(f"CSV Bersih : {PROCESSED_PATH}")
    print(f"Grafik     : {OUT_PATH}")


if __name__ == "__main__":
    main()

