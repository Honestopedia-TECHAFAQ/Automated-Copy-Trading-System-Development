from signal import raise_signal
import streamlit as st
from telegram import Update
from telegram.ext import Updater, MessageHandler, filters, CallbackContext
import time
import re
from PIL import Image
import pytesseract
def process_signal(signal, martingale_steps, risk_management):
    """
    Executes trades based on the signal provided. Supports optional Martingale steps.
    
    Args:
        signal (str): The signal message to process (e.g., "buy" or "sell").
        martingale_steps (int): Number of Martingale steps to perform.
        risk_management (bool): Whether to enable risk management.
    """
    position = "buy" if signal.lower().startswith("buy") else "sell" if signal.lower().startswith("sell") else None
    if position:
        st.success(f"Executing {position} trade based on signal: {signal}")
        if risk_management:
            for step in range(1, martingale_steps + 1):
                st.info(f"Applying Martingale step {step}...")
                time.sleep(1)  
                st.success(f"Executed {position} trade at Martingale step {step}.")
        else:
            st.success(f"Executed {position} trade without Martingale.")
    else:
        st.warning("Unknown signal type. Please send a valid buy or sell signal.")
def listen_to_telegram_signals(bot_token, chat_id):
    """
    Listens for incoming signals on the specified Telegram chat.
    
    Args:
        bot_token (str): Telegram bot token.
        chat_id (str): Telegram chat ID to listen for signals.
    
    Returns:
        updater (Updater): The Telegram updater to control the bot.
    """
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher
    def handle_message(update: Update, context: CallbackContext):
        if update.message.photo:
            file = update.message.photo[-1].get_file()
            file.download("signal_image.jpg")
            image = Image.open("signal_image.jpg")
            signal = extract_text_from_image(image) if ocr_enabled else ""
        else:
            signal = update.message.text

        parsed_data = raise_signal(signal)
        if parsed_data:
            asset, direction, duration, execution_time = parsed_data
            st.info(f"Received Signal: Asset={asset}, Direction={direction}, Duration={duration}, Execution Time={execution_time}")
            process_signal(direction, martingale_steps, risk_management)
        else:
            st.warning("Signal could not be parsed. Please ensure it follows the expected format.")
    dispatcher.add_handler(MessageHandler(filters.TEXT | filters.PHOTO, handle_message))
    updater.start_polling()
    return updater

def extract_text_from_image(image):
    """
    Uses OCR techniques to extract text from an image.
    
    Args:
        image (PIL.Image): The image to extract text from.
    
    Returns:
        str: Extracted text from the image.
    """
    text = pytesseract.image_to_string(image)
    return text

st.title("Automated Copy Trading System for Quotex")
st.write("This app processes Telegram signals (text or image) to execute trades on Quotex.")

telegram_token = st.text_input("Enter your Telegram Bot Token")
chat_id = st.text_input("Enter your Chat ID")
st.sidebar.header("Trading Options")
martingale_steps = st.sidebar.number_input("Martingale Steps (1-3)", min_value=1, max_value=3, value=1)
risk_management = st.sidebar.checkbox("Enable Risk Management", value=True)
st.sidebar.header("Signal Parsing Options")
ocr_enabled = st.sidebar.checkbox("Enable OCR for Image Signals", value=True)
if st.button("Start Listening"):
    if telegram_token and chat_id:
        updater = listen_to_telegram_signals(telegram_token, chat_id)
        st.success("Bot is now listening for signals...")
    else:
        st.error("Please provide both the Telegram Bot Token and Chat ID.")
if st.button("Stop Listening"):
    if 'updater' in locals():
        updater.stop()
        st.success("Bot stopped.")
    else:
        st.warning("Bot is not running.")
