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
        send_message(chat_id, "Downloading upscaled video...")
    elif filetype.startswith('image/'):
        send_message(chat_id, "Downloading upscaled image...")
    try:
        url = f"https://api.telegram.org/bot{token}/sendDocument"
        files = {"document": open(file_path, "rb")}
        data = {"chat_id": chat_id, "disable_content_type_detection": True}
        response = requests.post(url, files=files, data=data)
        print(response)
        print(f'[SENDING] File sended')
    except requests.exceptions.RequestException as e:
        print(f"Error sending the file: {e}")
        send_message(chat_id, "There was an error sending the file")