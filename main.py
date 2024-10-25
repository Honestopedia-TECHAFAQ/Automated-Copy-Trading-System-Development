import os
import time
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from telegram import Update, Bot
from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder
import streamlit as st
from threading import Thread, Timer
from PIL import Image
import pytesseract
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_credentials():
    """Load user credentials from an encrypted file or environment variables."""
    key = os.environ.get("CREDENTIALS_KEY")  
    fernet = Fernet(key)
    
    with open('encrypted_credentials.json', 'rb') as file:
        encrypted_data = file.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data)

class QuotexTradingBot:
    def __init__(self, telegram_bot):
        options = webdriver.ChromeOptions()
        options.headless = True
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.is_logged_in = False
        self.last_trade_amount = 0.0
        self.last_trade_result = None  
        self.trade_history = []  
        self.martingale_steps = 1  
        self.telegram_bot = telegram_bot 

    def login(self, username, password):
        """Login to the Quotex platform."""
        try:
            if not self.is_logged_in:
                self.driver.get('https://quotex.com')  
                username_field = self.driver.find_element(By.NAME, 'login')  
                password_field = self.driver.find_element(By.NAME, 'password')  
                
                username_field.clear()
                username_field.send_keys(username)
                password_field.clear()
                password_field.send_keys(password)

                login_button = self.driver.find_element(By.XPATH, '//button[contains(text(), "Login")]')  
                login_button.click()
                time.sleep(5)  
                self.is_logged_in = True
                logging.info("Logged in successfully!")
                self.telegram_bot.send_message(chat_id=self.telegram_bot.chat_id, text="Successfully logged in!")  
        except Exception as e:
            logging.error(f"Login failed: {e}")
            self.telegram_bot.send_message(chat_id=self.telegram_bot.chat_id, text=f"Login failed: {e}")  

    def execute_trade(self, trade_type, amount):
        """Execute the trade based on the trade_type ('buy' or 'sell') and amount."""
        try:
            self.set_trade_amount(amount)
            if trade_type == 'buy':
                buy_button = self.driver.find_element(By.XPATH, 'xpath_of_buy_button') 
                buy_button.click()
                self.check_trade_result(trade_type, amount)  
            elif trade_type == 'sell':
                sell_button = self.driver.find_element(By.XPATH, 'xpath_of_sell_button')  
                sell_button.click()
                self.check_trade_result(trade_type, amount)  
            logging.info(f"{trade_type.capitalize()} trade executed with amount {amount}!")
            self.telegram_bot.send_message(chat_id=self.telegram_bot.chat_id, text=f"{trade_type.capitalize()} trade executed with amount {amount}!")  
            self.last_trade_amount = amount
        except Exception as e:
            logging.error(f"Trade execution failed: {e}")
            self.telegram_bot.send_message(chat_id=self.telegram_bot.chat_id, text=f"Trade execution failed: {e}")  

    def check_trade_result(self, trade_type, amount):
        """Simulated check for trade result (this should be replaced with actual logic)."""
        import random
        result = random.choice(['win', 'loss'])
        self.trade_history.append((trade_type, amount, result))  
        if result == 'loss':
            logging.info("Trade result: Loss")
            self.last_trade_result = 'loss'
            self.telegram_bot.send_message(chat_id=self.telegram_bot.chat_id, text=f"Trade result: Loss for amount {amount}")  
        else:
            logging.info("Trade result: Win")
            self.last_trade_result = 'win'
            self.last_trade_amount = 0  
            self.telegram_bot.send_message(chat_id=self.telegram_bot.chat_id, text=f"Trade result: Win for amount {amount}")  

    def martingale_trade(self, trade_type):
        """Implement the Martingale strategy for trade execution."""
        if self.last_trade_result == 'loss':
            new_amount = self.last_trade_amount * 2 if self.last_trade_amount > 0 else 1 
        else:
            new_amount = self.last_trade_amount 
        logging.info(f"Applying Martingale strategy: New trade amount is {new_amount}")
        self.execute_trade(trade_type, new_amount)

    def set_trade_amount(self, amount):
        """Set the trade amount."""
        amount_input = self.driver.find_element(By.XPATH, 'xpath_of_amount_input') 
        amount_input.clear()
        amount_input.send_keys(amount)

    def set_martingale_steps(self, steps):
        """Set the martingale steps.""" 
        self.martingale_steps = steps

    def close(self):
        """Close the browser."""
        self.driver.quit()  

class TelegramBot:
    def __init__(self, token, chat_id):
        self.bot = Bot(token)
        self.chat_id = chat_id
        self.updater = ApplicationBuilder().token(token).build()  

        self.start_handlers()

    def start_handlers(self):
        """Set up message and image handlers."""
        self.updater.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))  
        self.updater.add_handler(MessageHandler(filters.PHOTO, self.handle_image)) 

    def start(self):
        self.updater.run_polling()

    def stop(self):
        self.updater.stop()

    def handle_message(self, update: Update, context):
        message = update.message.text
        self.process_signal(message)

    def handle_image(self, update: Update, context):
        """Handle incoming images and extract signals."""
        file = context.bot.getFile(update.message.photo[-1].file_id)  
        file.download('temp_image.jpg') 
        image = Image.open('temp_image.jpg')
        extracted_text = pytesseract.image_to_string(image)  
        logging.info(f"Extracted text from image: {extracted_text}")
        self.process_signal(extracted_text) 

    def process_signal(self, message):
        """Process incoming trading signals."""
        message = message.strip().lower() 
        parts = message.split()
        
        if len(parts) < 2:
            logging.error("Invalid signal format.")
            return
        
        trade_type = parts[0]
        try:
            amount = float(parts[1])
        except ValueError:
            logging.error("Invalid amount format.")
            return
        
        if len(parts) > 2:
            if parts[2].isnumeric():  
                delay = int(parts[2]) * 60
                Timer(delay, self.trading_bot.execute_trade, [trade_type, amount]).start()
                logging.info(f"Scheduled {trade_type} trade with amount {amount} in {parts[2]} minutes.")
            elif parts[2] in ["1m", "2m"]:  
                interval = int(parts[2][0])
                target_time = datetime.now() + timedelta(minutes=interval)
                delay_seconds = (target_time - datetime.now()).total_seconds()
                Timer(delay_seconds, self.trading_bot.execute_trade, [trade_type, amount]).start()
                logging.info(f"Scheduled {trade_type} trade with amount {amount} for {parts[2]}.")
        else:
            self.trading_bot.execute_trade(trade_type, amount)
            logging.info(f"Executed {trade_type} trade with amount {amount}")
            
        if trade_type == "martingale":
            self.trading_bot.martingale_trade(trade_type)

def run_streamlit():
    st.title("Quotex Trading Bot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")  
    telegram_token = st.text_input("Telegram Bot Token")
    chat_id = st.text_input("Telegram Chat ID")

    if st.button("Start Trading Bot"):
        if username and password and telegram_token and chat_id:
            telegram_bot = TelegramBot(telegram_token, chat_id) 
            trading_bot = QuotexTradingBot(telegram_bot)  
            trading_bot.login(username, password) 
            Thread(target=telegram_bot.start).start()
            st.success("Trading bot started successfully!")
        else:
            st.error("Please fill in all fields.")

if __name__ == "__main__":
    run_streamlit()
