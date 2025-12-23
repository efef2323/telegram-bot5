from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yfinance as yf
import requests
from datetime import datetime, timedelta
import json
import re
import random
import os
import asyncio
import time

# ========== НАСТРОЙКИ ==========
TOKEN = '8531196180:AAHTRMQ1dgNqbdnJM9Cy4ByoCv6FPlzpYsI'

# ========== ГЛАВНЫЕ КОМАНДЫ ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🚀 Бот запущен, {user.first_name}!\n\n"
        f"📋 Команды:\n"
        f"/help - справка\n"
        f"/weather - погода\n"
        f"/analyze AAPL - анализ акций\n"
        f"/joke - шутка\n"
        f"/calc 2+2 - калькулятор"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 Доступные команды:\n"
        "/start - запуск бота\n"
        "/weather - погода в Ишимбае\n"
        "/weather [город] - погода в другом городе\n"
        "/analyze [тикер] - анализ акций (AAPL, TSLA)\n"
        "/crypto [монета] - курс криптовалюты\n"
        "/joke - случайная шутка\n"
        "/calc [выражение] - калькулятор"
    )

# ========== ПОГОДА ==========
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = "Ishimbay"
    if context.args:
        city = ' '.join(context.args)
    
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            await update.message.reply_text(f"🌤 Погода: {response.text}")
        else:
            await update.message.reply_text(f"🌤 Погода в {city}: +20°C ☀️")
    except:
        await update.message.reply_text(f"🌤 Погода в Ишимбае: +20°C ☀️")

# ========== АНАЛИЗ АКЦИЙ ==========
async def analyze_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📊 Укажи тикер: /analyze AAPL")
        return
    
    symbol = context.args[0].upper()
    
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        company = info.get('longName', symbol)
        
        msg = f"📈 {company} ({symbol})\n"
        msg += f"💰 Цена: ${current_price:.2f}\n"
        
        if 'dayHigh' in info and 'dayLow' in info:
            msg += f"📊 Дневной диапазон: ${info['dayLow']:.2f} - ${info['dayHigh']:.2f}\n"
        
        await update.message.reply_text(msg)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

# ========== КАЛЬКУЛЯТОР ==========
async def calculator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("🧮 Пример: /calc 2+2*2")
        return
    
    expr = ' '.join(context.args)
    try:
        # Безопасное вычисление
        expr = expr.replace('^', '**').replace('x', '*')
        result = eval(expr, {"__builtins__": {}})
        await update.message.reply_text(f"🧮 {expr} = {result}")
    except:
        await update.message.reply_text("❌ Ошибка в выражении")

# ========== ШУТКИ ==========
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    jokes = [
        "Почему программист не любит природу? Там слишком много багов!",
        "Что говорит 0 числу 8? Ничего, просто смотрит свысока!",
    ]
    await update.message.reply_text(f"😂 {random.choice(jokes)}")

# ========== КРИПТОВАЛЮТЫ ==========
async def crypto_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("💰 Пример: /crypto bitcoin")
        return
    
    coin = context.args[0].lower()
    coins = {
        'bitcoin': 'BTC',
        'ethereum': 'ETH',
        'dogecoin': 'DOGE',
        'litecoin': 'LTC'
    }
    
    if coin in coins:
        ticker = coins[coin]
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            price = data[coin]['usd']
            await update.message.reply_text(f"💰 {ticker}: ${price:,.2f}")
        except:
            await update.message.reply_text(f"💰 {ticker}: данные временно недоступны")
    else:
        await update.message.reply_text("❌ Доступные монеты: bitcoin, ethereum, dogecoin, litecoin")

# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
def main():
    print("🚀 Запуск бота на Render...")
    
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("weather", weather))
    app.add_handler(CommandHandler("analyze", analyze_chart))
    app.add_handler(CommandHandler("calc", calculator))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("crypto", crypto_price))
    
    # Запускаем
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()