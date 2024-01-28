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
        text=f"Hello {update.from_user.mention}, Please send a media file or a URL to upload into pixeldrain.\n\nMade with love by DcOoL",
        disable_web_page_preview=True,
        quote=True
    )

@Bot.on_message(filters.private & (filters.media | filters.text))
async def media_filter(bot, update):
    logs = []
    message = await update.reply_text(
        text="`Processing...`",
        quote=True,
        disable_web_page_preview=True
    )
    
    try:
        # check if the message is a media file or a URL
        if update.media:
            media = await update.download()
        elif update.text:
            url = update.text
            parsed_url = urlparse(url)
            if not parsed_url.scheme or parsed_url.scheme not in ["http", "https"]:
                await message.edit_text(
                    text="Invalid URL format.",
                    disable_web_page_preview=True
                )
                return
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                await message.edit_text(
                    text=f"Error {response.status_code}:- `{response.reason}`",
                    disable_web_page_preview=True
                )
                return
            media = response.content
            filename = parsed_url.path.split("/")[-1]
            if not filename:
                await message.edit_text(
                    text="Invalid URL format.",
                    disable_web_page_preview=True
                )
                return
            with open(filename, "wb") as f:
                try:
                    f.write(media)
                    logs.append("Download Successfully")
                except TypeError as e:
                    if "embedded null byte" in str(e):
                        logs.append("Download Successfully (with null bytes)")
                    else:
                        raise e
        else:
            await message.edit_text(
                text="Invalid input format.",
                disable_web_page_preview=True
            )
            return
        
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
                InlineKeyboardButton(text="Join Updates Channel", url="https://telegram.me/kimgsb007")
            ]
        ]
    )
    
    await message.edit_text(
        text=text,
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


Bot.run()
