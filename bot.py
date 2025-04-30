
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from modules.data_loader import load_all_data
from modules.ml_engine import prepare_dataset, train_model, predict_today
from modules.logger import log_prediction, get_stats, update_actual_returns

# Настройки логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Переменные окружения или напрямую токен
TOKEN = os.environ.get("TOKEN") 
PORT = int(os.environ.get("PORT", "8443"))

# Telegram
app = Application.builder().token(TOKEN).build()

# Подписчики
subscribers = set()

# Команды
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Я умный инвест-бот. Используй /forecast и /subscribe.")

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribers.add(chat_id)
    await update.message.reply_text("✅ Вы подписались на прогнозы!")

async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text("⏳ Загружаю данные и считаю прогноз...")
        data = load_all_data()
        dataset = prepare_dataset(data)
        model, scaler = train_model(dataset)
        predictions = predict_today(model, scaler, data)

        if not predictions:
            await update.message.reply_text("⚠️ Недостаточно данных для прогноза.")
            return

        best = predictions[0]
        log_prediction(best[0], best[1], best[1])  # пока одинаково
        await update.message.reply_text(f"📈 Лидер дня: {best[0]} с вероятностью роста {best[1]*100:.2f}%")
    except Exception as e:
        logger.error(f"Ошибка в forecast: {e}")
        await update.message.reply_text(f"❌ Ошибка при прогнозе: {e}")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        update_actual_returns()
        summary = get_stats()
        await update.message.reply_text(summary)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка при получении статистики: {e}")

# Рассылка по подписке
def send_forecast_to_all():
    import asyncio
    async def send():
        try:
            data = load_all_data()
            dataset = prepare_dataset(data)
            model, scaler = train_model(dataset)
            predictions = predict_today(model, scaler, data)
            if predictions:
                best = predictions[0]
                log_prediction(best[0], best[1], best[1])
                text = f"📊 Прогноз дня: {best[0]} с вероятностью роста {best[1]*100:.2f}%"
                for user_id in subscribers:
                    try:
                        asyncio.create_task(app.bot.send_message(chat_id=user_id, text=text))
                    except Exception as err:
                        logger.error(f"Ошибка отправки пользователю {user_id}: {err}")
        except Exception as e:
            logger.error(f"Ошибка в автоматическом прогнозе: {e}")
    asyncio.run(send())

# Планировщик
scheduler = BackgroundScheduler()
scheduler.add_job(send_forecast_to_all, "cron", hour=10, minute=0)
scheduler.start()

# Регистрация команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("subscribe", subscribe))
app.add_handler(CommandHandler("forecast", forecast))
app.add_handler(CommandHandler("stats", stats))

# Старт бота
if __name__ == "__main__":
    print("🤖 ML-инвест-бот с подпиской запущен")
    app.run_polling()
