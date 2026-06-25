import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import VIDEO_CHANNEL, BRAZZER_CHANNEL, NO_IMG, POST_CHANNEL, POST_SHORTLINK, SEND_POST, ADMINS
from database.users_db import db
from utils import temp, get_shortlink, generate_weird_name, generate_thumbnail

# Global flag to control auto posting loop
AUTO_POST_RUNNING = False

# Fresh working telegraph banner image link
RANDOM_THUMBNAILS = [
    "https://i.ibb.co/mFz1FFwr/photo-2026-06-25-15-46-41-7655360050671648772.jpg"
]

# -----------------------
# BRAZZERS INDEX
# -----------------------
@Client.on_message(filters.video & filters.chat(BRAZZER_CHANNEL))
async def index_brazzers_videos(_, m: Message):
    file_id = m.video.file_id
    file_unique_id = m.video.file_unique_id
    await db.add_brazzers_video(file_unique_id, file_id)

# -----------------------
# NORMAL VIDEO INDEX
# -----------------------
@Client.on_message(filters.video & filters.chat(VIDEO_CHANNEL))
async def index_normal_videos(client, m: Message):
    try:
        file_id = m.video.file_id
        file_unique_id = m.video.file_unique_id

        file_name = generate_weird_name() + ".mp4"
        status = await db.add_video(file_unique_id, file_id)

        if status:
            print(f"✅ New Video Added: {file_name} (Msg ID: {m.id})")
        else:
            print(f"♻️ Duplicate Found: {file_name}")

        if not SEND_POST:
            return

        if not temp.U_NAME:
            me = await client.get_me()
            temp.U_NAME = me.username

        link = f"https://t.me/{temp.U_NAME}?start=avx-{file_unique_id}"

        if POST_SHORTLINK:
            try: shortlink = await get_shortlink(link)
            except: shortlink = link
        else:
            shortlink = link

        caption = f"<b>{file_name}</b>\n\n<i>Click the button below to watch the video.</i>"
        btn = InlineKeyboardMarkup([[InlineKeyboardButton("📂 ɢᴇᴛ ᴠɪᴅᴇᴏ 📂", url=shortlink)]])

        thumb_to_send = NO_IMG
        try:
            if m.video.thumbs:
                thumb_file = await client.download_media(m.video.thumbs[0].file_id)
                if thumb_file: thumb_to_send = thumb_file
            else:
                video_path = await m.download()
                gen_thumb = await generate_thumbnail(video_path)
                if gen_thumb: thumb_to_send = gen_thumb
        except Exception as e:
            print("Thumbnail handling error:", e)

        try:
            await client.send_photo(chat_id=POST_CHANNEL, photo=thumb_to_send, caption=caption, reply_markup=btn)
        except Exception as e:
            await client.send_photo(chat_id=POST_CHANNEL, photo=NO_IMG, caption=caption, reply_markup=btn)

    except Exception as e:
        print(f"❌ Error in Auto Index: {e}")

# =================================================
# 🤖 AUTOMATED BACKGROUND POSTING TASK (FIXED)
# =================================================
async def auto_post_loop(client: Client):
    global AUTO_POST_RUNNING
    print("✨ Auto Posting Loop Task Initialized...")
    
    while AUTO_POST_RUNNING:
        try:
            # 🔧 FIX: Database se file_unique_id nikalne ke liye hum direct pipeline use karenge
            # Taaki hamara send_requested_file function ise aaram se dhoondh sake
            try:
                pipeline = [{"$sample": {"size": 1}}]
                cursor = db.videos.aggregate(pipeline)
                result = await cursor.to_list(length=1)
                video_unique_id = result[0]["file_unique_id"] if result else None
            except Exception as db_err:
                print(f"Database fetch error: {db_err}")
                video_unique_id = None
            
            if video_unique_id:
                if not temp.U_NAME:
                    me = await client.get_me()
                    temp.U_NAME = me.username
                
                # Perfect short link format compatible with Telegram limits
                link = f"https://t.me/{temp.U_NAME}?start=avx-{video_unique_id}"
                
                if POST_SHORTLINK:
                    try: shortlink = await get_shortlink(link)
                    except: shortlink = link
                else:
                    shortlink = link
                
                caption = (
                    "🔥 <b>𝜝𝜸𝜸𝜾 𝜨𝜺𝝯 𝜠𝝴𝝭𝝾𝞄𝞇𝝸𝝯𝝴 𝜢𝝥𝝳𝝰𝞃𝝴</b> 🔥\n\n"
                    "📂 <b>Category:</b> FOREIGN\n"
                    "⚡ <b>Status:</b> Unlimited (No Limit)\n"
                    "🖼️ <b>Thumbnail:</b> Randomized\n\n"
                    "👇 <i>Niche button par click karke abhi dekhein!</i>"
                )
                
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 WATCH NOW", url=shortlink)]])
                photo_banner = random.choice(RANDOM_THUMBNAILS) if RANDOM_THUMBNAILS else NO_IMG
                
                try:
                    await client.send_photo(
                        chat_id=POST_CHANNEL,
                        photo=photo_banner,
                        caption=caption,
                        reply_markup=btn
                    )
                    print("📢 [Auto-Post] Successfully posted with thumbnail.")
                except Exception as img_err:
                    print(f"⚠️ [Image Failed]: {img_err} | Sending as text now...")
                    await client.send_message(
                        chat_id=POST_CHANNEL,
                        text=caption,
                        reply_markup=btn
                    )
            
            # ⏱️ Har 15 minute (900 seconds) me post karega.
            await asyncio.sleep(600)
            
        except Exception as e:
            print(f"⚠️ [Auto-Post Error]: {e}")
            await asyncio.sleep(60)

# =================================================
# 👑 OWNER ONLY COMMANDS TO CONTROL AUTO POST
# =================================================
@Client.on_message(filters.command("autopost_on") & filters.private & filters.user(ADMINS))
async def turn_on_autopost(client, message: Message):
    global AUTO_POST_RUNNING
    if AUTO_POST_RUNNING:
        return await message.reply("🤖 Auto Posting pehle se hi ON hai!")
    
    AUTO_POST_RUNNING = True
    asyncio.create_task(auto_post_loop(client))
    await message.reply("✅ <b>Auto Posting System ON ho gaya hai!</b> Bot ab automatically channel me posts dalta rahega.")

@Client.on_message(filters.command("autopost_off") & filters.private & filters.user(ADMINS))
async def turn_off_autopost(_, message: Message):
    global AUTO_POST_RUNNING
    if not AUTO_POST_RUNNING:
        return await message.reply("🤖 Auto Posting pehle se hi OFF hai!")
    
    AUTO_POST_RUNNING = False
    await message.reply("🛑 <b>Auto Posting System OFF kar diya gaya hai!</b>")
