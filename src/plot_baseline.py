"""
Visualisasi hasil Tahap 2 (Walk-Forward Baseline):
1. Perbandingan Price_RMSE dan Dir_Acc_% antar model per horizon (h=1, 5, 20).
2. Perbandingan harga aktual vs prediksi (Naive & Ridge Eksternal) untuk h=1 dan h=20.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
OUT_DIR = os.path.join(BASE_DIR, "outputs")
RES_PATH = os.path.join(OUT_DIR, "baseline_results.csv")
PRED_PATH = os.path.join(OUT_DIR, "baseline_predictions.csv")


def plot_metrics_bar(res_df: pd.DataFrame) -> str:
    """Membuat bar chart perbandingan Price_RMSE dan Dir_Acc_% per horizon."""
    horizons = ["h=1", "h=5", "h=20"]
    models = ["Naive (Random Walk)", "Ridge (Internal Only)", "Ridge (Internal + Eksternal)"]
    colors = ["#7f7f7f", "#1f77b4", "#ff7f0e"]

    x = np.arange(len(horizons))
    width = 0.25

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    for idx, (model, color) in enumerate(zip(models, colors)):
        sub = res_df[res_df["Model"] == model].set_index("Horizon").reindex(horizons)
        bars1 = ax1.bar(x + (idx - 1) * width, sub["Price_RMSE"], width, label=model, color=color)
        bars2 = ax2.bar(x + (idx - 1) * width, sub["Dir_Acc_%"], width, label=model, color=color)

        for b in bars1:
            ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 6, f"{b.get_height():.1f}", ha="center", fontsize=8)
        for b in bars2:
            ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.6, f"{b.get_height():.1f}%", ha="center", fontsize=8)

    ax1.set_title("Perbandingan Price RMSE per Horizon (Lebih Rendah Lebih Baik)", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(horizons)
    ax1.set_ylabel("Price RMSE (MYR/ton)")
    ax1.legend(loc="upper left", fontsize=8)
    ax1.grid(True, axis="y", linestyle="--", alpha=0.4)

    ax2.set_title("Perbandingan Directional Accuracy per Horizon (Lebih Tinggi Lebih Baik)", fontsize=11, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(horizons)
    ax2.set_ylabel("Directional Accuracy (%)")
    ax2.axhline(50.0, color="red", linestyle="--", linewidth=1.0, label="Acuan 50% (Acak)")
    ax2.set_ylim(35, 62)
    ax2.legend(loc="upper left", fontsize=8)
    ax2.grid(True, axis="y", linestyle="--", alpha=0.4)

    out_path = os.path.join(OUT_DIR, "baseline_metrics_plot.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def plot_price_predictions(pred_df: pd.DataFrame) -> str:
    """Membuat grafik harga aktual vs prediksi walk-forward untuk h=1 dan h=20."""
    fig, axes = plt.subplots(2, 1, figsize=(13, 8), sharex=True)

    for ax, h, title in [
        (axes[0], 1, "Walk-Forward Horizon h=1 Hari: Harga Aktual vs Prediksi"),
        (axes[1], 20, "Walk-Forward Horizon h=20 Hari: Harga Aktual vs Prediksi"),
    ]:
        sub = pred_df[pred_df["Horizon"] == h].copy()
        p_actual = sub["Base_Price"] * np.exp(sub["Actual_Ret"])
        p_naive = sub["Base_Price"] * np.exp(sub["Pred_Naive"])
        p_ridge_all = sub["Base_Price"] * np.exp(sub["Pred_Ridge_All"])

        ax.plot(sub["Tanggal"], p_actual, label="Harga Aktual (t+h)", color="#1f77b4", linewidth=1.3)
        ax.plot(sub["Tanggal"], p_naive, label="Naive (Random Walk)", color="#7f7f7f", linewidth=0.9, alpha=0.7, linestyle="--")
        ax.plot(sub["Tanggal"], p_ridge_all, label="Ridge (Internal + Eksternal)", color="#ff7f0e", linewidth=1.0, alpha=0.85)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_ylabel("Harga (MYR/ton)")
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.4)

    axes[1].set_xlabel("Tanggal (Periode Uji Walk-Forward 2019–2026)")
    axes[1].xaxis.set_major_locator(mdates.YearLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    out_path = os.path.join(OUT_DIR, "baseline_predictions_plot.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main() -> None:
    res_df = pd.read_csv(RES_PATH)
    pred_df = pd.read_csv(PRED_PATH, parse_dates=["Tanggal"])

    p1 = plot_metrics_bar(res_df)
    p2 = plot_price_predictions(pred_df)
    print(f"Grafik metrik   : {p1}")
    print(f"Grafik prediksi : {p2}")


if __name__ == "__main__":
    main()

