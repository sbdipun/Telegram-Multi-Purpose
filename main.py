import os
from enum import Enum
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import pixeldrain

Bot = Client(
    "Pixeldrain-Bot",
    bot_token=os.environ["BOT_TOKEN"],
    api_id=int(os.environ["API_ID"]),
    api_hash=os.environ["API_HASH"]
)

class States(Enum):
    START = 0
    RENAMING = 1

temporary_storage = {}

@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, update):
    await update.reply_text(
        f"Hello!! {update.from_user.mention}, Please send a file to Upload in PixelDrain.\n\nThis Is Made With Love By DcOoL ❤️❤️❤️",
        quote=True
    )

@Bot.on_message(filters.private & filters.media)
async def media_filter(bot, update):
    message = await update.reply_text("Processing...", quote=True)    
    media = await update.download()
    temporary_storage[update.from_user.id] = media
    await update.reply_text("Please send the new filename for your file (with the proper extension).", quote=True)
    temporary_storage[update.from_user.id + "_state"] = States.RENAMING

@Bot.on_message(filters.private & filters.text & filters.create(lambda _, , query: temporary_storage.get(query.from_user.id + "_state") == States.RENAMING))
async def get_new_filename(bot, update):
    media = temporary_storage[update.from_user.id]
    new_name = update.text
    if not os.path.splitext(new_name)[1]:
        await update.reply_text("Please include the file extension in the new filename.", quote=True)
        return
    new_media_path = os.path.join(os.path.dirname(media), new_name)
    os.rename(media, new_media_path)
    await upload_to_pixeldrain(bot, update, new_media_path)

async def upload_to_pixeldrain(bot, update, media_path):
    message = await update.reply_text("Uploading...", quote=True)
    response = pixeldrain.upload_file(media_path)
    os.remove(media_path)
    if response["success"]:
        data = pixeldrain.info(response["id"])
        text = f"File Name: {data['name']}" + "\n"
        text += f"Download Page: https://pixeldrain.com/u/{data['id']}" + "\n"
        text += f"Direct Download Link: https://pixeldrain.com/api/file/{data['id']}" + "\n"
        text += f"Upload Date: {data['date_upload']}" + "\n"
        text += f"Last View Date: {data['date_last_view']}" + "\n"
        text += f"Size: {data['size']}" + "\n"
        text += f"Total Views: {data['views']}" + "\n"
        text += f"Bandwidth Used: {data['bandwidth_used']}" + "\n"
        text += f"Mime Type: {data['mime_type']}"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Open Link", url=f"https://pixeldrain.com/u/{data['id']}"),
             InlineKeyboardButton(text="Share Link",
                                  url=f"https://telegram.me/share/url?url=https://pixeldrain.com/u/{data['id']}")],
            [InlineKeyboardButton(text="Join Updates Channel", url="https://telegram.me/kingsb007")]
        ])
        await message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await message.edit_text(f"Upload failed: {response['message']}")
    del temporary_storage[update.from_user.id]
    del temporary_storage[update.from_user.id + "_state"]

Bot.run()
