import datetime
import asyncio
import random
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid, MediaEmpty
from Script import script
from database.users_db import db
# 🛠️ INFO se PHOTO_CHANNEL ko import kar liya gaya hai
from info import LOG_CHANNEL, PREMIUM_LOGS, FSUB, QR_CODE_IMAGE, DAILY_LIMIT, PREMIUM_DAILY_LIMIT, UPI_ID, PHOTO_CHANNEL
from utils import temp, is_user_joined
from plugins.verification import verify_user_on_start
from plugins.send_file import send_requested_file
from plugins.refer import refer_on_start

# =================================================
# 🖼️ MULTIPLE START IMAGES LIST
# =================================================
START_PICS_LIST = [
    "https://i.ibb.co/vv3vZ5Xg/photo-2026-06-26-12-05-20-7655674163104841744.jpg",
    "https://i.ibb.co/6cKdRWbV/photo-2026-06-26-12-05-24-7655674201759547408.jpg",
    "https://i.ibb.co/84bJ6P79/photo-2026-06-26-12-05-26-7655674223234383888.jpg",
    "https://i.ibb.co/0w6w5BW/photo-2026-06-26-12-05-29-7655674261889089552.jpg",
    "https://i.ibb.co/zHXf41Zs/photo-2026-06-26-12-05-30-7655674304838762512.jpg",
    "https://i.ibb.co/HfDpcqqk/photo-2026-06-26-12-05-33-7655674326313598980.jpg"
]

# =================================================
# 🚀 START COMMAND (ZERO-ERROR SYSTEM)
# =================================================
@Client.on_message(filters.command("start") & filters.private)
async def start_command(client, message: Message):
    user_id = message.from_user.id
    mention = message.from_user.mention
    me2 = (await client.get_me()).mention
    
    if FSUB and not await is_user_joined(client, message):
        return
        
    argument = message.command[1] if len(message.command) > 1 else None

    if argument and argument.startswith('avbotz'):
        await verify_user_on_start(client, message)
        return

    if argument == "terms":
        await send_legal_text(client, message, script.TERMS_TXT)
        return
    elif argument == "disclaimer":
        await send_legal_text(client, message, script.DISCLAIMER_TXT)
        return
    elif argument == "help":
        await send_legal_text(client, message, script.HELP_TXT)
        return
    elif argument == "about":
        await send_about_text(client, message)
        return

    if argument and argument.startswith("reff_"):
        try:
            await refer_on_start(client, message)
            return 
        except Exception as e:
            print(f"Referral Error: {e}")

    # --------------------------------------------------------
    # 🔥 AUTO-BACKUP DEEP LINKING RESOLVER
    # --------------------------------------------------------
    if argument:
        search_id = argument.replace("avx-", "")
        
        for attempt in range(5):
            try:
                await send_requested_file(client, message, user_id, search_id)
                return 
                
            except (MediaEmpty, Exception) as e:
                if "MEDIA_EMPTY" in str(e) or isinstance(e, MediaEmpty):
                    print(f"⚠️ Broken File ID auto-bypassed: {search_id}")
                    
                    try:
                        pipeline = [{"$sample": {"size": 1}}]
                        cursor = db.videos.aggregate(pipeline)
                        result = await cursor.to_list(length=1)
                        if result:
                            search_id = result[0]["file_unique_id"]
                            continue 
                    except Exception as db_err:
                        print(f"Backup fetch error: {db_err}")
                        break
                else:
                    print(f"Other Error: {e}")
                    break
                    
        return await message.reply("🍿 <b>Server busy!</b> Kripya channel se kisi doosri video par click karein.")

    # --- New User Registration ---
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)
        try:
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT.format(me2, user_id, mention))
        except Exception:
            pass

    # ⌨️ KEYBOARD BLOCK KO IF SE BAHAR NIKAL DIYA (TAAKI SABKO DIKHE)
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton("Get Video"), KeyboardButton("Get Photo")], # <- Naya button set ho gaya!
            [KeyboardButton("Brazzers")],
            [KeyboardButton("My plan"), KeyboardButton("Subscription")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

    # 🔥 RANDOM IMAGE SELECTOR
    random_pic = random.choice(START_PICS_LIST)

    await message.reply_photo(
        photo=random_pic,
        caption=script.START_TXT.format(mention, temp.U_NAME, temp.U_NAME),
        reply_markup=reply_keyboard,
        has_spoiler=True
    )

# =================================================
# 🖼️ GET PHOTO BUTTON HANDLER (DYNAMIC CHANNEL FETCH)
# =================================================
@Client.on_message(filters.text & filters.private)
async def send_photo_from_channel(client, message: Message):
    if message.text == "Get Photo":
        if not PHOTO_CHANNEL:
            return await message.reply("⚠️ <b>Photo Channel configuration missing hai! info.py check karein.</b>")
            
        processing_msg = await message.reply("🔄 <b>Aapke liye badiya photo dhoondh raha hoon...</b>")
        
        try:
            all_photos = []
            # Channel se latest 100 messages me se photos filter karega
            async for msg in client.get_chat_history(PHOTO_CHANNEL, limit=100):
                if msg.photo:
                    all_photos.append(msg.photo.file_id)
            
            if not all_photos:
                return await processing_msg.edit("❌ <b>Photo wale channel me koi photo nahi mili!</b>")
                
            # Random photo select hogi
            random_photo_id = random.choice(all_photos)
            
            await message.reply_photo(
                photo=random_photo_id,
                caption="<b>Here is your requested photo! ✨\n\nJoin our backup channels for more content!</b>"
            )
            await processing_msg.delete()
            
        except Exception as e:
            print(f"Error in Get Photo: {e}")
            await processing_msg.edit(f"⚠️ <b>Photo nahi bhej paya.</b> Check karein ki bot channel me Admin hai ya nahi.")

# =================================================
# 📜 HELPER HANDLERS
# =================================================

@Client.on_message(filters.command("disclaimer") & filters.private)
async def legal_disclaimer(client, message: Message):
    await send_legal_text(client, message, script.DISCLAIMER_TXT)

@Client.on_message(filters.command("terms") & filters.private)
async def legal_terms(client, message: Message):
    await send_legal_text(client, message, script.TERMS_TXT)

@Client.on_message(filters.command("about") & filters.private)
async def legal_about(client, message: Message):
    await send_about_text(client, message)

@Client.on_message(filters.command("help") & filters.private)
async def legal_hepl(client, message: Message):
    await send_legal_text(client, message, script.HELP_TXT)
    
async def send_legal_text(client, message, text):
    inline_buttons = [[
        InlineKeyboardButton('• ᴄʟᴏsᴇ •', callback_data='close_data')
    ]]
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_buttons),
        disable_web_page_preview=True
    )

async def send_about_text(client, message):
    inline_buttons = [[
        InlineKeyboardButton('• ᴄʟᴏsᴇ •', callback_data='close_data')
    ]]
    await message.reply_text(
        text=script.ABOUT_TXT.format(temp.B_NAME, temp.B_LINK),
        reply_markup=InlineKeyboardMarkup(inline_buttons),
        disable_web_page_preview=True
    )

# =========================================================
# 🔙 CALLBACK QUERY HANDLER
# =========================================================
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data

    if data == "close_data":
        await query.message.delete()

    elif data == "get":
        buttons = [
            [InlineKeyboardButton('• 𝖢𝗅𝗈𝗌𝖾 •', callback_data='close_data')]
        ]
        await query.message.reply_photo(
            photo=QR_CODE_IMAGE,
            caption=script.SEENBUY_TXT.format(DAILY_LIMIT, PREMIUM_DAILY_LIMIT, UPI_ID),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
