"""
Tahap 2: Kerangka Walk-Forward Validation (Expanding Window + Embargo) & Baseline (Naive + Ridge).
Menghasilkan metrik evaluasi multi-horizon (h=1, 5, 20) bebas data leakage.
"""

import os
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "dataset_aligned.csv")
OUT_DIR = os.path.join(BASE_DIR, "outputs")

HORIZONS = [1, 5, 20]
TEST_YEARS = list(range(2019, 2027))

INTERNAL_FEATURES = [
    "fcpo_ret_1d", "fcpo_ret_lag1", "fcpo_ret_lag2", "fcpo_ret_lag3",
    "fcpo_ret_lag5", "fcpo_ret_lag10",
    "fcpo_ma20_ratio", "fcpo_ma60_ratio",
    "fcpo_vol20_ann", "fcpo_vol60_ann", "regime_high_vol",
]

EXTERNAL_FEATURES = [
    "zl_ret_lag1", "zl_ret_lag2", "zl_ret_lag5", "zl_vol20_lag1",
    "bz_ret_lag1", "bz_ret_lag2", "bz_ret_lag5", "bz_vol20_lag1",
    "myr_ret_lag1", "myr_ret_lag2", "myr_ret_lag5", "myr_vol20_lag1",
    "idr_ret_lag1", "idr_ret_lag2", "idr_ret_lag5", "idr_vol20_lag1",
]

ALL_FEATURES = INTERNAL_FEATURES + EXTERNAL_FEATURES


def compute_metrics(y_true_ret: np.ndarray, y_pred_ret: np.ndarray, p_base: np.ndarray) -> dict:
    """Menghitung metrik return dan rekonstruksi harga (RMSE, MAE, MAPE, Directional Accuracy)."""
    p_true = p_base * np.exp(y_true_ret)
    p_pred = p_base * np.exp(y_pred_ret)

    price_rmse = float(np.sqrt(mean_squared_error(p_true, p_pred)))
    price_mae = float(mean_absolute_error(p_true, p_pred))
    price_mape = float(np.mean(np.abs((p_true - p_pred) / p_true)) * 100.0)
    ret_rmse = float(np.sqrt(mean_squared_error(y_true_ret, y_pred_ret)))

    # Directional Accuracy: apakah arah prediksi sama dengan arah aktual (kecuali 0)
    dir_acc = float(np.mean((y_pred_ret > 0) == (y_true_ret > 0)) * 100.0)

    return {
        "Price_RMSE": round(price_rmse, 2),
        "Price_MAE": round(price_mae, 2),
        "Price_MAPE": round(price_mape, 2),
        "Return_RMSE": round(ret_rmse, 5),
        "Dir_Acc_%": round(dir_acc, 2),
    }


def run_walk_forward_for_horizon(df: pd.DataFrame, horizon: int) -> tuple:
    """Menjalankan walk-forward expanding window untuk satu horizon."""
    target_col = f"target_ret_h{horizon}"
    valid = df.dropna(subset=ALL_FEATURES + [target_col]).copy().reset_index(drop=True)
    valid["Year"] = valid["Tanggal"].dt.year

    oof_records = []

    for test_year in TEST_YEARS:
        train_mask = valid["Year"] < test_year
        test_mask = valid["Year"] == test_year

        train_df = valid[train_mask].copy()
        test_df = valid[test_mask].copy()

        # Embargo: buang h baris terakhir data latih agar target t_train+h tidak masuk periode uji
        if len(train_df) <= horizon + 50 or len(test_df) == 0:
            continue
        train_df = train_df.iloc[:-horizon].reset_index(drop=True)

        y_train = train_df[target_col].values
        y_test = test_df[target_col].values
        p_base_test = test_df["fcpo_close"].values

        # 1. Naive (Random Walk): prediksi log-return = 0 (harga tetap)
        pred_naive = np.zeros_like(y_test)

        # 2. Ridge (Internal Only)
        scaler_int = StandardScaler()
        X_tr_int = scaler_int.fit_transform(train_df[INTERNAL_FEATURES].values)
        X_te_int = scaler_int.transform(test_df[INTERNAL_FEATURES].values)
        ridge_int = Ridge(alpha=10.0)
        ridge_int.fit(X_tr_int, y_train)
        pred_ridge_int = ridge_int.predict(X_te_int)

        # 3. Ridge (Internal + Eksternal)
        scaler_all = StandardScaler()
        X_tr_all = scaler_all.fit_transform(train_df[ALL_FEATURES].values)
        X_te_all = scaler_all.transform(test_df[ALL_FEATURES].values)
        ridge_all = Ridge(alpha=10.0)
        ridge_all.fit(X_tr_all, y_train)
        pred_ridge_all = ridge_all.predict(X_te_all)

        for i in range(len(test_df)):
            oof_records.append({
                "Tanggal": test_df.iloc[i]["Tanggal"],
                "Horizon": horizon,
                "Fold_Year": test_year,
                "Regime_High_Vol": test_df.iloc[i]["regime_high_vol"],
                "Base_Price": p_base_test[i],
                "Actual_Ret": y_test[i],
                "Pred_Naive": pred_naive[i],
                "Pred_Ridge_Internal": pred_ridge_int[i],
                "Pred_Ridge_All": pred_ridge_all[i],
            })

    oof_df = pd.DataFrame(oof_records)
    summary_rows = []
    for model_name, pred_col in [
        ("Naive (Random Walk)", "Pred_Naive"),
        ("Ridge (Internal Only)", "Pred_Ridge_Internal"),
        ("Ridge (Internal + Eksternal)", "Pred_Ridge_All"),
    ]:
        metrics = compute_metrics(
            oof_df["Actual_Ret"].values,
            oof_df[pred_col].values,
            oof_df["Base_Price"].values,
        )
        summary_rows.append({"Horizon": f"h={horizon}", "Model": model_name, "N_Test": len(oof_df), **metrics})

    return summary_rows, oof_df


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    df = pd.read_csv(DATA_PATH, parse_dates=["Tanggal"])

    all_summary = []
    all_oof = []
    for h in HORIZONS:
        s_rows, oof_df = run_walk_forward_for_horizon(df, h)
        all_summary.extend(s_rows)
        all_oof.append(oof_df)

    summary_df = pd.DataFrame(all_summary)
    oof_all_df = pd.concat(all_oof, ignore_index=True)

    summary_path = os.path.join(OUT_DIR, "baseline_results.csv")
    oof_path = os.path.join(OUT_DIR, "baseline_predictions.csv")
    summary_df.to_csv(summary_path, index=False)
    oof_all_df.to_csv(oof_path, index=False)

    print("=== Hasil Evaluasi Walk-Forward Baseline (2019–2026) ===")
    print(summary_df.to_string(index=False))
    print(f"\nTersimpan: {summary_path}")
    print(f"Tersimpan: {oof_path}")


if __name__ == "__main__":
    main()

