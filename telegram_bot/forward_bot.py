import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

# Set up logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get environment variables
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = int(os.getenv('CHAT_ID'))  # Ensure CHAT_ID is an integer

# Log the environment variables for debugging
logger.debug(f"Telegram Token: {BOT_TOKEN}")
logger.debug(f"Chat ID (CHAT_ID): {CHAT_ID}")

if not CHAT_ID:
    logger.error("Error: CHAT_ID is empty. Please set the CHAT_ID environment variable.")

# Create the bot application
app = Application.builder().token(BOT_TOKEN).build()

# Define message handler
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Skip forwarding if the message is from the owner's chat ID
    if user_id == CHAT_ID:
        logger.debug("Message from owner's chat ID. Skipping forwarding.")
        return

    # Send message with username and ID of the sender
    await context.bot.send_message(chat_id=CHAT_ID, text=f"Message from {username} (ID: {user_id}): {user_message}")
    await update.message.reply_text("Your message has been sent to the owner.")

# Command handler for /send
async def send_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Only allow the command for the owner
    if update.message.from_user.id != CHAT_ID:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    # Parse command arguments
    try:
        target_id = context.args[0]
        message = " ".join(context.args[1:])

        # Ensure the target ID is an integer
        target_id = int(target_id)

        # Send the message to the specified target ID
        await context.bot.send_message(chat_id=target_id, text=message)
        await update.message.reply_text("Message sent successfully.")
    except (IndexError, ValueError):
        await update.message.reply_text("Invalid format. Use /send <number_id> <message>.")
    except Exception as e:
        await update.message.reply_text(f"Failed to send message: {e}")

# Add handlers
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_message))
app.add_handler(CommandHandler("send", send_command))

# Start polling
app.run_polling()
