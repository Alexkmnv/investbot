
import pandas as pd
import os
from datetime import datetime, timedelta
import yfinance as yf

LOG_FILE = "predictions_log.csv"

def log_prediction(ticker, prob_3d, prob_1d):
    today = datetime.now().strftime("%Y-%m-%d")
    entry = pd.DataFrame([{
        "date": today,
        "ticker": ticker,
        "prob_3d": prob_3d,
        "prob_1d": prob_1d,
        "actual_1d_return": None,
        "actual_3d_return": None
    }])
    if os.path.exists(LOG_FILE):
        df = pd.read_csv(LOG_FILE)
        df = pd.concat([df, entry], ignore_index=True)
    else:
        df = entry
    df.to_csv(LOG_FILE, index=False)

def update_actual_returns():
    if not os.path.exists(LOG_FILE):
        return None
    df = pd.read_csv(LOG_FILE)
    updated = False
    for i, row in df.iterrows():
        if pd.isna(row["actual_1d_return"]) or pd.isna(row["actual_3d_return"]):
            try:
                start = datetime.strptime(row["date"], "%Y-%m-%d")
                end3 = start + timedelta(days=3)
                data = yf.download(row["ticker"], start=start.strftime("%Y-%m-%d"), end=end3.strftime("%Y-%m-%d"))

                if not data.empty and len(data) > 2:
                    try:
                        open_price = float(data["Open"].iloc[0])
                        close_1d = float(data["Close"].iloc[1])
                        close_3d = float(data["Close"].iloc[2])
                    except Exception as convert_error:
                        print(f"❌ Ошибка преобразования в число: {convert_error}")
                        continue

                    if open_price != 0:
                        df.at[i, "actual_1d_return"] = (close_1d - open_price) / open_price
                        df.at[i, "actual_3d_return"] = (close_3d - open_price) / open_price
                        updated = True
            except Exception as e:
                print(f"Ошибка обновления {row['ticker']}: {e}")
    if updated:
        df.to_csv(LOG_FILE, index=False)

def get_stats():
    if not os.path.exists(LOG_FILE):
        return "Нет данных для статистики"
    df = pd.read_csv(LOG_FILE).dropna()
    if df.empty:
        return "Недостаточно данных для статистики"
    count = len(df)
    avg_prob_3d = df["prob_3d"].mean()
    avg_prob_1d = df["prob_1d"].mean()
    success_1d = (df["actual_1d_return"] > 0).mean()
    success_3d = (df["actual_3d_return"] > 0).mean()
    avg_return_1d = df["actual_1d_return"].mean()
    avg_return_3d = df["actual_3d_return"].mean()

    return (
        f"📊 Прогнозов: {count}\n"
        f"📈 Средняя вероятность роста (3 дня): {avg_prob_3d:.1%}\n"
        f"⚡ Средняя вероятность роста (1 день): {avg_prob_1d:.1%}\n"
        f"✅ Успешных прогнозов (1 день): {success_1d:.1%}\n"
        f"🚀 Успешных прогнозов (3 дня): {success_3d:.1%}\n"
        f"💵 Средний доход за день: {avg_return_1d:.2%}\n"
        f"💵 Средний доход за 3 дня: {avg_return_3d:.2%}"
    )
