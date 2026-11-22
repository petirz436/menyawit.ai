"""
Mengonversi file HTML halaman Historical Data Yahoo Finance yang disimpan dari browser
menjadi file CSV bersih di data/raw/.
"""

import glob
import os
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")

HTML_MAPPING = {
    "ZL=F": "zl_soybean_oil.csv",
    "BZ=F": "bz_brent_crude.csv",
    "MYR=X": "myr_usd.csv",
    "IDR=X": "idr_usd.csv",
}


def convert_yahoo_html_to_csv(html_path: str, out_csv_path: str) -> pd.DataFrame:
    """Membaca tabel historis dari HTML Yahoo Finance dan menyimpannya ke CSV."""
    tables = pd.read_html(html_path)
    if not tables:
        raise ValueError(f"Tidak ada tabel di {html_path}")

    df = tables[0].copy()
    rename_map = {}
    for col in df.columns:
        c_low = str(col).lower()
        if c_low.startswith("date"):
            rename_map[col] = "Date"
        elif c_low.startswith("open"):
            rename_map[col] = "Open"
        elif c_low.startswith("high"):
            rename_map[col] = "High"
        elif c_low.startswith("low"):
            rename_map[col] = "Low"
        elif c_low.startswith("close"):
            rename_map[col] = "Close"
        elif c_low.startswith("adj close"):
            rename_map[col] = "Adj Close"
        elif c_low.startswith("volume"):
            rename_map[col] = "Volume"

    df = df.rename(columns=rename_map)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].replace("-", pd.NA), errors="coerce")

    df = (
        df.dropna(subset=["Close"])
        .drop_duplicates(subset=["Date"])
        .sort_values("Date")
        .reset_index(drop=True)
    )
    df.to_csv(out_csv_path, index=False)
    return df


def main() -> None:
    html_files = sorted(glob.glob(os.path.join(RAW_DIR, "*.html")))
    if not html_files:
        print("Tidak ada file .html di data/raw/.")
        return

    for html_path in html_files:
        basename = os.path.basename(html_path)
        matched_csv = None
        for ticker, csv_name in HTML_MAPPING.items():
            if ticker in basename:
                matched_csv = csv_name
                break

        if not matched_csv:
            print(f"[SKIP] {basename} (ticker tidak dikenali)")
            continue

        out_path = os.path.join(RAW_DIR, matched_csv)
        df = convert_yahoo_html_to_csv(html_path, out_path)
        print(
            f"[OK] {basename} -> {matched_csv} | "
            f"{len(df)} baris | {df['Date'].min().date()} s.d. {df['Date'].max().date()}"
        )


if __name__ == "__main__":
    main()

