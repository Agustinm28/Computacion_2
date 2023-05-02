import logging
import socket
import subprocess
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Poll, PollOption, KeyboardButton, KeyboardButtonPollType, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
import telegram
from telegram.ext import filters, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, Application, PollAnswerHandler, PollHandler, filters
from telegram.constants import ParseMode
import asyncio
import argparse
import os
import pickle
import time

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

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="start - Set the chat_id so that the bot can send you messages\nhelp - Tells you the bot commands\nscale - Set scale reason (2 default)")

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
            print("First, you must send the command /start to save the chat_id")

def send_message(message):
    asyncio.run(await_message(message))

async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    video = update.message.video

    # Verificar tamaño del video
    if video.file_size > 20 * 1024 * 1024:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The maximum size for the video is 20MB")
        return

    # Guarda el video localmente
    await context.bot.send_message(chat_id=chat_id, text="Uploading video")
    video_file = await context.bot.get_file(video.file_id)
    os.makedirs("./videos", exist_ok=True)
    video_path = "./videos/" + f"{chat_id}_{video.file_unique_id}.{video.mime_type.split('/')[1]}"
    try:
        await video_file.download_to_drive(video_path)
    except Exception as e:
        logging.error(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing video")

    # Envia el video al servidor para ser procesado
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Video uploaded correctly")
    await send_file(file=video_path, scale_method=None)

async def receive_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    image = update.message.photo[-1]

    # Verificar tamaño de la imagen
    if image.file_size > 20 * 1024 * 1024:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="The maximum size for the image is 20MB")
        return

    # Guarda la imagen localmente
    await context.bot.send_message(chat_id=chat_id, text="Uploading image")
    image_file = await context.bot.get_file(image.file_id)
    os.makedirs("./images", exist_ok=True)
    image_path = "./images/" + f"{chat_id}_{image.file_unique_id}.jpeg"
    try:
        await image_file.download_to_drive(image_path)
    except Exception as e:
        logging.error(e)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing image")

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Image uploaded correctly")

    # Aqui necesito que aparezca la encuensta para saber que hacer con la imagen
    questions = ["Interpolation", "AI"]
    message = await context.bot.send_poll(
        chat_id,
        "Select a upscale method:",
        questions,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    # Save some info about the poll the bot_data for later use in receive_poll_answer
    payload = {
        message.poll.id: {
            "questions": questions,
            "message_id": message.message_id,
            "chat_id": chat_id,
            "answers": 0,
            "image_path": image_path
        }
    }
    context.bot_data.update(payload)


async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    file = update.message.document

    if file.mime_type.startswith('video/'):
        # Verificar tamaño del archivo
        if file.file_size > 20 * 1024 * 1024:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="The maximum size for the video is 20MB")
            return
        # Guarda el archivo localmente
        await context.bot.send_message(chat_id=chat_id, text="Uploading video")
        document_file = await context.bot.get_file(file.file_id)
        os.makedirs("./videos", exist_ok=True)
        file_path = "./videos/" + f"{chat_id}_{file.file_unique_id}.{file.mime_type.split('/')[1]}"
        try:
            await document_file.download_to_drive(file_path)
        except Exception as e:
            logging.error(e)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing video")

        # Envia el archivo al servidor para ser procesado
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Video uploaded correctly")
        await send_file(file=file_path, scale_method=None)
    elif file.mime_type.startswith('image/'):
        # Verificar tamaño del archivo
        if file.file_size > 20 * 1024 * 1024:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="The maximum size for the image is 20MB")
            return
        await context.bot.send_message(chat_id=chat_id, text="Uploading image")
        document_file = await context.bot.get_file(file.file_id)
        os.makedirs("./images", exist_ok=True)
        file_path = "./images/" + f"{chat_id}_{file.file_unique_id}.{file.mime_type.split('/')[1]}"
        try:
            await document_file.download_to_drive(file_path)
        except Exception as e:
            logging.error(e)
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Error processing image")

        await context.bot.send_message(chat_id=update.effective_chat.id, text="Image uploaded correctly")

        # Aqui necesito que aparezca la encuensta para saber que hacer con la imagen
        questions = ["Interpolation", "AI"]
        message = await context.bot.send_poll(
            chat_id,
            "Select a upscale method:",
            questions,
            is_anonymous=False,
            allows_multiple_answers=False,
        )
        # Save some info about the poll the bot_data for later use in receive_poll_answer
        payload = {
            message.poll.id: {
                "questions": questions,
                "message_id": message.message_id,
                "chat_id": chat_id,
                "answers": 0,
                "image_path": file_path
            }
        }
        context.bot_data.update(payload)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="File type not recognized")
        return

async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Save a user's poll vote and send the image file"""
    answer = update.poll_answer
    poll_id = answer.poll_id
    # Get the poll from the bot_data
    poll = context.bot_data.get(poll_id)
    # If the poll is not found, return
    if poll is None:
        return
    # Get the selected option ids
    selected_options = answer.option_ids
    option = selected_options[0]
    # Get the image path from the poll
    image_path = poll["image_path"]
    # Send the image file to be processed
    await send_file(file=image_path, scale_method=option)

async def send_file(file, scale_method):
    HOST, PORT = args.ip, int(args.port)

    with open(file, "rb") as f:
        print("[SERIALIZING] Loading object") 
        filename = os.path.basename(file)
        file_data = f.read()
        file_obj = {'filename':filename, 'data':file_data, 'scale':scale_method}
        file_pickle = pickle.dumps(file_obj) 
        print("[SERIALIZING] Pickle object loaded")
        f.close()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((HOST, PORT))
        print(f"[CONNECT] Conexion establecida con {HOST} en el puerto {PORT}")
        print("[SENDING FILE]")        
        sock.sendall(file_pickle)
        sock.close()
        os.remove(file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Telegram Bot')
    parser.add_argument('-ip', type=str, default='127.0.0.1', help='IP of the process server')
    parser.add_argument('-port', '-p', type=int, default=5556, help='Port of the process server')
    args = parser.parse_args()

    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    poll_answer = PollAnswerHandler(receive_poll_answer)

    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(poll_answer)
    application.add_handler(MessageHandler(filters.VIDEO, receive_video))
    application.add_handler(MessageHandler(filters.PHOTO, receive_image))
    application.add_handler(MessageHandler(filters.ATTACHMENT, receive_file))
    
    
    application.run_polling()