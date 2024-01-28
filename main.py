import os
import requests
import shutil
from urllib.parse import urlparse
import pixeldrain
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

Bot = Client(
    "Pixeldrain-Bot",
    bot_token = os.environ["BOT_TOKEN"],
    api_id = int(os.environ["API_ID"]),
    api_hash = os.environ["API_HASH"]
)


@Bot.on_message(filters.private & filters.command("start"))
async def start(bot, update):
    await update.reply_text(
        text=f"Hello!! {update.from_user.mention}, Please send a file to Upload in PixelDrain.\n\nThis Is Made With Love By DcOoL ❤️❤️❤️",
        disable_web_page_preview=True,
        quote=True
    )

async def download_from_url(url, download_folder="downloads"):
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    local_filepath = os.path.join(download_folder, filename)
    os.makedirs(download_folder, exist_ok=True)
    with requests.get(url, stream=True) as r:
        with open(local_filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    return local_filepath

@Bot.on_message(filters.private & filters.text)
async def text_filter(bot, update):
    text = update.text
    if text.startswith("http"):
        try:
            message = await update.reply_text("Downloading file from link...", quote=True)
            local_filepath = await download_from_url(text)
            await update.reply_text(
                "Please send the new filename for your file (with the proper extension).",
                quote=True,
            )
        except Exception as e:
            await message.edit_text(f"Failed to download file: {str(e)}")
            return
        await upload_file_to_pixeldrain(update, local_filepath, message)
    else:
        await update.reply_text("Please send a valid PixelDrain link or any direct download link.")

async def upload_file_to_pixeldrain(update, filepath, message):
    try:
        await message.edit_text("Uploading to PixelDrain...", disable_web_page_preview=True)
        response = pixeldrain.upload_file(filepath)
        try:
            os.remove(filepath)
        except:
            pass
        if response["success"]:
            await message.edit_text("Uploaded Successfully!", disable_web_page_preview=True)
        else:
            await message.edit_text(f"Failed to upload to PixelDrain: {response.get('message', 'Unknown error')}")
    except Exception as e:
        await message.edit_text(f"An error occurred: {str(e)}")

@Bot.on_message(filters.private & filters.media)
async def media_filter(bot, update):
    
    logs = []
    message = await update.reply_text(
        text="`Processing...`",
        quote=True,
        disable_web_page_preview=True
    )
    
    try:
        # download
        try:
            await message.edit_text(
                text="`Downloading...`",
                disable_web_page_preview=True
            )
        except:
            pass
        media = await update.download()
        logs.append("Download Successfully")
        await update.reply_text(
        "Please send the new filename for your file (with the proper extension).",
        quote=True,
    )

        # upload
        try:
            await message.edit_text(
                text="`Uploading...`",
                disable_web_page_preview=True
            )
        except:
            pass
        response = pixeldrain.upload_file(media)
        
        try:
            os.remove(media)
        except:
            pass
        try:
            await message.edit_text(
                text="`Uploaded Successfully!`",
                disable_web_page_preview=True
            )
        except:
            pass
        logs.append("Upload Successfully")
        
        # after upload
        if response["success"]:
            logs.append("Success is True")
            data = pixeldrain.info(response["id"])
        else:
            logs.append("Success is False")
            value = response["value"]
            error = response["message"]
            await message.edit_text(
                text=f"**Error {value}:-** `{error}`",
                disable_web_page_preview=True
            )
            return
    except Exception as error:
        await message.edit_text(
            text=f"Error :- `{error}`"+"\n\n"+'\n'.join(logs),
            disable_web_page_preview=True
        )
        return
    
    # pixeldrain data
    text = f"**File Name:** `{data['name']}`" + "\n"
    text += f"**Download Page:** `https://pixeldrain.com/u/{data['id']}`" + "\n"
    text += f"**Direct Download Link:** `https://pixeldrain.com/api/file/{data['id']}`" + "\n"
    text += f"**Upload Date:** `{data['date_upload']}`" + "\n"
    text += f"**Last View Date:** `{data['date_last_view']}`" + "\n"
    text += f"**Size:** `{data['size']}`" + "\n"
    text += f"**Total Views:** `{data['views']}`" + "\n"
    text += f"**Bandwidth Used:** `{data['bandwidth_used']}`" + "\n"
    text += f"**Mime Type:** `{data['mime_type']}`"
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Open Link",
                    url=f"https://pixeldrain.com/u/{data['id']}"
                ),
                InlineKeyboardButton(
                    text="Share Link",
                    url=f"https://telegram.me/share/url?url=https://pixeldrain.com/u/{data['id']}"
                )
            ],
            [
                InlineKeyboardButton(text="Join Updates Channel", url="https://telegram.me/kingsb007")
            ]
        ]
    )
    
    await message.edit_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


Bot.run()
