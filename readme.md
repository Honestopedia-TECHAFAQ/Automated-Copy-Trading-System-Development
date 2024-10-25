# Quotex Trading Bot

This Quotex Trading Bot automates trading activities on the Quotex platform by processing signals received via a Telegram bot. The bot can execute trades based on the received signals and incorporates a Martingale strategy for risk management.

## Features

- **Login to Quotex**: Automatically log into the Quotex trading platform using provided credentials.
- **Trade Execution**: Execute buy and sell trades based on signals received via Telegram.
- **Signal Processing**: Accepts trading signals as text messages or images, extracts relevant information, and executes trades.
- **Martingale Strategy**: Implements a Martingale strategy to double down on losing trades.
- **Trade Logging**: Keeps a history of trades executed, including results (win/loss).

## Requirements

- Python 3.x
- Chrome WebDriver (for Selenium)
- Required Python packages (see below)
- Quotex account credentials
- Telegram bot token and chat ID

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/quotex-trading-bot.git
   cd quotex-trading-bot
   ```

**Install required packages** :

```
pip install -r requirements.txt

```


 **Set up environment variables** :

Set the following environment variable for your encryption key:


```
export CREDENTIALS_KEY='your-encryption-key'

```


* **Add your credentials** :
  Create a file named `encrypted_credentials.json` containing your Quotex credentials in encrypted format.
* **Set up your Telegram bot** :
* Create a new bot via [BotFather]() on Telegram and obtain the bot token.
* Get your chat ID by messaging the bot or using the Telegram API.


## Usage

1. **Run the bot** :
   Start the Streamlit web interface to run the bot:

   ```
   py -m streamlit run main.py

   Or

   streamlit run app.py

   ```


1. **Enter your credentials** :

* Input your Quotex username and password.
* Input your Telegram bot token and chat ID.
* Click on "Start Trading Bot" to initiate the trading session.

1. **Sending signals** :

* Send trading signals to your Telegram bot in the format:
  * `buy <amount>` or `sell <amount>`
  * Optionally, you can specify a delay in minutes: `buy <amount> <delay_in_minutes>`.
* For Martingale trading, send `martingale buy` or `martingale sell`.

1. **Monitor trades** :
   The bot will execute trades based on the received signals and log the results (win/loss) in the console.

## Important Notes

* **Testing** : It is highly recommended to test the bot in a controlled environment before deploying it in live trading scenarios.
* **Dependencies** : Ensure you have the correct version of Chrome installed that matches the Chrome WebDriver version you are using.
* **Web Scraping** : The bot uses Selenium for web scraping; make sure to comply with Quotex's terms of service.
