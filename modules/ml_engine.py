
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

def create_features(df):
    df[["Open", "High", "Low", "Close", "Volume"]] = df[["Open", "High", "Low", "Close", "Volume"]].apply(pd.to_numeric, errors="coerce")
    df["return"] = df["Close"].pct_change()
    df["sma_5"] = df["Close"].rolling(window=5).mean()
    df["sma_10"] = df["Close"].rolling(window=10).mean()
    df["volatility"] = df["Close"].rolling(window=5).std()
    df = df.dropna()
    return df

def label_data(df, horizon=3):
    df["target_3d"] = df["Close"].shift(-horizon) > df["Close"]
    df["target_1d"] = df["Close"].shift(-1) > df["Close"]
    return df

def prepare_dataset(data_dict):
    all_rows = []
    for ticker, df in data_dict.items():
        df = create_features(df)
        if df.empty:
            continue
        df = label_data(df)
        df["ticker"] = ticker
        all_rows.append(df)

    if not all_rows:
        print("⚠️ prepare_dataset: нет подходящих данных для обучения")
        return pd.DataFrame()

    full_data = pd.concat(all_rows)
    full_data = full_data.dropna()

    if full_data.empty:
        print("⚠️ prepare_dataset: после очистки данных ничего не осталось!")
    return full_data

def train_model(data, horizon="target_3d"):
    if data.empty:
        raise ValueError("Датасет пустой, модель не может быть обучена.")

    features = ["Open", "High", "Low", "Close", "Volume", "return", "sma_5", "sma_10", "volatility"]
    X = data[features]
    y = data[horizon]

    if len(X) < 5:
        raise ValueError(f"Недостаточно данных: только {len(X)} строк.")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss")
    model.fit(X_train_scaled, y_train)

    return model, scaler

def predict_today(model, scaler, data_dict):
    predictions = []
    for ticker, df in data_dict.items():
        df = create_features(df)
        if df.empty:
            continue
        latest = df.iloc[-1:]
        X = latest[["Open", "High", "Low", "Close", "Volume", "return", "sma_5", "sma_10", "volatility"]]
        X_scaled = scaler.transform(X)
        prob = model.predict_proba(X_scaled)[0][1]
        predictions.append((ticker, prob))
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions
