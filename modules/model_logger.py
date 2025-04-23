
import os
import pandas as pd
from datetime import datetime
from sklearn.metrics import accuracy_score

LOG_PATH = "model_accuracy_log.csv"

def log_model_performance(y_true, y_pred):
    date = datetime.now().strftime("%Y-%m-%d")
    accuracy = accuracy_score(y_true, y_pred)
    new_entry = pd.DataFrame([{"date": date, "accuracy": accuracy}])

    if os.path.exists(LOG_PATH):
        df = pd.read_csv(LOG_PATH)
        df = pd.concat([df, new_entry], ignore_index=True)
    else:
        df = new_entry

    df.to_csv(LOG_PATH, index=False)

def get_accuracy_history():
    if not os.path.exists(LOG_PATH):
        return "История точности модели пока пуста."
    df = pd.read_csv(LOG_PATH)
    if df.empty:
        return "История точности модели пока пуста."
    latest = df.tail(5)
    summary = "📈 История точности модели:
"
    for _, row in latest.iterrows():
        summary += f"{row['date']}: {row['accuracy']:.2%}
"
    return summary
