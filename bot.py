
import logging
import asyncio
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules.data_loader import load_all_data
from modules.ml_engine import prepare_dataset, train_model, predict_today
from modules.logger import log_prediction, update_actual_returns, get_stats
from datetime import datetime, time, timedelta

TOKEN = '7904337093:AAFtX2tjlkiyfqgAyBcgU5d4qsthdI74bkM'
SUBSCRIBERS_FILE = 'subscribers.json'

logging.basicConfig(level=logging.INFO)

# === Подписка ===
def add_subscriber(chat_id):
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            subs = json.load(f)
    except:
        subs = []
    if chat_id not in subs:
        subs.append(chat_id)
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(subs, f)

def remove_subscriber(chat_id):
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            subs = json.load(f)
        subs = [cid for cid in subs if cid != chat_id]
        with open(SUBSCRIBERS_FILE, 'w') as f:
            json.dump(subs, f)
    except:
        pass

def get_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

# === Команды ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я умный инвест-бот с машинным обучением.\n"
        "📩 Используй /subscribe чтобы получать прогнозы автоматически.\n"
        "📊 Команды:\n"
        "/forecast — прогноз на сегодня\n"
        "/stats — статистика по прогнозам\n"
        "/unsubscribe — отписаться"
    )

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    add_subscriber(chat_id)
    await update.message.reply_text("✅ Ты подписан на ежедневные прогнозы!")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    remove_subscriber(chat_id)
    await update.message.reply_text("❌ Ты отписался от рассылки прогнозов.")

async def forecast(update: Update = None, context: ContextTypes.DEFAULT_TYPE = None, auto=False, chat_id=None):
    if not auto and update:
        await update.message.reply_text("🔄 Получаю данные и строю прогноз. Подожди немного...")

    try:
        data = load_all_data()
        dataset = prepare_dataset(data)
        model3d, scaler3d = train_model(dataset, horizon="target_3d")
        pred3d = predict_today(model3d, scaler3d, data)
        top_ticker, top_prob3d = pred3d[0]

        model1d, scaler1d = train_model(dataset, horizon="target_1d")
        pred1d_dict = dict(predict_today(model1d, scaler1d, data))
        top_prob1d = pred1d_dict.get(top_ticker, 0)

        log_prediction(top_ticker, top_prob3d, top_prob1d)

        msg = (
            f"📈 *Акция дня:* ${top_ticker}\n"
            f"📊 Прогноз на 3 дня: *{top_prob3d:.1%}*\n"
            f"⚡ Прогноз на завтра: *{top_prob1d:.1%}*\n"
            f"🧠 Основано на анализе 90 дней по 100 акциям"
        )
        if auto:
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(msg, parse_mode='Markdown')

    except Exception as e:
        msg = f"❌ Ошибка при прогнозе: {e}"
        if auto:
            await context.bot.send_message(chat_id=chat_id, text=msg)
        elif update:
            await update.message.reply_text(msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_actual_returns()
    result = get_stats()
    await update.message.reply_text(result)

async def daily_forecast_task(app):
    while True:
        now = datetime.now()
        run_time = datetime.combine(now.date(), time(10, 0))
        if now > run_time:
            run_time += timedelta(days=1)
        wait_seconds = (run_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        subs = get_subscribers()
        for chat_id in subs:
            context = ContextTypes.DEFAULT_TYPE()
            dummy_job = type('Dummy', (), {'chat_id': chat_id})()
            await forecast(context=context, auto=True, chat_id=chat_id)

# === Запуск ===
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("unsubscribe", unsubscribe))
app.add_handler(CommandHandler("forecast", forecast))
app.add_handler(CommandHandler("stats", stats))

print("🤖 ML-инвест-бот с подпиской запущен")
app.run_polling()
