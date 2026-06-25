import asyncio
import random
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import VIDEO_CHANNEL, BRAZZER_CHANNEL, NO_IMG, POST_CHANNEL, POST_SHORTLINK, SEND_POST, ADMINS
from database.users_db import db
from utils import temp, get_shortlink, generate_weird_name, generate_thumbnail

# Global flag to control auto posting loop
AUTO_POST_RUNNING = False

# Kuch sample banner images ke URLs jo aap randomized dikhana chahte hain (Agar video thumb na mile)
RANDOM_THUMBNAILS = [
    "https://i.ibb.co/mFz1FFwr/photo-2026-06-25-15-46-41-7655360050671648772.jpg", 
    "https://i.ibb.co/RpYsNR4m/photo-2026-06-25-15-44-44-7655360059261583380.jpg"
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
# 🤖 AUTOMATED BACKGROUND POSTING TASK
# =================================================
async def auto_post_loop(client: Client):
    global AUTO_POST_RUNNING
    print("✨ Auto Posting Loop Task Initialized...")
    
    while AUTO_POST_RUNNING:
        try:
            # 1. Database se random video fetch karo
            video_id = await db.get_random_video()
            
            if video_id:
                if not temp.U_NAME:
                    me = await client.get_me()
                    temp.U_NAME = me.username
                
                # Link format matching your start handler (avx- uniquely identifying it)
                # If your get_random_video returns file_id, pass that, or modify accordingly.
                link = f"https://t.me/{temp.U_NAME}?start={video_id}"
                
                if POST_SHORTLINK:
                    try: shortlink = await get_shortlink(link)
                    except: shortlink = link
                else:
                    shortlink = link
                
                # 2. Perfect style caption
                caption = (
                    "🔥 <b>𝜝𝜸𝜸𝜾 𝜨𝜺𝝯 𝜠𝝴𝝭𝝾𝞄𝞇𝝸𝝯𝝴 𝜢𝝥𝝳𝝰𝞃𝝴</b> 🔥\n\n"
                    "📂 <b>Category:</b> FOREIGN\n"
                    "⚡ <b>Status:</b> Unlimited (No Limit)\n"
                    "🖼️ <b>Thumbnail:</b> Randomized\n\n"
                    "👇 <i>Niche button par click karke abhi dekhein!</i>"
                )
                
                btn = InlineKeyboardMarkup([[InlineKeyboardButton("🚀 WATCH NOW", url=shortlink)]])
                
                # Random thumbnail url pick karo banner ke liye
                photo_banner = random.choice(RANDOM_THUMBNAILS) if RANDOM_THUMBNAILS else NO_IMG
                
                # 3. Channel me post send karo
                await client.send_photo(
                    chat_id=POST_CHANNEL,
                    photo=photo_banner,
                    caption=caption,
                    reply_markup=btn
                )
                print("📢 [Auto-Post] Successfully posted a random video to channel.")
            
            # ⏱️ Har 30 minute (1800 seconds) me post karega. Aap ise kam-zyada kar sakte hain.
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
