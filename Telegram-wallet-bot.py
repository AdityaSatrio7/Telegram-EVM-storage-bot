import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import psycopg2
from web3 import Web3
import re
import os
from datetime import datetime

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
WALLET = 0

# Database connection parameters - adjust as needed
DB_HOST = "localhost"
DB_NAME = "telegram_bot"
DB_USER = "postgres"
DB_PASS = "your_password_here"
DB_PORT = "5432"

# Telegram bot token
TOKEN = "your_telegram_bot_token_here"

# Function to connect to the database
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )
    return conn

# Function to check if address is a valid EVM address
def is_valid_evm_address(address):
    # Check if it matches the Ethereum address format (0x followed by 40 hex characters)
    if not re.match(r'^0x[a-fA-F0-9]{40}$', address):
        return False
    
    # Use Web3 to check address checksum (optional but recommended)
    try:
        return Web3.is_address(address)
    except:
        # If Web3 validation fails, fall back to regex match
        return True

# Function to save user data to database
def save_user_data(telegram_id, username, wallet_address):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if user already exists
        cur.execute("SELECT * FROM wallet_users WHERE telegram_id = %s", (telegram_id,))
        user = cur.fetchone()
        
        if user:
            # Update existing user
            cur.execute(
                "UPDATE wallet_users SET username = %s, wallet_address = %s, registration_date = %s WHERE telegram_id = %s",
                (username, wallet_address, datetime.now(), telegram_id)
            )
        else:
            # Insert new user
            cur.execute(
                "INSERT INTO wallet_users (telegram_id, username, wallet_address) VALUES (%s, %s, %s)",
                (telegram_id, username, wallet_address)
            )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Database error: {e}")
        return False

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! 👋\n\n"
        f"Please send me your EVM wallet address."
    )
    return WALLET

# Process wallet address
async def process_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    wallet_address = update.message.text.strip()
    
    # Validate the wallet address
    if not is_valid_evm_address(wallet_address):
        await update.message.reply_text(
            "That doesn't look like a valid EVM wallet address. "
            "Please make sure it starts with '0x' followed by 40 hexadecimal characters.\n\n"
            "Send me your wallet address again:"
        )
        return WALLET
    
    # Save the data
    username = user.username if user.username else ""
    success = save_user_data(user.id, username, wallet_address)
    
    if success:
        await update.message.reply_text(
            f"Thank you! Your wallet address has been successfully recorded. ✅\n\n"
            f"Address: `{wallet_address}`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "Sorry, there was an error saving your information. Please try again later."
        )
    
    return ConversationHandler.END

# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

# Main function
def main():
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WALLET: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_wallet)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    
    # Start the Bot
    application.run_polling()

if __name__ == '__main__':
    main()