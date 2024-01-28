import os
import sys
import asyncio
import tgcrypto
import pyrogram
import requests

API_ID = 7405235  # Replace with your TGCrypto API ID
API_HASH = '5c9541eefe8452186e9649e2effc1f3f'  # Replace with your TGCrypto API Hash

BOT_TOKEN = '6989567311:AAGQpZSTMgko2IpgLRJsCaIQIiALm1hgLzI'  # Replace with your Telegram bot token
PIXELDRAIN_API_KEY = '60a0f36c-70fb-4f12-af49-8984ae2a9d78'  # Replace with your PixelDrain API key

@pyrogram.Client.on_message(filters.command(['start', 'help']))
async def start(client, message):
    await message.reply_text(f"Welcome to the PixelDrain Upload Bot! Use /pixeldrain to upload files to PixelDrain.")

@pyrogram.Client.on_message(filters.command(['pixeldrain']))
async def pixeldrain(client, message):
    # Get the file from the user
    file_id = message.reply_to_message.document.file_id
    file = await client.download_media(file_id)
    # Generate a random filename
    filename = 'temp_file' + str(os.getpid()) + '.bin'

    # Upload the file to PixelDrain
    headers = {
        'Authorization': f'Basic {btoa(":"+PIXELDRAIN_API_KEY)}'
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://api.pixeldrain.com/v1/upload',
            headers=headers,
            data=file
        ) as response:
            if response.status == 20:
                # Get the uploaded file's URL
                data = await response.json()
                url = data['url']

                # Send the file URL to the user
                await message.reply_text(f"File uploaded successfully!\n\nURL: {url}\n\nFile: {filename}")
            else:
                # Handle upload errors
                error_msg = await response.text()
                await message.reply_text(f"Error uploading the file:\n{error_msg}")

    # Clean up the temporary file
    os.remove(filename)

app = pyrogram.Client(
    "PixelDrain Bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

app.run()
