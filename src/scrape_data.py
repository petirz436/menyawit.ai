"""
Skrip akuisisi data historis untuk proyek Prediksi Multi-Horizon Harga Minyak Sawit Berjangka.
Sumber:
1. Yahoo Finance (ZL=F, BZ=F, MYR=X, IDR=X) via chart API
2. Investing.com (link shortener https://share.google/Zjl2F9L7QktfnB4e0)
"""

import json
import os
import subprocess
import time
import requests
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/html,application/xhtml+xml,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

YAHOO_TICKERS = {
    "ZL=F": "zl_soybean_oil.csv",
    "BZ=F": "bz_brent_crude.csv",
    "MYR=X": "myr_usd.csv",
    "IDR=X": "idr_usd.csv",
}


def fetch_yahoo_history(ticker: str, data_range: str = "5y") -> pd.DataFrame:
    """Mengambil data OHLCV harian dari Yahoo Finance v8 chart API via curl."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={data_range}&interval=1d"
    proc = subprocess.run(
        ["curl", "-fsSL", "-A", HEADERS["User-Agent"], url],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    payload = json.loads(proc.stdout)

    result = payload["chart"]["result"][0]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]
    adjclose = result["indicators"].get("adjclose", [{}])[0].get("adjclose", [None] * len(timestamps))

    df = pd.DataFrame({
        "Date": pd.to_datetime(timestamps, unit="s", utc=True).tz_convert(None).normalize(),
        "Open": quote.get("open"),
        "High": quote.get("high"),
        "Low": quote.get("low"),
        "Close": quote.get("close"),
        "Adj Close": adjclose,
        "Volume": quote.get("volume"),
    })
    df = df.dropna(subset=["Close"]).drop_duplicates(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df


def try_fetch_investing(short_url: str = "https://share.google/Zjl2F9L7QktfnB4e0") -> None:
    """Mencoba resolve short URL dan mengambil tabel historis Investing.com."""
    print(f"\n[Investing.com] Resolving {short_url} ...")
    session = requests.Session()
    resp = session.get(short_url, headers=HEADERS, timeout=20, allow_redirects=True)
    print(f"[Investing.com] Final URL: {resp.url} | Status: {resp.status_code}")

    if resp.status_code != 200:
        print(
            "[Investing.com] Gagal mengakses halaman langsung (kemungkinan proteksi Cloudflare/anti-bot). "
            "Jika terblokir, unduh CSV historis secara manual dari browser ke data/raw/fcpo_investing.csv."
        )
        return

    try:
        tables = pd.read_html(resp.text)
        if tables:
            df = tables[0]
            out_path = os.path.join(RAW_DIR, "fcpo_investing_preview.csv")
            df.to_csv(out_path, index=False)
            print(f"[Investing.com] Berhasil parsing tabel preview ({len(df)} baris) -> {out_path}")
        else:
            print("[Investing.com] Tidak ada tabel HTML yang terdeteksi di respons.")
    except Exception as exc:
        print(f"[Investing.com] Gagal parsing tabel HTML: {exc}")


def main() -> None:
    print("=== Mulai Akuisisi Data Yahoo Finance ===")
    for ticker, filename in YAHOO_TICKERS.items():
        try:
            df = fetch_yahoo_history(ticker)
            out_path = os.path.join(RAW_DIR, filename)
            df.to_csv(out_path, index=False)
            print(
                f"[OK] {ticker:6s} -> {filename:22s} | "
                f"{len(df):5d} baris | {df['Date'].min().date()} s.d. {df['Date'].max().date()}"
            )
        except Exception as exc:
            print(f"[GAGAL] {ticker}: {exc}")
        time.sleep(2.0)

    try_fetch_investing()


if __name__ == "__main__":
    main()
