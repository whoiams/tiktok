import os
import re
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from pytube import YouTube


# Define your Telegram bot token
TOKEN = '6162835664:AAF82yhi5W7jJe8VJxeLTk10xKGCLWBn6Fk'

# Define the command handler for the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the TikTok downloader bot!")

# Define the function to handle text messages
def handle_message(update, context):
    message_text = update.message.text
    
    # Check if the message text is a valid TikTok video URL
    if re.match(r'^(https?://)?(www\.)?tiktok\.com/.*$', message_text):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Downloading TikTok video...")
        
        # Download the TikTok video using requests library
        video_url = get_video_url(message_text)
        response = requests.get(video_url, stream=True)
        
        # Get the filename from the URL
        filename = os.path.basename(video_url)
        
        # Save the video to a file
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        
        # Send the downloaded video file
        context.bot.send_video(chat_id=update.effective_chat.id, video=open(filename, 'rb'))
        
        # Remove the downloaded video file
        os.remove(filename)
        
        # Download the TikTok audio using pytube library
        audio_url = get_audio_url(message_text)
        audio_filename = 'audio_' + os.path.basename(audio_url)
        YouTube(audio_url).streams.first().download(filename='audio', filename_prefix='')
        os.rename(audio_filename, audio_filename + '.mp3')
        
        # Send the downloaded audio file
        context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(audio_filename + '.mp3', 'rb'))
        
        # Remove the downloaded audio file
        os.remove(audio_filename + '.mp3')
        
    else:
        # Send an error message if the message is not a valid TikTok URL
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a valid TikTok video URL.")


# Define a helper function to get the TikTok video URL
def get_video_url(url):
    # Make a request to the TikTok URL
    response = requests.get(url)
    
    # Search for the video URL in the response HTML
    match = re.search(r'"video":{"url":"(.*?)"', response.text)
    
    if match:
        video_url = match.group(1)
        return video_url.replace('\\u0026', '&')

    return None


# Define a helper function to get the TikTok audio URL
def get_audio_url(url):
    # Make a request to the TikTok URL
    response = requests.get(url)
    
    # Search for the audio URL in the response HTML
    match = re.search(r'"audio":{"url":"(.*?)"', response.text)
    
    if match:
        audio_url = match.group(1)
        return audio_url.replace('\\u0026', '&')

    return None


# Create an instance of the Updater class and pass it the Telegram bot token
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Register the command handlers
dispatcher.add_handler(CommandHandler("start", start))

# Register the message handler
dispatcher.add_handler(MessageHandler(Filters.text, handle_message))

# Start the bot
updater.start_polling()
