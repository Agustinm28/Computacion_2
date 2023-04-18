import logging
from telegram import Update
import telegram
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import asyncio

global chat_id

with open('./data/BOT_CREDENTIALS.txt', 'r') as f:
    token = str(f.read())
chat_id = None

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global chat_id
    chat_id = update.effective_chat.id
    with open('./data/chat_id.txt', 'w') as f:
        f.write(str(chat_id))
    await context.bot.send_message(chat_id=chat_id, text="Hi! I have saved the chat_id for this chat.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('./data/status.txt') as f:
        status = f.read()
    with open('./data/status_nsfw.txt') as f:
        status_nsfw = f.read()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=status)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=status_nsfw)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="start - Set the chat_id so that the bot can send you messages\nhelp - Tells you the bot commands\nscale - Set scale reason (2 default)")

async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Obtén la información del archivo de la imagen
    photo_file = update.message.photo[-1].get_file()
    
    # Descarga el archivo de la imagen
    photo_path = './imagen.jpg'
    photo_file.download(custom_path=photo_path)
    
    # Envía un mensaje confirmando la recepción de la imagen
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Image receive!")

async def get_me():
    bot = telegram.Bot(token)
    async with bot:
        print(await bot.get_me())

async def get_updates():
    bot = telegram.Bot(token)
    async with bot:
        print((await bot.get_updates())[0])

async def await_message(message):
    global chat_id
    bot = telegram.Bot(token)
    async with bot:
        try:
            with open('./data/chat_id.txt', 'r') as f:
                chat_id = int(f.read())
            await bot.send_message(chat_id=chat_id, text=message)
        except FileNotFoundError or ValueError:
            print("First, you must send the command /start to save the chat_id.")

def send_message(message):
    asyncio.run(await_message(message))

def main():
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    status_handler = CommandHandler('status', status)
    help_handler = CommandHandler('help', help)
    receive_image_handler = CommandHandler('receive_image', receive_image)
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(status_handler)
    application.add_handler(receive_image_handler)
    
    application.run_polling()

if __name__ == '__main__':
    main()