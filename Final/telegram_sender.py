import requests

# Modulo destinado a enviar mensajes o archivos al usuario de Telegram

with open('./data/BOT_CREDENTIALS.txt', 'r') as f:
    token = str(f.read())

def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    response = requests.post(url, data=data)


def send_file(file_path, filetype, chat_id):
    if filetype.startswith('video/'):
        send_message(chat_id, "Upscaled video:")
        url = f"https://api.telegram.org/bot{token}/sendVideo"
        files = {"video": open(file_path, "rb")}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
    else:
        send_message(chat_id, "Upscaled Image:")
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {"photo": open(file_path, "rb")}
        data = {"chat_id": chat_id}
        response = requests.post(url, files=files, data=data)
    print(f'[SENDING] File sended')